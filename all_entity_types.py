import pygame as pg
from global_constants import *


class EntityTypes(pg.sprite.Sprite):
    def __init__(self, image=pg.Surface(size=(TILE_SIZE, TILE_SIZE)), position=(10, 10)):
        super().__init__()  # inheriting from parent class sprite
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.position = position
