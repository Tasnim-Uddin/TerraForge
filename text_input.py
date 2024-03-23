import pygame
from global_constants import *
from event_manager import EventManager


class TextInput:
    def __init__(self):
        self.all_valid_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -_!@#$%^&*()[]{};:',.<>/\|`~+="

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
                    # # For username
                    # if validation_type in ["Username", "Player", "World"]:
                    #     if event.unicode in valid_typical_characters and len(self.input_text) < 20:
                    #         self.input_text += event.unicode
                    # # For password
                    # elif validation_type == "Password":
                    #     self.input_text += event.unicode
                    entered_character = event.unicode
                    if entered_character in self.all_valid_characters:
                        if validation_type in ["Username", "Create Username", "Create Player", "Create World"]:
                            if len(self.input_text) <= 20:
                                self.input_text += entered_character
                        elif validation_type in ["Password", "Create Password"]:
                            if len(self.input_text) <= 64:
                                self.input_text += entered_character


    # def validate_text_input(self, validation_type):
    #     if validation_type == "Create Username":
    #         create_username_text_valid = False
    #         if 5 <= len(self.input_text) <= 20:
    #             create_username_text_valid = True
    #         return create_username_text_valid
    #
    #     elif validation_type == "Create Password":
    #         create_password_lower = False
    #         create_password_upper = False
    #         create_password_number = False
    #         create_password_special = False
    #         create_password_text_valid = False
    #         if 5 <= len(self.input_text) <= 64:
    #             for character in self.input_text:
    #                 if character in "abcdefghijklmnopqrstuvwxyz":
    #                     create_password_lower = True
    #                 if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    #                     create_password_upper = True
    #                 if character in "0123456789":
    #                     create_password_number = True
    #                 if character in " -_!@#$%^&*()[]{};:',.<>/\|`~+=":
    #                     create_password_special = True
    #         if create_password_lower and create_password_upper and create_password_number and create_password_special:
    #             create_password_text_valid = True
    #         return create_password_text_valid

    def draw(self, screen):
        pygame.draw.rect(surface=screen, color="#1874cd", rect=self.input_rect, width=2)
        text_surface = self.font.render(text=self.input_text, antialias=True, color="white")
        screen.fblits([(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))])

        self.input_rect.centerx = WINDOW_WIDTH / 2
        self.input_rect.w = max(text_surface.get_width() + 15, 200)
