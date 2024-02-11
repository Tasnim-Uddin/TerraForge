import pygame

from global_constants import *
from event_manager import EventManager


class TextInput:
    def __init__(self):
        self.input_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50)
        self.input_text = ''
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.font = pygame.font.Font(filename=None, size=32)

    # def update(self):
    #     for event in EventManager.events:
    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             if self.input_rect.collidepoint(event.pos):
    #                 self.active = not self.active
    #             else:
    #                 self.active = False
    #         if event.type == pygame.KEYDOWN:
    #             if self.active:
    #                 if event.key == pygame.K_RETURN:
    #                     self.active = False
    #                 elif event.key == pygame.K_BACKSPACE:
    #                     self.input_text = self.input_text[:-1]
    #                 else:
    #                     self.input_text += event.unicode

    def update(self):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode

    def draw(self, screen):
        colour = self.color_active  # if self.active else self.color_inactive
        pygame.draw.rect(surface=screen, color=colour, rect=self.input_rect, width=2)
        text_surface = self.font.render(text=self.input_text, antialias=True, color=(255, 255, 255))
        screen.blit(source=text_surface, dest=(self.input_rect.x + 5, self.input_rect.y + 5))
