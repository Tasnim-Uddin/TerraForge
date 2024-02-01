import pygame
from global_constants import *


class Block:
    def __init__(self, image, position):
        self.image = pygame.transform.scale(
            surface=image, size=(BLOCK_SIZE, BLOCK_SIZE)
        )
        self.position = position
        self.rect = self.image.get_rect(topleft=self.position)
