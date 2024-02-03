import pygame
from global_constants import *


class Block:
    def __init__(self, block_type, image, position):
        self.block_type = block_type
        self.image = pygame.transform.scale(
            surface=image, size=(BLOCK_SIZE, BLOCK_SIZE)
        )
        self.position = position
        self.rect = self.image.get_rect(topleft=self.position)
