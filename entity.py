import pygame as pg
from global_constants import *


class Entity(pg.sprite.Sprite):
    def __init__(self, image=pg.Surface(size=(BLOCK_SIZE, BLOCK_SIZE)), position=(10, 10)):
        super().__init__()  # inheriting from parent class sprite
        self.image = pg.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=position)
        self.position = position

    def update(self):
        pass
