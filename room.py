# room.py
import pygame
from constants import *

class Room:
    # Charger l'image de fond une seule fois pour toutes les salles
    try:
        background_image = pygame.image.load('assets/image/background.jpg')
    except pygame.error:
        print("Erreur: Impossible de charger l'image de fond")
        background_image = None

    def __init__(self, room_id, doors=None, items=None, switches=None, hidden_items=None, hidden_switches=None, special_decor=None):
        self.room_id = room_id
        # Mettre à l'échelle l'image de fond si elle existe
        if Room.background_image:
            self.background = pygame.transform.scale(Room.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        self.doors = doors or {
            'front': pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - DOOR_HEIGHT - 50, DOOR_WIDTH, DOOR_HEIGHT),
            'back': pygame.Rect(-DOOR_WIDTH, SCREEN_HEIGHT - DOOR_HEIGHT - 50, DOOR_WIDTH, DOOR_HEIGHT)
        }
        self.items = items or {}  # {position: item_type}
        self.hidden_items = hidden_items or {}  # Items visibles uniquement en mode inversé
        self.switches = switches or {}  # {position: is_activated}
        self.hidden_switches = hidden_switches or {}  # Interrupteurs visibles uniquement en mode inversé
        self.next_room = {'front': None, 'back': None}
        self.special_decor = special_decor  # Pour les éléments de décor spéciaux
        
    def draw(self, screen, is_inverted=False):
        # Dessiner le fond
        if hasattr(self, 'background') and not is_inverted:
            screen.blit(self.background, (0, 0))
        else:
            # Remplir avec la couleur de fond appropriée si pas de background ou en mode inversé
            screen.fill(BLACK if not is_inverted else WHITE)
            
        # Dessiner les portes
        for door in self.doors.values():
            pygame.draw.rect(screen, WHITE if not is_inverted else BLACK, door)
            
        # Dessiner le décor spécial si présent
        if self.special_decor:
            if not is_inverted:
                pygame.draw.rect(screen, GRAY, self.special_decor)
            else:
                pygame.draw.rect(screen, WHITE, self.special_decor)
            
        # Dessiner les objets visibles normalement
        if not is_inverted:
            for pos, item_type in self.items.items():
                if item_type == 'key':
                    pygame.draw.circle(screen, RED, pos, SCREEN_WIDTH//80)
                elif item_type == 'inversion_power':
                    pygame.draw.circle(screen, BLUE, pos, SCREEN_WIDTH//60)
            
            # Dessiner les interrupteurs normaux
            for pos, is_activated in self.switches.items():
                color = RED if is_activated else WHITE
                switch_size = SCREEN_WIDTH//40
                pygame.draw.rect(screen, color, (pos[0]-switch_size, pos[1]-switch_size, 
                                               switch_size*2, switch_size*2))
        else:
            # Mode inversé
            # Dessiner les objets cachés
            for pos, item_type in self.hidden_items.items():
                if item_type == 'key':
                    pygame.draw.circle(screen, BLACK, pos, SCREEN_WIDTH//80)
            
            # Dessiner les interrupteurs cachés
            for pos, is_activated in self.hidden_switches.items():
                color = BLACK if is_activated else GRAY
                switch_size = SCREEN_WIDTH//40
                pygame.draw.rect(screen, color, (pos[0]-switch_size, pos[1]-switch_size, 
                                               switch_size*2, switch_size*2))
            
            # Dessiner les objets normaux en inversé
            for pos, item_type in self.items.items():
                if item_type == 'key':
                    pygame.draw.circle(screen, BLACK, pos, SCREEN_WIDTH//80)
                elif item_type == 'inversion_power':
                    pygame.draw.circle(screen, BLACK, pos, SCREEN_WIDTH//60)
            
            # Dessiner les interrupteurs normaux en inversé
            for pos, is_activated in self.switches.items():
                color = BLACK if is_activated else GRAY
                switch_size = SCREEN_WIDTH//40
                pygame.draw.rect(screen, color, (pos[0]-switch_size, pos[1]-switch_size, 
                                               switch_size*2, switch_size*2))

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.setup_rooms()
        self.game_completed = False
        self.last_teleport_time = 0  # Temps de la dernière téléportation
        self.teleport_cooldown = 500  # Délai de 500 millisecondes entre les téléportations
        
    def setup_rooms(self):
        # Création d'un élément de décor spécial pour la salle 4
        special_decor = pygame.Rect(SCREEN_WIDTH//2 - SCREEN_WIDTH//10, 
                                  SCREEN_HEIGHT//2 - SCREEN_HEIGHT//10, 
                                  SCREEN_WIDTH//5, SCREEN_HEIGHT//5)
        
        # Positions adaptées à l'écran
        key_y = SCREEN_HEIGHT * 0.75  # Position verticale des clés
        switch_y = SCREEN_HEIGHT * 0.75  # Position verticale des interrupteurs
        power_y = SCREEN_HEIGHT * 0.7  # Position verticale du pouvoir d'inversion
        
        # Création des pièces avec leurs objets et connexions
        self.rooms = {
            0: Room(0),  # Salle vide initiale
            1: Room(1),  # Salle vide initiale
            2: Room(2),  # Salle vide initiale
            3: Room(3),  # Salle vide initiale
            4: Room(4, special_decor=special_decor),  # Salle avec décor bougé
            5: Room(5, hidden_switches={(SCREEN_WIDTH//2, switch_y): False}),  # Interrupteur caché
            6: Room(6, items={(SCREEN_WIDTH//4, key_y): 'key'}),  # Première clé visible
            7: Room(7),  # Salle vide
            8: Room(8, switches={(SCREEN_WIDTH//2, switch_y): False}),  # Premier interrupteur
            9: Room(9, items={(SCREEN_WIDTH//2, power_y): 'inversion_power'}),  # Pouvoir d'inversion
            10: Room(10, items={(3*SCREEN_WIDTH//4, key_y): 'key'}),  # Deuxième clé
            11: Room(11),  # Salle vide
            12: Room(12, switches={(SCREEN_WIDTH//3, switch_y): False}),  # Deuxième interrupteur
            13: Room(13, hidden_items={(3*SCREEN_WIDTH//4, key_y): 'key'}),  # Troisième clé cachée
        }
        
        # Établir les connexions entre les pièces dans l'ordre
        self.rooms[0].next_room = {'front': 1, 'back': 13}
        self.rooms[1].next_room = {'front': 2, 'back': 0}
        self.rooms[2].next_room = {'front': 3, 'back': 1}
        self.rooms[3].next_room = {'front': 4, 'back': 2}
        self.rooms[4].next_room = {'front': 5, 'back': 3}
        self.rooms[5].next_room = {'front': 6, 'back': 4}
        self.rooms[6].next_room = {'front': 7, 'back': 5}
        self.rooms[7].next_room = {'front': 8, 'back': 6}
        self.rooms[8].next_room = {'front': 9, 'back': 7}
        self.rooms[9].next_room = {'front': 10, 'back': 8}
        self.rooms[10].next_room = {'front': 11, 'back': 9}
        self.rooms[11].next_room = {'front': 12, 'back': 10}
        self.rooms[12].next_room = {'front': 13, 'back': 11}
        self.rooms[13].next_room = {'front': 0, 'back': 12}
        
        self.current_room = self.rooms[0]

    def check_all_switches_activated(self):
        for room in self.rooms.values():
            # Vérifier les interrupteurs normaux
            for is_activated in room.switches.values():
                if not is_activated:
                    return False
            # Vérifier les interrupteurs cachés
            for is_activated in room.hidden_switches.values():
                if not is_activated:
                    return False
        return True
        
    def update(self, player):
        current_time = pygame.time.get_ticks()
        
        # Vérifier les collisions avec les portes
        for direction, door in self.current_room.doors.items():
            # Ajustez la largeur de collision pour permettre au joueur d'atteindre les portes
            extended_door = pygame.Rect(
                door.x, 
                door.y, 
                door.width + 100,  # Augmentez la largeur de collision
                door.height
            )
            
            if player.rect.colliderect(extended_door):
                # Vérifier le temps écoulé depuis la dernière téléportation
                if current_time - self.last_teleport_time > self.teleport_cooldown:
                    if self.check_all_switches_activated():
                        self.game_completed = True
                    else:
                        next_room_id = self.current_room.next_room[direction]
                        if next_room_id is not None:
                            self.current_room = self.rooms[next_room_id]
                            if direction == 'front':
                                # Positionnez le joueur juste à côté de la porte arrière
                                player.x = self.current_room.doors['back'].right
                            else:
                                # Positionnez le joueur juste à côté de la porte avant
                                player.x = self.current_room.doors['front'].left - player.width 
                            
                            # Mettre à jour le temps de la dernière téléportation
                            self.last_teleport_time = current_time
        
        # Vérifier les collisions avec les objets visibles
        for pos, item_type in list(self.current_room.items.items()):
            item_rect = pygame.Rect(pos[0]-SCREEN_WIDTH//80, pos[1]-SCREEN_WIDTH//80, 
                                  SCREEN_WIDTH//40, SCREEN_WIDTH//40)
            if player.rect.colliderect(item_rect):
                if item_type == 'inversion_power':
                    player.has_inversion_power = True
                player.add_to_inventory(item_type)
                self.current_room.items.pop(pos)

        # Vérifier les collisions avec les objets cachés
        for pos, item_type in list(self.current_room.hidden_items.items()):
            item_rect = pygame.Rect(pos[0]-SCREEN_WIDTH//80, pos[1]-SCREEN_WIDTH//80, 
                                  SCREEN_WIDTH//40, SCREEN_WIDTH//40)
            if player.rect.colliderect(item_rect):
                player.add_to_inventory(item_type)
                self.current_room.hidden_items.pop(pos)
                
        # Vérifier les collisions avec les interrupteurs (normaux et cachés)
        for switches in [self.current_room.switches, self.current_room.hidden_switches]:
            for pos, is_activated in switches.items():
                if not is_activated:  # Seulement si l'interrupteur n'est pas déjà activé
                    switch_rect = pygame.Rect(pos[0]-SCREEN_WIDTH//40, pos[1]-SCREEN_WIDTH//40, 
                                           SCREEN_WIDTH//20, SCREEN_WIDTH//20)
                    if player.rect.colliderect(switch_rect):
                        # Vérifier si le joueur a une clé
                        if 'key' in player.inventory:
                            switches[pos] = True
                            player.inventory.remove('key')  # Utiliser une clé
                
    def draw(self, screen, is_inverted=False):
        self.current_room.draw(screen, is_inverted)
