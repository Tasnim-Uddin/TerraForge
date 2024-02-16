import pygame

from global_constants import *


class Entity:
    def __init__(self, idle_image, left_image, right_image):
        self.image = idle_image
        self.left_image = left_image
        self.right_image = right_image

        self.x = 0
        self.y = 0

        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        self.velocity = [0, 0]

        self.directions = {
            "left": False,
            "right": False,
            "up": False,
            "idle": False
        }
        self.on_ground = False

        self.health = DEFAULT_HEALTH

    def horizontal_collision(self, surrounding_chunks, block_textures):
        for chunk in surrounding_chunks:
            for block in surrounding_chunks[chunk]:
                block_rect = block.create_rect(block=block, block_textures=block_textures)
                if block_rect.colliderect(self.rect):
                    if self.velocity[0] > 0:
                        self.x = block_rect.left - self.rect.width
                    elif self.velocity[0] < 0:
                        self.x = block_rect.right
                    self.velocity[0] = 0
                    return

    def vertical_collision(self, surrounding_chunks, block_textures):
        for chunk in surrounding_chunks:
            for block in surrounding_chunks[chunk]:
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
        self.vertical_collision(surrounding_chunks=chunks, block_textures=block_textures)
        self.rect.y = self.y

        self.x += self.velocity[0] * dt
        self.rect.x = self.x
        self.horizontal_collision(surrounding_chunks=chunks, block_textures=block_textures)
        self.rect.x = self.x

    def update(self, chunks, block_textures, dt):
        self.movement(chunks=chunks, block_textures=block_textures, dt=dt)

    def draw(self, screen, camera_offset):
        if self.directions["idle"]:
            screen.blit(self.image, (self.x - camera_offset[0], self.y - camera_offset[1]))
        if self.directions["left"]:
            screen.blit(self.left_image, (self.x - camera_offset[0], self.y - camera_offset[1]))
        if self.directions["right"]:
            screen.blit(self.right_image, (self.x - camera_offset[0], self.y - camera_offset[1]))

        self.draw_health_bar(screen=screen, camera_offset=camera_offset)

    def draw_health_bar(self, screen, camera_offset):
        # Display health above the entity
        health_bar_width = 30
        health_bar_height = 5

        # Draw the background health bar (green)
        health_bar_rect = pygame.Rect(self.rect.x - camera_offset[0], self.y - camera_offset[1] - 10, health_bar_width,
                                      health_bar_height)
        pygame.draw.rect(surface=screen, color=(0, 255, 0), rect=health_bar_rect)

        # Calculate the width of the lost health bar (red)
        lost_health_width = ((100 - self.health) / 100) * health_bar_width
        lost_health_rect = pygame.Rect(self.rect.x - camera_offset[0] + (health_bar_width - lost_health_width),
                                       self.y - camera_offset[1] - 10, lost_health_width, health_bar_height)
        pygame.draw.rect(screen, (255, 0, 0), lost_health_rect)
