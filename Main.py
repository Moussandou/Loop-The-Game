##
## EPITECH PROJECT, 2025
## Loop-The-Game
## File description:
## Main
##

# main.py
import pygame
import sys
from game_states import MenuState, GameState, OptionsState, VictoryState
from constants import *

class Game:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.fullscreen = True
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Loop Escape")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # États du jeu
        self.states = {
            'menu': MenuState(self),
            'game': GameState(self),
            'options': OptionsState(self),
            'victory': VictoryState(self)
        }
        self.current_state = self.states['menu']
        
        # Configuration de la musique
        self.menu_music_loaded = False
        self.game_music_loaded = False
        self.load_menu_music()
        
    def load_menu_music(self):
        try:
            pygame.mixer.music.load('assets/music/menu.mp3')
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            self.menu_music_loaded = True
            self.game_music_loaded = False
        except:
            print("Erreur: Impossible de charger la musique du menu")
            
    def load_game_music(self):
        try:
            pygame.mixer.music.load('assets/music/ambient.mp3')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.menu_music_loaded = False
            self.game_music_loaded = True
        except:
            print("Erreur: Impossible de charger la musique du jeu")
            
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and self.current_state == self.states['game']:
                    self.change_state('menu')
            self.current_state.handle_event(event)
                
    def update(self):
        self.current_state.update()
        
    def draw(self):
        self.current_state.draw(self.screen)
        pygame.display.flip()
        
    def change_state(self, state_name):
        # Changer la musique selon l'état
        if state_name == 'game' and not self.game_music_loaded:
            self.load_game_music()
        elif (state_name == 'menu' or state_name == 'options') and not self.menu_music_loaded:
            self.load_menu_music()
            
        if state_name == 'game':
            self.states['game'] = GameState(self)
        self.current_state = self.states[state_name]
        
if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
