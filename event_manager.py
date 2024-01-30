import pygame as pygame


class EventManager:
    """
    this is so that I won't have to always pass the events between classes and methods,
    it's better to have a separate class to hold all the events
    """

    def __init__(self):
        EventManager.events = pygame.event.get()

    @staticmethod
    def queue_events():
        EventManager.events = pygame.event.get()

    @staticmethod
    def quit_game():
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
