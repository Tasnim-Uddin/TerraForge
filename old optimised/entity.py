import pygame
from global_constants import *


class Entity:
    def __init__(self, block, position):
        self.block = block
        self.position = position


class ComplexEntity(Entity):
    def __init__(self, block, position, image, rect):
        super().__init__(block, position)
        self.image = image
        self.rect = rect
