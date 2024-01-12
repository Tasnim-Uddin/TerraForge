import pygame as pg


class CurrentEvents:
    """
    this is so that I won't have to always pass the events between classes and methods,
    it's better to have a separate class to hold all the events
    """

    def __init__(self):
        CurrentEvents.events = pg.event.get()

    @staticmethod
    def queue_events():
        CurrentEvents.events = pg.event.get()
