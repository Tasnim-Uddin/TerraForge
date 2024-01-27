# import pygame as pg
# from global_constants import *
#
#
# class Block:
#     def __init__(self, image=pg.Surface(size=(BLOCK_SIZE, BLOCK_SIZE)), position=(0, 0)):
#         self.image = pg.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE))
#         self.position = position
#         self.rect = self.image.get_rect(topleft=position)
#
#     def update(self, camera_shift):
#         rendered_output_position = [0, 0]
#         rendered_output_position[0] = self.rect.x - camera_shift[0]
#         rendered_output_position[1] = self.rect.y - camera_shift[1]
#         return self.image, (rendered_output_position[0], rendered_output_position[1])

import pygame
from global_constants import *


class Block:
    def __init__(self, image, position):
        self.image = pygame.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE))
        self.position = position
        self.rect = self.image.get_rect(topleft=self.position)

