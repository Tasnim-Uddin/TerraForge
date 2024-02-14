# import pygame
#
# from global_constants import *
# from event_manager import EventManager
#
#
# class Player:
#     def __init__(self):
#         raw_image = pygame.image.load(file="assets/player.png").convert_alpha()
#         # self.image = pygame.transform.scale(
#         #     surface=raw_image, size=(BLOCK_SIZE, BLOCK_SIZE * 2)
#         # )
#         self.image = raw_image
#
#         self.x = 0
#         self.y = 0
#
#         self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
#         self.velocity = [0, 0]
#
#         self.directions = {
#             "left": False,
#             "right": False,
#             "up": False
#         }
#         self.on_ground = False
#
#     def get_input(self):
#         for event in EventManager.events:  # Handle events
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_d:
#                     self.directions["right"] = True
#                 if event.key == pygame.K_a:
#                     self.directions["left"] = True
#                 if event.key == pygame.K_SPACE:
#                     self.directions["up"] = True
#
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_d:
#                     self.directions["right"] = False
#                 if event.key == pygame.K_a:
#                     self.directions["left"] = False
#                 if event.key == pygame.K_SPACE:
#                     self.directions["up"] = False
#
#     def set_velocity(self):
#         if self.directions["right"]:
#             self.velocity[0] = PLAYER_HORIZONTAL_SPEED
#         if self.directions["left"]:
#             self.velocity[0] = -PLAYER_HORIZONTAL_SPEED
#         if self.directions["up"] and self.on_ground:  # Jumping allowed only when the player is on the ground
#             self.on_ground = False
#             self.velocity[1] = -PLAYER_JUMP_HEIGHT
#
#         if not self.directions["right"] and not self.directions["left"]:
#             self.velocity[0] = 0
#
#     def horizontal_collision(self, chunks, block_textures):
#         if self.x <= 0:
#             self.x = 0
#
#         for chunk in chunks:
#             for block in chunks[chunk]:
#                 block_rect = block.create_rect(block=block, block_textures=block_textures)
#                 if block_rect.colliderect(self.rect):
#                     if self.velocity[0] > 0:
#                         self.x = block_rect.left - self.rect.width
#                     elif self.velocity[0] < 0:
#                         self.x = block_rect.right
#                     self.velocity[0] = 0
#                     return
#
#     def vertical_collision(self, chunks, block_textures):
#         for chunk in chunks:
#             for block in chunks[chunk]:
#                 block_rect = block.create_rect(block=block, block_textures=block_textures)
#                 if block_rect.colliderect(self.rect):
#                     if self.velocity[1] > 0:
#                         self.y = block_rect.top - self.rect.height
#                         self.on_ground = True
#                     elif self.velocity[1] < 0:
#                         self.y = block_rect.bottom
#                     self.velocity[1] = 0
#                     return
#
#     def movement(self, chunks, block_textures, dt):
#         self.get_input()
#         self.set_velocity()
#
#         self.velocity[1] += GRAVITY * dt
#
#         self.y += self.velocity[1] * dt
#         self.rect.y = self.y
#         self.vertical_collision(chunks=chunks, block_textures=block_textures)
#         self.rect.y = self.y
#
#         self.x += self.velocity[0] * dt
#         self.rect.x = self.x
#         self.horizontal_collision(chunks=chunks, block_textures=block_textures)
#         self.rect.x = self.x
#
#     def update(self, chunks, block_textures, dt):
#         self.movement(chunks=chunks, block_textures=block_textures, dt=dt)
#
#     def draw(self, screen, offset):
#         screen.blit(source=self.image, dest=(self.x - offset[0], self.y - offset[1]))


import pygame

from global_constants import *
from event_manager import EventManager
from entity import Entity


class Player(Entity):
    def __init__(self):
        image = pygame.image.load(file="assets/player.png").convert_alpha()
        super().__init__(image=image)

        self.directions = {
            "left": False,
            "right": False,
            "up": False
        }
        self.on_ground = False

    def get_input(self):
        for event in EventManager.events:  # Handle events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.directions["right"] = True
                if event.key == pygame.K_a:
                    self.directions["left"] = True
                if event.key == pygame.K_SPACE:
                    self.directions["up"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.directions["right"] = False
                if event.key == pygame.K_a:
                    self.directions["left"] = False
                if event.key == pygame.K_SPACE:
                    self.directions["up"] = False

    def set_velocity(self):
        if self.directions["right"]:
            self.velocity[0] = PLAYER_HORIZONTAL_SPEED
        if self.directions["left"]:
            self.velocity[0] = -PLAYER_HORIZONTAL_SPEED
        if self.directions["up"] and self.on_ground:  # Jumping allowed only when the player is on the ground
            self.on_ground = False
            self.velocity[1] = -PLAYER_JUMP_HEIGHT

        if not self.directions["right"] and not self.directions["left"]:
            self.velocity[0] = 0

    def movement(self, chunks, block_textures, dt):
        super().movement(chunks=chunks, block_textures=block_textures, dt=dt)
        self.get_input()
        self.set_velocity()
