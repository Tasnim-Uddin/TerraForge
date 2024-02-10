import pygame as pygame


class EventManager:
    def __init__(self):
        EventManager.events = pygame.event.get()

    @staticmethod
    def queue_events():
        EventManager.events = pygame.event.get()

    @staticmethod
    def specific_key_down(key):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == key:
                    return True
        return False
    @staticmethod
    def scroll_wheel_up():
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    return True
        return False

    @staticmethod
    def scroll_wheel_down():
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    return True
        return False

    @staticmethod
    def left_mouse_click():
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return True
        return False

    @staticmethod
    def right_mouse_click():
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    return True
        return False

    @staticmethod
    def mouse_any_clicked():
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
        return False

    @staticmethod
    def quit_game():
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
