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

        self.surrounding_blocks = []
        self.surrounding_block_rects = []

        self.health = DEFAULT_HEALTH

    def get_surrounding_blocks(self, surrounding_chunks):
        self.surrounding_blocks = []
        for entity_block_y_offset in range(-self.rect.height // BLOCK_SIZE + 1, self.rect.height // BLOCK_SIZE + 1):
            for entity_block_x_offset in range(-self.rect.width // BLOCK_SIZE + 1, self.rect.width // BLOCK_SIZE + 1):
                self.surrounding_blocks.append((
                    int((self.x // BLOCK_SIZE) + entity_block_x_offset),
                    int((self.y // BLOCK_SIZE) + entity_block_y_offset)
                ))

        self.surrounding_block_rects = []
        for block in self.surrounding_blocks:
            if (int(block[0] // CHUNK_WIDTH), int(block[1] // CHUNK_HEIGHT)) in surrounding_chunks and block in \
                    surrounding_chunks[(int(block[0] // CHUNK_WIDTH), int(block[1] // CHUNK_HEIGHT))]:
                block_rect = pygame.Rect(block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                self.surrounding_block_rects.append(block_rect)

    def horizontal_collision(self, surrounding_block_rects):
        for block_rect in surrounding_block_rects:
            if self.rect.colliderect(block_rect):
                if self.velocity[0] > 0:
                    self.x = block_rect.left - self.rect.width
                elif self.velocity[0] < 0:
                    self.x = block_rect.right
                self.velocity[0] = 0
                return

    def vertical_collision(self, surrounding_block_rects):
        for block_rect in surrounding_block_rects:
            if self.rect.colliderect(block_rect):
                if self.velocity[1] > 0:
                    self.y = block_rect.top - self.rect.height
                    self.on_ground = True
                elif self.velocity[1] < 0:
                    self.y = block_rect.bottom
                self.velocity[1] = 0
                return

    def movement(self, surrounding_chunks, dt):
        self.velocity[1] += GRAVITY * dt

        self.y += self.velocity[1] * dt
        self.rect.y = self.y
        self.get_surrounding_blocks(surrounding_chunks=surrounding_chunks)
        self.vertical_collision(surrounding_block_rects=self.surrounding_block_rects)
        self.rect.y = self.y

        self.x += self.velocity[0] * dt
        self.rect.x = self.x
        self.get_surrounding_blocks(surrounding_chunks=surrounding_chunks)
        self.horizontal_collision(surrounding_block_rects=self.surrounding_block_rects)
        self.rect.x = self.x

    def update(self, chunks, dt):
        self.movement(surrounding_chunks=chunks, dt=dt)

    def draw(self, screen, camera_offset):
        # for block in self.surrounding_blocks:
        #     pygame.draw.rect(surface=screen, color="white",
        #                      rect=pygame.Rect(block[0] * BLOCK_SIZE - camera_offset[0],
        #                                       block[1] * BLOCK_SIZE - camera_offset[1],
        #                                       BLOCK_SIZE, BLOCK_SIZE),
        #                      width=2)

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
