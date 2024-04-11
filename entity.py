import pygame

from global_constants import *
from all_texture_data import all_texture_data


class Entity:
    def __init__(self, idle_image, left_image, right_image):
        self.idle_image = idle_image
        self.right_image = right_image
        self.left_image = left_image

        self._x = 0
        self._y = 0

        self._rect = pygame.Rect(self._x, self._y, self.idle_image.get_width(), self.idle_image.get_height())
        self._velocity = [0, 0]

        self._directions = {
            "left": False,
            "right": False,
            "up": False,
            "idle": False
        }
        self._on_ground = False

        self._surrounding_blocks = []
        self._surrounding_block_rects = []

        self._health = MAX_HEALTH

    def _get_surrounding_blocks(self, surrounding_chunks):
        self._surrounding_blocks = []
        for entity_block_y_offset in range(-self._rect.height // BLOCK_SIZE + 1, self._rect.height // BLOCK_SIZE + 1):
            for entity_block_x_offset in range(-self._rect.width // BLOCK_SIZE + 1, self._rect.width // BLOCK_SIZE + 1):
                self._surrounding_blocks.append((
                    int((self._x // BLOCK_SIZE) + entity_block_x_offset),
                    int((self._y // BLOCK_SIZE) + entity_block_y_offset)
                ))

        self._surrounding_block_rects = []
        for block in self._surrounding_blocks:
            if (int(block[0] // CHUNK_WIDTH), int(block[1] // CHUNK_HEIGHT)) in surrounding_chunks and block in \
                    surrounding_chunks[(int(block[0] // CHUNK_WIDTH), int(block[1] // CHUNK_HEIGHT))]:
                current_block = surrounding_chunks[(int(block[0] // CHUNK_WIDTH), int(block[1] // CHUNK_HEIGHT))][(int(block[0]), int(block[1]))]

                if current_block not in ["crafting_table", "furnace", "torch", "oak_wallpaper", "top_oak_door_open", "bottom_oak_door_open"]:
                    block_rect = pygame.Rect(block[0] * BLOCK_SIZE, block[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    self._surrounding_block_rects.append(block_rect)

    def _horizontal_collision(self, surrounding_block_rects):
        for block_rect in surrounding_block_rects:
            if self._rect.colliderect(block_rect):
                if self._velocity[0] > 0:
                    self._x = block_rect.left - self._rect.width
                elif self._velocity[0] < 0:
                    self._x = block_rect.right
                self._velocity[0] = 0
                return

    def _vertical_collision(self, surrounding_block_rects):
        for block_rect in surrounding_block_rects:
            if self._rect.colliderect(block_rect):
                if self._velocity[1] > 0:
                    self._y = block_rect.top - self._rect.height
                    self._on_ground = True
                elif self._velocity[1] < 0:
                    self._y = block_rect.bottom
                self._velocity[1] = 0
                return

    def _movement(self, surrounding_chunks, dt):
        self._velocity[1] += GRAVITY * dt

        self._y += self._velocity[1] * dt
        self._rect.y = self._y
        self._get_surrounding_blocks(surrounding_chunks=surrounding_chunks)
        self._vertical_collision(surrounding_block_rects=self._surrounding_block_rects)
        self._rect.y = self._y

        self._x += self._velocity[0] * dt
        self._rect.x = self._x
        self._get_surrounding_blocks(surrounding_chunks=surrounding_chunks)
        self._horizontal_collision(surrounding_block_rects=self._surrounding_block_rects)
        self._rect.x = self._x

    def update(self, chunks, dt):
        self._movement(surrounding_chunks=chunks, dt=dt)

    def draw(self, screen, camera_offset):
        # Shows surrounding blocks
        # for block in self.surrounding_blocks:
        #     pygame.draw.rect(surface=screen, color="white",
        #                      rect=pygame.Rect(block[0] * BLOCK_SIZE - camera_offset[0],
        #                                       block[1] * BLOCK_SIZE - camera_offset[1],
        #                                       BLOCK_SIZE, BLOCK_SIZE),
        #                      width=2)

        if self._directions["idle"]:
            screen.fblits([(self.idle_image, (self._x - camera_offset[0], self._y - camera_offset[1]))])
        if self._directions["left"]:
            screen.fblits([(self.left_image, (self._x - camera_offset[0], self._y - camera_offset[1]))])
        if self._directions["right"]:
            screen.fblits([(self.right_image, (self._x - camera_offset[0], self._y - camera_offset[1]))])

        self.draw_health_bar(screen=screen, camera_offset=camera_offset)

    def draw_health_bar(self, screen, camera_offset):
        # Display health above the entity
        health_bar_width = 30
        health_bar_height = 5

        # Draw the background health bar (green)
        health_bar_rect = pygame.Rect(self._rect.x - camera_offset[0], self._y - camera_offset[1] - 10, health_bar_width,
                                      health_bar_height)
        pygame.draw.rect(surface=screen, color="green", rect=health_bar_rect)

        # Calculate the width of the lost health bar (red)
        lost_health_width = ((100 - self._health) / 100) * health_bar_width
        lost_health_rect = pygame.Rect(self._rect.x - camera_offset[0] + (health_bar_width - lost_health_width),
                                       self._y - camera_offset[1] - 10, lost_health_width, health_bar_height)
        pygame.draw.rect(screen, (255, 0, 0), lost_health_rect)

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def set_x(self, x):
        self._x = x

    def set_y(self, y):
        self._y = y

    def get_velocity(self):
        return self._velocity

    def get_rect(self):
        return self._rect

    def get_health(self):
        return self._health

    def set_health(self, health):
        self._health = health
        if self._health > 100:
            self._health = 100
        elif self._health < 0:
            self._health = 0

