# player.py
import pygame
from constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed = PLAYER_SPEED
        self.velocity_y = 0
        self.is_jumping = False
        self.gravity = 0.5
        self.jump_power = -12
        self.inventory = []  # Liste au lieu d'un set
        self.has_inversion_power = False
        
        # Variables pour l'animation
        self.facing_right = True
        self.is_moving = False
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        self.TOTAL_FRAMES = 11
        self.JUMP_FRAME = 0  # La frame à utiliser pendant le saut
        
        try:
            # Chargement et configuration des sprites de marche
            walk_sheet = pygame.image.load('assets/image/walk_animation.png').convert_alpha()
            self.walk_frames = self.load_animation(walk_sheet)
            self.walk_frames_left = [pygame.transform.flip(frame, True, False) for frame in self.walk_frames]
            
            # Frame immobile (même que la frame de saut)
            self.idle_frame = self.walk_frames[self.JUMP_FRAME]
            self.idle_frame_left = self.walk_frames_left[self.JUMP_FRAME]
            
        except pygame.error as e:
            print(f"Erreur lors du chargement des animations: {e}")
            self.create_fallback_surfaces()

    def load_animation(self, sheet):
        frames = []
        frame_width = sheet.get_width() // self.TOTAL_FRAMES
        frame_height = sheet.get_height()
        
        scale = PLAYER_HEIGHT / frame_height
        scaled_width = int(frame_width * scale)
        
        for i in range(self.TOTAL_FRAMES):
            frame_surface = pygame.Surface((frame_width + 4, frame_height), pygame.SRCALPHA)
            frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            frame_surface.blit(frame, (2, 0))
            scaled_frame = pygame.transform.scale(frame_surface, (scaled_width, PLAYER_HEIGHT))
            frames.append(scaled_frame)
            
        return frames

    def create_fallback_surfaces(self):
        self.idle_frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.idle_frame, WHITE, (0, 0, self.width, self.height))
        self.walk_frames = [self.idle_frame] * self.TOTAL_FRAMES
        self.walk_frames_left = [self.idle_frame] * self.TOTAL_FRAMES
        
    def update(self, keys):
        old_x = self.x
        
        # Mouvement horizontal
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_right = True
            self.is_moving = True
        else:
            self.is_moving = False
            
        # Gestion du saut
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.current_frame = self.JUMP_FRAME
            
        # Application de la gravité
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Limite au sol
        if self.y > SCREEN_HEIGHT - self.height - 250:
            self.y = SCREEN_HEIGHT - self.height - 250
            self.velocity_y = 0
            self.is_jumping = False
            
        # Limites de l'écran avec marge
        margin = SCREEN_WIDTH // 4
        self.x = max(-margin, min(self.x, SCREEN_WIDTH - self.width + margin))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # Mise à jour du rectangle de collision
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Mise à jour de l'animation uniquement si on marche et qu'on ne saute pas
        if not self.is_jumping:
            if self.is_moving:
                self.animation_timer += self.animation_speed
                if self.animation_timer >= 1:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % self.TOTAL_FRAMES
            else:
                self.current_frame = 0
        
    def draw(self, screen):
        frames = self.walk_frames_left if not self.facing_right else self.walk_frames
        frame_to_use = self.JUMP_FRAME if self.is_jumping else self.current_frame
        screen.blit(frames[frame_to_use], self.rect)
        
    def draw_inverted(self, screen):
        frames = self.walk_frames_left if not self.facing_right else self.walk_frames
        frame_to_use = self.JUMP_FRAME if self.is_jumping else self.current_frame
        current_frame = frames[frame_to_use]
        
        # Créer une version inversée de la frame sans le fond blanc
        inverted_frame = pygame.Surface(current_frame.get_size(), pygame.SRCALPHA)
        pixel_array = pygame.PixelArray(current_frame)
        for x in range(current_frame.get_width()):
            for y in range(current_frame.get_height()):
                if current_frame.get_at((x, y))[3] > 0:  # Si le pixel n'est pas transparent
                    inverted_frame.set_at((x, y), BLACK)
        del pixel_array
        
        screen.blit(inverted_frame, self.rect)
        
    def add_to_inventory(self, item):
        self.inventory.append(item)
        
    def has_item(self, item):
        return item in self.inventory
        
    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
