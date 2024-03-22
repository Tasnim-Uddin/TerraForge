# import pygame
# from global_constants import *
#
#
# class Block:
#     def __init__(self, block, position):
#         self.block = block
#         self.position = position
#
#     @staticmethod
#     def create_rect(block, block_textures):
#         block_rect = pygame.Rect(
#             block_textures[block.block].get_rect(topleft=block.position).x * BLOCK_SIZE,
#             block_textures[block.block].get_rect(topleft=block.position).y * BLOCK_SIZE,
#             block_textures[block.block].get_rect(topleft=block.position).width,
#             block_textures[block.block].get_rect(topleft=block.position).height
#         )
#         return block_rect
