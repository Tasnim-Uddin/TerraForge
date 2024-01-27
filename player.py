# import pygame as pygame
# from global_constants import *
# from current_events import EventManager
#
#
# class Player(pygame.sprite.Sprite):
#     def __init__(self, block_group, position, image=pygame.Surface(size=(BLOCK_SIZE, 2 * BLOCK_SIZE))):
#         super().__init__()
#
#         self.block_group = block_group
#         self.image = pygame.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE * 2))
#         self.rect = self.image.get_rect(topleft=position)
#         self.camera_scroll = pygame.math.Vector2()
#         self.velocity = pygame.math.Vector2()
#         self.on_ground = False
#
#     def input(self):
#         for event in EventManager.events:  # noqa
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_d:
#                     self.velocity.x = HORIZONTAL_SPEED
#                 if event.key == pygame.K_a:
#                     self.velocity.x = -HORIZONTAL_SPEED
#                 if event.key == pygame.K_SPACE:
#                     if self.on_ground:  # jumping allowed only when the player is on the ground
#                         self.on_ground = False
#                         self.velocity.y -= JUMP_HEIGHT
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_d or event.key == pygame.K_a:
#                     self.velocity.x = 0
#
#     def horizontal_collision(self):
#         collided_block = pygame.sprite.spritecollideany(sprite=self, group=self.block_group)  # noqa
#         if collided_block is not None:
#             if self.velocity.x > 0:
#                 self.rect.right = collided_block.rect.left
#             elif self.velocity.x < 0:
#                 self.rect.left = collided_block.rect.right
#
#     def vertical_collision(self):
#         collided_block = pygame.sprite.spritecollideany(sprite=self, group=self.block_group)  # noqa
#         if collided_block is not None:
#             if self.velocity.y > 0:
#                 self.velocity.y = 0
#                 self.rect.bottom = collided_block.rect.top
#                 self.on_ground = True
#             elif self.velocity.y < 0:
#                 self.velocity.y = -self.velocity.y
#
#     def movement(self):
#         self.input()
#
#         if self.velocity.y <= TERMINAL_VELOCITY:
#             self.velocity.y += 1
#
#         self.rect.x += self.velocity.x
#         self.horizontal_collision()
#
#         self.rect.y += self.velocity.y
#         self.vertical_collision()
#
#         self.get_camera_scroll()
#
#     def get_camera_scroll(self):
#         self.camera_scroll.x = self.rect.x - WINDOW_WIDTH/2 + self.rect.width/2
#         self.camera_scroll.y = self.rect.y - WINDOW_HEIGHT/2 + self.rect.height/2
#         return self.camera_scroll
#
#     def update(self):
#         self.movement()


import pygame

from global_constants import *
from current_events import EventManager


class Player:
    def __init__(self):
        raw_image = pygame.image.load(file="assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(surface=raw_image, size=(24, 24))

        self.position = [10, 0]
        self.rect = self.image.get_rect(topleft=self.position)
        self.velocity = [0, 0]

        self.on_ground = False

    def input(self):
        for event in EventManager.events:  # noqa
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.velocity[0] = HORIZONTAL_SPEED
                if event.key == pygame.K_a:
                    self.velocity[0] = -HORIZONTAL_SPEED
                if event.key == pygame.K_SPACE:
                    if self.on_ground:  # jumping allowed only when the player is on the ground
                        self.on_ground = False
                        self.velocity[1] -= JUMP_HEIGHT
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d or event.key == pygame.K_a:
                    self.velocity[0] = 0

    def apply_gravity(self):
        if self.velocity[1] <= TERMINAL_VELOCITY:
            self.velocity[1] += GRAVITY

    def horizontal_collision(self, chunks):
        for chunk in chunks:
            for block in chunk:
                if block.rect.colliderect(self.rect):
                    if self.velocity[0] > 0:
                        self.rect.right = block.rect.left
                    if self.velocity[0] < 0:
                        self.rect.left = block.rect.right
        # for block in chunks:
        #     if block.rect.colliderect(self.rect):
        #         if self.velocity[0] > 0:
        #             self.rect.right = block.rect.left
        #         if self.velocity[0] < 0:
        #             self.rect.left = block.rect.right

    def vertical_collision(self, chunks):
        for chunk in chunks:
            for block in chunk:
                if block.rect.colliderect(self.rect):
                    if self.velocity[1] > 0:
                        self.on_ground = True
                        self.rect.bottom = block.rect.top
                    if self.velocity[1] < 0:
                        self.velocity[1] = -self.velocity[1]
        # for block in chunks:
        #     if block.rect.colliderect(self.rect):
        #         if self.velocity[1] > 0:
        #             self.on_ground = True
        #             self.rect.bottom = block.rect.top
        #         if self.velocity[1] < 0:
        #             self.velocity[1] = -self.velocity[1]
    def movement(self, chunks):
        self.input()

        if self.velocity[1] <= TERMINAL_VELOCITY:
            self.velocity[1] += GRAVITY

        self.rect.x += self.velocity[0]
        self.horizontal_collision(chunks=chunks)
        self.rect.y += self.velocity[1]
        self.vertical_collision(chunks=chunks)

        self.position = self.rect

    def render(self, screen):
        screen.blit(self.image, self.position)
