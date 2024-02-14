from collections import deque

import pygame
import random

from global_constants import *
from entity import Entity


class SlimeEnemy(Entity):
    def __init__(self):
        idle_image = pygame.transform.scale(surface=pygame.image.load(file="assets/slime.png").convert_alpha(),
                                            size=(BLOCK_SIZE, BLOCK_SIZE))
        right_image = pygame.transform.scale(surface=pygame.image.load(file="assets/right_slime.png").convert_alpha(),
                                             size=(BLOCK_SIZE, BLOCK_SIZE))
        left_image = pygame.transform.scale(surface=pygame.image.load(file="assets/left_slime.png").convert_alpha(),
                                            size=(BLOCK_SIZE, BLOCK_SIZE))
        super().__init__(idle_image=idle_image, left_image=left_image, right_image=right_image)

        # Randomly spawn the enemy within the game world
        self.x = random.randint(a=0, b=1500)

        self.attack_distance = 0 * BLOCK_SIZE  # Define the distance at which the enemy starts attacking

        self.direction_timer = 0
        self.random_direction = None

        self.directions = {
            "left": False,
            "right": False,
            "idle": False
        }

    def random_movement(self):
        if self.direction_timer <= 0:
            self.direction_timer = random.randint(100, 150)  # Number of frames before the enemy changes direction
            self.random_direction = random.choice(list(self.directions.keys()))
            self.directions[self.random_direction] = True
        else:
            self.direction_timer -= 1
            if self.random_direction == "right":
                self.velocity[0] = ENEMY_HORIZONTAL_SPEED
                self.directions["left"] = False
            elif self.random_direction == "left":
                self.velocity[0] = -ENEMY_HORIZONTAL_SPEED
                self.directions["right"] = False
            elif self.random_direction == "idle":
                self.directions["right"] = False
                self.directions["left"] = False
                self.velocity[0] = 0
        self.jump()

    def jump(self):
        # Implement jumping only when on the ground
        if self.on_ground:  # Jumping allowed only when the player is on the ground
            self.on_ground = False
            self.velocity[1] = -ENEMY_JUMP_HEIGHT

    def attack_update(self, player, dt):
        speed = ENEMY_HORIZONTAL_SPEED
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= self.attack_distance and distance != 0:
            self.velocity[0] = dx / distance * speed
            self.velocity[1] += GRAVITY * dt
            self.jump()
        elif distance > self.attack_distance:
            self.random_movement()
