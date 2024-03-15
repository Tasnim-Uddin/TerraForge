import pygame
from global_constants import *
from event_manager import EventManager


class TextInput:
    def __init__(self):
        self.input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)
        self.input_text = ""
        self.active = False

        self.font = pygame.font.Font(filename=None, size=32)

    def update(self):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif len(self.input_text) <= 20:  # TODO: add more validation (e.g. cant be blank, etc)
                    self.input_text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(surface=screen, color="#1874cd", rect=self.input_rect, width=2)
        text_surface = self.font.render(text=self.input_text, antialias=True, color=(255, 255, 255))
        screen.fblits([(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))])
