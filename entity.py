import pygame

from global_constants import *


class Entity:
    def __init__(self, image):
        self.image = image

        self.x = 0
        self.y = 0

        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.velocity = [0, 0]

        self.directions = {
            "left": False,
            "right": False,
            "up": False
        }
        self.on_ground = False

    def horizontal_collision(self, chunks, block_textures):
        if self.x <= 0:
            self.x = 0

        for chunk in chunks:
            for block in chunks[chunk]:
                block_rect = block.create_rect(block=block, block_textures=block_textures)
                if block_rect.colliderect(self.rect):
                    if self.velocity[0] > 0:
                        self.x = block_rect.left - self.rect.width
                    elif self.velocity[0] < 0:
                        self.x = block_rect.right
                    self.velocity[0] = 0
                    return

    def vertical_collision(self, chunks, block_textures):
        for chunk in chunks:
            for block in chunks[chunk]:
                block_rect = block.create_rect(block=block, block_textures=block_textures)
                if block_rect.colliderect(self.rect):
                    if self.velocity[1] > 0:
                        self.y = block_rect.top - self.rect.height
                        self.on_ground = True
                    elif self.velocity[1] < 0:
                        self.y = block_rect.bottom
                    self.velocity[1] = 0
                    return

    def movement(self, chunks, block_textures, dt):
        self.velocity[1] += GRAVITY * dt

        self.y += self.velocity[1] * dt
        self.rect.y = self.y
        self.vertical_collision(chunks=chunks, block_textures=block_textures)
        self.rect.y = self.y

        self.x += self.velocity[0] * dt
        self.rect.x = self.x
        self.horizontal_collision(chunks=chunks, block_textures=block_textures)
        self.rect.x = self.x

    def update(self, chunks, block_textures, dt):
        self.movement(chunks=chunks, block_textures=block_textures, dt=dt)

    def draw(self, screen, offset):
        screen.blit(source=self.image, dest=(self.x - offset[0], self.y - offset[1]))
