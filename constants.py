import pygame

# Initialiser pygame
pygame.init()

# Obtenir la résolution de l'écran
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_HEIGHT = SCREEN_HEIGHT // 3  
PLAYER_WIDTH = int(PLAYER_HEIGHT * 0.4)  # Largeur proportionnelle à la hauteur
PLAYER_SPEED = SCREEN_WIDTH // 140  # Vitesse ajustée
PLAYER_GRAVITY = 0.8
PLAYER_JUMP_POWER = -16

# Room settings
ROOM_WIDTH = SCREEN_WIDTH
ROOM_HEIGHT = SCREEN_HEIGHT
DOOR_WIDTH = SCREEN_WIDTH // 20  # Portes plus étroites
DOOR_HEIGHT = SCREEN_HEIGHT // 4  # Portes plus hautes

# Background settings
BACKGROUND_WIDTH = SCREEN_WIDTH
BACKGROUND_HEIGHT = SCREEN_HEIGHT
