import pygame as pygame


class EventManager:
    def __init__(self):
        EventManager.events = pygame.event.get()

    @staticmethod
    def queue_events():
        EventManager.events = pygame.event.get()

    @staticmethod
    def keydown(key):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == key:
                    return True
        return False

    @staticmethod
    def scroll_wheel_up():
        for e in EventManager.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    return True
        return False

    @staticmethod
    def scroll_wheel_down():
        for e in EventManager.events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 5:
                    return True
        return False

    @staticmethod
    def mouse_button_clicked(mouse_button):
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == mouse_button:
                    return True
        return False

    @staticmethod
    def quit_game():
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
