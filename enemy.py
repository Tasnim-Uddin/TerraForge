import pygame
import random

from global_constants import *
from entity import Entity


class Enemy(Entity):
    def __init__(self):
        image = pygame.transform.scale(surface=pygame.image.load(file="assets/enemy.png").convert_alpha(),
                                       size=(BLOCK_SIZE, BLOCK_SIZE))
        super().__init__(image=image)

        # Randomly spawn the enemy within the game world
        self.x = random.randint(a=0, b=1500)
        self.y = 0

        self.attack_distance = 0  # Define the distance at which the enemy starts attacking

        self.idle_timer = 0
        self.idle_direction = None
        self.on_ground = False

    def random_movement(self):
        if self.idle_timer <= 0:
            self.idle_timer = random.randint(50, 100)  # Number of frames before the enemy changes direction
            self.idle_direction = random.choice(["left", "right", None])
            if self.idle_direction is not None:
                self.directions[self.idle_direction] = True
        else:
            self.idle_timer -= 1
            if self.idle_direction == "right":
                self.velocity[0] = ENEMY_HORIZONTAL_SPEED
            elif self.idle_direction == "left":
                self.velocity[0] = -ENEMY_HORIZONTAL_SPEED
            else:
                self.velocity[0] = 0

        # Implement jumping only when on the ground
        if self.on_ground:
            if random.random() < 0.01:
                self.velocity[1] = -ENEMY_JUMP_SPEED
                self.on_ground = False

    def attack_update(self, player_rect):
        speed = ENEMY_HORIZONTAL_SPEED
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance <= self.attack_distance and distance != 0:
            self.velocity[0] = dx / distance * speed
            self.velocity[1] = dy / distance * speed
        elif distance > self.attack_distance:
            self.random_movement()

    def draw(self, screen, offset):
        super().draw(screen=screen, offset=offset)
