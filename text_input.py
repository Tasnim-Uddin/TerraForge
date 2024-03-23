import string

import pygame
from global_constants import *
from event_manager import EventManager


class TextInput:
    def __init__(self):
        self.all_valid_characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

        self.input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)
        self.input_text = ""
        self.active = False

        self.font = pygame.font.Font(filename=None, size=32)

    def update(self, validation_type):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    entered_character = event.unicode
                    if entered_character in self.all_valid_characters:
                        if validation_type in ["Username", "Create Username", "Create Player", "Create World"]:
                            if len(self.input_text) <= 20:
                                self.input_text += entered_character
                        elif validation_type in ["Password", "Create Password"]:
                            if len(self.input_text) <= 64:
                                self.input_text += entered_character

    def draw(self, screen):
        pygame.draw.rect(surface=screen, color="#1874cd", rect=self.input_rect, width=2)
        text_surface = self.font.render(text=self.input_text, antialias=True, color="white")
        screen.fblits([(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))])

        self.input_rect.centerx = WINDOW_WIDTH / 2
        self.input_rect.w = max(text_surface.get_width() + 15, 200)
