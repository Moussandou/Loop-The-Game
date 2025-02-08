# game_states.py
import pygame
from player import Player
from room import Room, RoomManager
from constants import *

class VictoryState:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 64)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state('menu')
                
    def update(self):
        pass
        
    def draw(self, screen):
        screen.fill(BLACK)
        text = self.font.render("Félicitations ! Vous vous êtes échappé !", True, WHITE)
        text2 = self.font.render("Appuyez sur Entrée pour revenir au menu", True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
        rect2 = text2.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50))
        screen.blit(text, rect)
        screen.blit(text2, rect2)

class MenuState:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 64)
        self.options = ['Jouer', 'Options', 'Quitter']
        self.selected = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.options[self.selected] == 'Jouer':
                    self.game.change_state('game')
                elif self.options[self.selected] == 'Options':
                    self.game.change_state('options')
                elif self.options[self.selected] == 'Quitter':
                    self.game.running = False
                    
    def update(self):
        pass
        
    def draw(self, screen):
        screen.fill(BLACK)
        for i, option in enumerate(self.options):
            color = RED if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50 + i * 50))
            screen.blit(text, rect)

class GameState:
    def __init__(self, game):
        self.game = game
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.room_manager = RoomManager()
        self.inverted_colors = False
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
            elif event.key == pygame.K_i and self.player.has_inversion_power:
                self.inverted_colors = not self.inverted_colors
                
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        self.room_manager.update(self.player)
        
        # Vérifier si le jeu est terminé
        if self.room_manager.game_completed:
            self.game.change_state('victory')
        
    def draw(self, screen):
        if not self.inverted_colors:
            screen.fill(BLACK)
            self.room_manager.draw(screen, False)
            self.player.draw(screen)
        else:
            screen.fill(WHITE)
            self.room_manager.draw(screen, True)
            self.player.draw_inverted(screen)

class OptionsState:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 48)
        self.music_on = True
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state('menu')
            elif event.key == pygame.K_m:
                self.music_on = not self.music_on
                if self.music_on:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
                    
    def update(self):
        pass
        
    def draw(self, screen):
        screen.fill(BLACK)
        music_text = self.font.render(f"Musique: {'ON' if self.music_on else 'OFF'} (M)", True, WHITE)
        back_text = self.font.render("ESC pour retourner", True, WHITE)
        screen.blit(music_text, (SCREEN_WIDTH//2 - music_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(back_text, (SCREEN_WIDTH//2 - back_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
