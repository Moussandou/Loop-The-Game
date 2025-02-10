import pygame
import cv2
import numpy as np
from constants import *

class Cinematic:
    def __init__(self, video_path, sound_path=None):
        self.video = cv2.VideoCapture(video_path)
        self.finished = False
        self.skipped = False
        self.frame_surface = None
        
        self.sound = None
        if sound_path:
            try:
                self.sound = pygame.mixer.Sound(sound_path)
                self.sound.play()
            except Exception as e:
                print(f"Erreur de chargement du son : {e}")
        
        self.width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.font = pygame.font.Font(None, 36)
        self.skip_text = self.font.render("Appuyez sur ESPACE pour passer", True, WHITE)
        self.skip_rect = self.skip_text.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.skipped = True
                self.finished = True
                if self.sound:
                    self.sound.stop()
                return
        
        ret, frame = self.video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.frame_surface = frame
        else:
            self.finished = True
            if self.sound:
                self.sound.stop()
            self.video.release()
            
    def draw(self, screen):
        if self.frame_surface:
            screen.blit(self.frame_surface, (0, 0))
            screen.blit(self.skip_text, self.skip_rect)
            
    def __del__(self):
        if self.video:
            self.video.release()

class CinematicManager:
    def __init__(self):
        self.cinematics = {
            'intro': {
                'video': 'assets/videos/intro.mp4',
                'sound': 'assets/sounds/intro.wav'
            },
            'first_key': {
                'video': 'assets/videos/first_key.mp4',
                'sound': 'assets/sounds/first_key.wav'
            },
            'power': {
                'video': 'assets/videos/power.mp4',
                'sound': 'assets/sounds/power.wav'
            },
            'ending': {
                'video': 'assets/videos/ending.mp4',
                'sound': 'assets/sounds/ending.wav'
            }
        }
        self.current_cinematic = None
        self.played_cinematics = set()
        
    def play_cinematic(self, cinematic_name):
        if cinematic_name not in self.played_cinematics and cinematic_name in self.cinematics:
            video_path = self.cinematics[cinematic_name]['video']
            sound_path = self.cinematics[cinematic_name]['sound']
            
            self.current_cinematic = Cinematic(video_path, sound_path)
            self.played_cinematics.add(cinematic_name)
            
            pygame.mixer.music.pause()
            
            return True
        return False
        
    def update(self, events):
        if self.current_cinematic:
            self.current_cinematic.update(events)
            if self.current_cinematic.finished:
                pygame.mixer.music.unpause()
                self.current_cinematic = None
                return True
        return False
        
    def draw(self, screen):
        if self.current_cinematic:
            self.current_cinematic.draw(screen)
            return True
        return False
        
    def is_playing(self):
        return self.current_cinematic is not None
