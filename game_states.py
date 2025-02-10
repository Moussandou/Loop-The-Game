##
## EPITECH PROJECT, 2025
## Loop-The-Game
## File description:
## game_states
##

import pygame
import math
from player import Player
from room import Room, RoomManager
from cinematics import CinematicManager
from constants import *

class Button:
    def __init__(self, text, font_size, y_position, width=300, height=60):
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.width = width
        self.height = height
        self.color = WHITE
        self.hover_factor = 0
        self.y_position = y_position
        self.animation_time = 0
        
    def draw(self, screen, selected=False, hover=False):
        x = SCREEN_WIDTH // 2
        y = self.y_position
        self.animation_time += 0.05
        float_offset = math.sin(self.animation_time) * 5
        if selected or hover:
            self.hover_factor = min(1.0, self.hover_factor + 0.1)
        else:
            self.hover_factor = max(0.0, self.hover_factor - 0.1)
        current_width = self.width + (50 * self.hover_factor)
        current_height = self.height + (10 * self.hover_factor)
        outer_rect = pygame.Rect(
            x - current_width//2,
            y - current_height//2 + float_offset,
            current_width,
            current_height
        )
        color = RED if selected else WHITE
        pygame.draw.rect(screen, color, outer_rect, 2, border_radius=15)
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=(x, y + float_offset))
        screen.blit(text_surface, text_rect)
        return outer_rect

class MenuState:
    try:
        title_image = pygame.image.load('assets/image/title.png')
        background_image = pygame.image.load('assets/image/menu_background.jpg')
    except pygame.error as e:
        print(f"Erreur: Impossible de charger les images: {e}")
        title_image = None
        background_image = None

    def __init__(self, game):
        self.game = game
        spacing = 100
        base_y = SCREEN_HEIGHT//2 - 50
        self.buttons = {
            'play': Button('Jouer', 64, base_y),
            'options': Button('Options', 64, base_y + spacing),
            'fullscreen': Button('Plein écran', 64, base_y + spacing * 2),
            'quit': Button('Quitter', 64, base_y + spacing * 3)
        }
        self.selected = 'play'
        self.mouse_pos = (0, 0)
        self.animation_time = 0
        if MenuState.title_image:
            title_width = 900
            title_height = 400
            self.title = pygame.transform.scale(MenuState.title_image, (title_width, title_height))
        if MenuState.background_image:
            self.background = pygame.transform.scale(MenuState.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                options = list(self.buttons.keys())
                current_index = options.index(self.selected)
                self.selected = options[(current_index - 1) % len(options)]
            elif event.key == pygame.K_DOWN:
                options = list(self.buttons.keys())
                current_index = options.index(self.selected)
                self.selected = options[(current_index + 1) % len(options)]
            elif event.key == pygame.K_RETURN:
                if self.selected == 'play':
                    self.game.change_state('game')
                elif self.selected == 'options':
                    self.game.change_state('options')
                elif self.selected == 'fullscreen':
                    self.game.toggle_fullscreen()
                elif self.selected == 'quit':
                    self.game.running = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button_name, button in self.buttons.items():
                    if button.draw(self.game.screen).collidepoint(event.pos):
                        if button_name == 'play':
                            self.game.change_state('game')
                        elif button_name == 'options':
                            self.game.change_state('options')
                        elif button_name == 'fullscreen':
                            self.game.toggle_fullscreen()
                        elif button_name == 'quit':
                            self.game.running = False
                    
    def update(self):
        self.animation_time += 0.02
        
    def draw(self, screen):
        if hasattr(self, 'background'):
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BLACK)
        if hasattr(self, 'title'):
            offset = math.sin(self.animation_time * 2) * 10
            title_x = SCREEN_WIDTH//2 - self.title.get_width()//2
            title_y = SCREEN_HEIGHT//4 - self.title.get_height()//2 + offset
            screen.blit(self.title, (title_x, title_y))
        for button_name, button in self.buttons.items():
            is_selected = button_name == self.selected
            is_hovered = button.draw(screen).collidepoint(self.mouse_pos)
            button.draw(screen, is_selected, is_hovered)

class GameState:
    def __init__(self, game):
        self.game = game
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.room_manager = RoomManager()
        self.room_manager.player = self.player
        self.inverted_colors = False
        self.font = pygame.font.Font(None, 48)
        self.cinematic_manager = CinematicManager()
        self.cinematic_manager.play_cinematic('intro')
        try:
            self.key_icon = pygame.image.load('assets/image/key.png').convert_alpha()
            self.key_icon = pygame.transform.scale(self.key_icon, (40, 40))
        except:
            print("Erreur: Impossible de charger l'icône de clé")
            self.key_icon = None

    def draw_key_counter(self, screen):
        counter_surface = pygame.Surface((120, 60), pygame.SRCALPHA)
        counter_surface.fill((0, 0, 0, 180))
        screen.blit(counter_surface, (20, 20))
        if self.key_icon:
            screen.blit(self.key_icon, (30, 30))
        key_count = self.player.inventory.count('key')
        keys_text = self.font.render(f"x {key_count}", True, WHITE)
        screen.blit(keys_text, (80, 35))
        
    def handle_event(self, event):
        if self.cinematic_manager.is_playing():
            self.cinematic_manager.update([event])
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
            elif event.key == pygame.K_i and self.player.has_inversion_power:
                self.inverted_colors = not self.inverted_colors
                
    def update(self):
        if self.cinematic_manager.is_playing():
            if self.cinematic_manager.update(pygame.event.get()):
                if 'ending' in self.cinematic_manager.played_cinematics:
                    self.game.change_state('victory')
            return
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.room_manager.update(self.player)
        current_room = self.room_manager.current_room.room_id
        if current_room == 4 and 'first_key' not in self.cinematic_manager.played_cinematics:
            self.cinematic_manager.play_cinematic('first_key')
        elif current_room == 6 and 'power' not in self.cinematic_manager.played_cinematics:
            self.cinematic_manager.play_cinematic('power')
        if self.room_manager.game_completed and 'ending' not in self.cinematic_manager.played_cinematics:
            self.cinematic_manager.play_cinematic('ending')
        
    def draw(self, screen):
        if self.cinematic_manager.is_playing():
            self.cinematic_manager.draw(screen)
            return
        if not self.inverted_colors:
            self.room_manager.draw(screen, False)
            self.player.draw(screen)
        else:
            self.room_manager.draw(screen, True)
            self.player.draw_inverted(screen)
        self.draw_key_counter(screen)

class OptionsState:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 48)
        spacing = 100
        base_y = SCREEN_HEIGHT//2 - 100
        self.buttons = {
            'music': Button('Musique: ON', 64, base_y),
            'back': Button('Retour', 64, base_y + spacing)
        }
        self.selected = 'music'
        self.mouse_pos = (0, 0)
        self.music_on = True
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.selected = 'back' if self.selected == 'music' else 'music'
            elif event.key == pygame.K_RETURN:
                if self.selected == 'music':
                    self.toggle_music()
                elif self.selected == 'back':
                    self.game.change_state('menu')
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button_name, button in self.buttons.items():
                    if button.draw(self.game.screen).collidepoint(event.pos):
                        if button_name == 'music':
                            self.toggle_music()
                        elif button_name == 'back':
                            self.game.change_state('menu')
                    
    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            pygame.mixer.music.unpause()
            self.buttons['music'].text = 'Musique: ON'
        else:
            pygame.mixer.music.pause()
            self.buttons['music'].text = 'Musique: OFF'
                    
    def update(self):
        pass
        
    def draw(self, screen):
        screen.fill(BLACK)
        title_font = pygame.font.Font(None, 100)
        title_text = title_font.render("Options", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        screen.blit(title_text, title_rect)
        for button_name, button in self.buttons.items():
            is_selected = button_name == self.selected
            is_hovered = button.draw(screen).collidepoint(self.mouse_pos)
            button.draw(screen, is_selected, is_hovered)

class VictoryState:
    def __init__(self, game):
        self.game = game
        self.buttons = {
            'menu': Button('Menu Principal', 64, SCREEN_HEIGHT//2 + 100)
        }
        self.selected = 'menu'
        self.mouse_pos = (0, 0)
        self.animation_time = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.buttons['menu'].draw(self.game.screen).collidepoint(event.pos):
                    self.game.change_state('menu')
                
    def update(self):
        self.animation_time += 0.02
        
    def draw(self, screen):
        screen.fill(BLACK)
        title_font = pygame.font.Font(None, 100)
        main_text = "Félicitations !"
        offset_y = math.sin(self.animation_time) * 20
        for i in range(len(main_text)):
            hue = (self.animation_time * 100 + i * 20) % 360
            color = pygame.Color(0)
            color.hsva = (hue, 100, 100, 100)
            char = title_font.render(main_text[i], True, color)
            x = SCREEN_WIDTH//2 - (len(main_text) * 25) + (i * 50)
            y = SCREEN_HEIGHT//3 + offset_y
            screen.blit(char, (x, y))
        subtitle_font = pygame.font.Font(None, 64)
        subtitle = subtitle_font.render("Vous vous êtes échappé !", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(subtitle, subtitle_rect)
        for button_name, button in self.buttons.items():
            is_selected = button_name == self.selected
            is_hovered = button.draw(screen).collidepoint(self.mouse_pos)
            button.draw(screen, is_selected, is_hovered)
