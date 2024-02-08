import pygame
from global_constants import *


class Entity:
    def __init__(self, block, image, position):
        self.block = block
        self.image = pygame.transform.scale(
            surface=image, size=(BLOCK_SIZE, BLOCK_SIZE)
        )
        self.position = position
        self.rect = self.image.get_rect(topleft=self.position)
