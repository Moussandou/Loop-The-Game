# room.py
import pygame
import math
from constants import *

class Room:
    # Chargement des images une seule fois pour toutes les salles
    try:
        background_image = pygame.image.load('assets/image/background.jpg')
        background_inverted = pygame.image.load('assets/image/background_inversé.jpg')
        key_sprite = pygame.image.load('assets/image/key.png')
        switch_on = pygame.image.load('assets/image/switch_on.png')
        switch_off = pygame.image.load('assets/image/switch_off.png')
        power_sprite = pygame.image.load('assets/image/power.png')
        button_e = pygame.image.load('assets/image/e.png')
    except pygame.error as e:
        print(f"Erreur: Impossible de charger les images: {e}")
        background_image = None
        background_inverted = None
        key_sprite = None
        switch_on = None
        switch_off = None
        power_sprite = None
        button_e = None

    def __init__(self, room_id, doors=None, items=None, switches=None, hidden_items=None, hidden_switches=None, special_decor=None):
        self.room_id = room_id
        if Room.background_image and Room.background_inverted:
            self.background = pygame.transform.scale(Room.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_inverted = pygame.transform.scale(Room.background_inverted, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        # Redimensionner les sprites
        if Room.key_sprite:
            self.key_sprite = pygame.transform.scale(Room.key_sprite, (40, 40))
        if Room.switch_on:
            self.switch_on = pygame.transform.scale(Room.switch_on, (60, 60))
        if Room.switch_off:
            self.switch_off = pygame.transform.scale(Room.switch_off, (60, 60))
        if Room.power_sprite:
            self.power_sprite = pygame.transform.scale(Room.power_sprite, (100, 100))
        if Room.button_e:
            self.button_e = pygame.transform.scale(Room.button_e, (30, 30))
            
        self.doors = doors or {
            'front': pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - DOOR_HEIGHT - 50, DOOR_WIDTH, DOOR_HEIGHT),
            'back': pygame.Rect(-DOOR_WIDTH, SCREEN_HEIGHT - DOOR_HEIGHT - 50, DOOR_WIDTH, DOOR_HEIGHT)
        }
        self.items = items or {}
        self.hidden_items = hidden_items or {}
        self.switches = switches or {}
        self.hidden_switches = hidden_switches or {}
        self.next_room = {'front': None, 'back': None}
        self.special_decor = special_decor
        self.animation_time = 0
        self.switch_in_range = None
        self.key_in_range = None
        
    def draw(self, screen, is_inverted=False, player_has_key=False):
        # Mise à jour de l'animation
        self.animation_time += 0.05
        float_offset = math.sin(self.animation_time) * 10

        # Dessiner le fond selon le mode
        if hasattr(self, 'background') and hasattr(self, 'background_inverted'):
            if not is_inverted:
                screen.blit(self.background, (0, 0))
            else:
                screen.blit(self.background_inverted, (0, 0))
        else:
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
            
        if not is_inverted:
            # Dessiner les objets visibles
            for pos, item_type in self.items.items():
                if item_type == 'key' and hasattr(self, 'key_sprite'):
                    screen.blit(self.key_sprite, 
                              (pos[0] - 20, pos[1] - 150 + float_offset))
                    if self.key_in_range == pos:
                        screen.blit(self.button_e, (pos[0] - 15, pos[1] - 180))
                elif item_type == 'inversion_power' and hasattr(self, 'power_sprite'):
                    screen.blit(self.power_sprite, 
                              (pos[0] - 50, pos[1] - 200 + float_offset))
            
            # Dessiner les interrupteurs normaux
            for pos, is_activated in self.switches.items():
                sprite = self.switch_on if is_activated else self.switch_off
                if sprite:
                    screen.blit(sprite, (pos[0] - 30, pos[1] - 170))
                    if self.switch_in_range == pos and player_has_key and not is_activated and hasattr(self, 'button_e'):
                        screen.blit(self.button_e, (pos[0] - 15, pos[1] - 200))
        else:
            # Mode inversé
            # Dessiner les objets cachés
            for pos, item_type in self.hidden_items.items():
                if item_type == 'key' and hasattr(self, 'key_sprite'):
                    screen.blit(self.key_sprite, 
                              (pos[0] - 20, pos[1] - 150 + float_offset))
                    if self.key_in_range == pos:
                        screen.blit(self.button_e, (pos[0] - 15, pos[1] - 180))
            
            # Dessiner les interrupteurs cachés
            for pos, is_activated in self.hidden_switches.items():
                sprite = self.switch_on if is_activated else self.switch_off
                if sprite:
                    screen.blit(sprite, (pos[0] - 30, pos[1] - 170))
                    if self.switch_in_range == pos and player_has_key and not is_activated and hasattr(self, 'button_e'):
                        screen.blit(self.button_e, (pos[0] - 15, pos[1] - 200))

class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.setup_rooms()
        self.game_completed = False
        self.last_teleport_time = 0
        self.teleport_cooldown = 500
        self.player = None
        
    def setup_rooms(self):
        special_decor = pygame.Rect(SCREEN_WIDTH//2 - SCREEN_WIDTH//10, 
                                  SCREEN_HEIGHT//2 - SCREEN_HEIGHT//10, 
                                  SCREEN_WIDTH//5, SCREEN_HEIGHT//5)
        
        # Positions ajustées
        key_y = SCREEN_HEIGHT * 0.65
        switch_y = SCREEN_HEIGHT * 0.65
        power_y = SCREEN_HEIGHT * 0.6
        
        # Création des pièces avec leurs objets et connexions
        self.rooms = {
            0: Room(0),  # Salle vide initiale
            1: Room(1),  # Salle vide initiale
            2: Room(2),  # Salle avec décor bougé, special_decor=special_decor),
            3: Room(3, hidden_switches={(SCREEN_WIDTH//2, switch_y): False}),  # Interrupteur caché
            4: Room(4, items={(SCREEN_WIDTH//4, key_y): 'key'}),  # Première clé visible
            5: Room(5, switches={(SCREEN_WIDTH//2, switch_y): False}),  # Premier interrupteur
            6: Room(6, items={(SCREEN_WIDTH//2, power_y): 'inversion_power'}),  # Pouvoir d'inversion
            7: Room(7, items={(3*SCREEN_WIDTH//4, key_y): 'key'}),  # Deuxième clé
            8: Room(8, switches={(SCREEN_WIDTH//3, switch_y): False}),  # Deuxième interrupteur
            9: Room(9, hidden_items={(3*SCREEN_WIDTH//4, key_y): 'key'}),  # Troisième clé cachée
        }
        
        # Établir les connexions entre les pièces dans l'ordre
        self.rooms[0].next_room = {'front': 1, 'back': 9}
        self.rooms[1].next_room = {'front': 2, 'back': 0}
        self.rooms[2].next_room = {'front': 3, 'back': 1}
        self.rooms[3].next_room = {'front': 4, 'back': 2}
        self.rooms[4].next_room = {'front': 5, 'back': 3}
        self.rooms[5].next_room = {'front': 6, 'back': 4}
        self.rooms[6].next_room = {'front': 7, 'back': 5}
        self.rooms[7].next_room = {'front': 8, 'back': 6}
        self.rooms[8].next_room = {'front': 9, 'back': 7}
        self.rooms[9].next_room = {'front': 0, 'back': 8}
        
        self.current_room = self.rooms[0]

    def check_all_switches_activated(self):
        for room in self.rooms.values():
            for is_activated in room.switches.values():
                if not is_activated:
                    return False
            for is_activated in room.hidden_switches.values():
                if not is_activated:
                    return False
        return True
        
    def update(self, player):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        # Réinitialiser les éléments en portée
        self.current_room.switch_in_range = None
        self.current_room.key_in_range = None
        
        # Gestion des portes, même code qu'avant
        for direction, door in self.current_room.doors.items():
            extended_door = pygame.Rect(
                door.x - 50 if direction == 'back' else door.x, 
                door.y, 
                door.width + 100,
                door.height
            )
            
            if player.rect.colliderect(extended_door):
                if current_time - self.last_teleport_time > self.teleport_cooldown:
                    if self.check_all_switches_activated():
                        self.game_completed = True
                    else:
                        next_room_id = self.current_room.next_room[direction]
                        if next_room_id is not None:
                            self.current_room = self.rooms[next_room_id]
                            if direction == 'front':
                                player.x = self.current_room.doors['back'].right
                            else:
                                player.x = self.current_room.doors['front'].left - player.width 
                            self.last_teleport_time = current_time
        
        # Vérifier les collisions avec les objets
        for obj_dict, offset_y in [(self.current_room.items, -150), (self.current_room.hidden_items, -150)]:
            for pos, item_type in list(obj_dict.items()):
                item_rect = pygame.Rect(
                    pos[0]-20, 
                    pos[1]+offset_y,
                    40 if item_type == 'key' else 100,
                    40 if item_type == 'key' else 100
                )
                if player.rect.colliderect(item_rect):
                    if item_type == 'key':
                        self.current_room.key_in_range = pos
                        if keys[pygame.K_e]:
                            player.add_to_inventory(item_type)
                            obj_dict.pop(pos)
                    elif item_type == 'inversion_power':
                        player.has_inversion_power = True
                        obj_dict.pop(pos)
    
        for switches in [self.current_room.switches, self.current_room.hidden_switches]:
            for pos, is_activated in switches.items():
                if not is_activated:
                    switch_rect = pygame.Rect(pos[0]-30, pos[1]-170, 60, 60)
                    if player.rect.colliderect(switch_rect):
                        self.current_room.switch_in_range = pos
                        if keys[pygame.K_e] and 'key' in player.inventory:
                            switches[pos] = True
                            player.inventory.remove('key')  # Une clé = un interrupteur
                
    def draw(self, screen, is_inverted=False):
        has_key = 'key' in self.player.inventory if self.player else False
        self.current_room.draw(screen, is_inverted, has_key)
