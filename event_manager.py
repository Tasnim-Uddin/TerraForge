import pygame as pygame


class EventManager:
    def __init__(self):
        self.events = pygame.event.get()

    @staticmethod
    def queue_events():
        EventManager.events = pygame.event.get()
