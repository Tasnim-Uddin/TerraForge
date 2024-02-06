import pygame

from global_constants import *
from event_manager import EventManager


class Player:
    def __init__(self):
        raw_image = pygame.image.load(file="assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(
            surface=raw_image, size=(BLOCK_SIZE, BLOCK_SIZE * 2)
        )

        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(round(self.x), round(self.y), self.image.get_width(), self.image.get_height())
        self.velocity = [0, 0]

        self.directions = {
            'left': False,
            'right': False,
            'up': False
        }
        self.on_ground = False

    def get_input(self):
        for event in EventManager.events:  # Handle events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self.directions['right'] = True
                if event.key == pygame.K_a:
                    self.directions['left'] = True
                if event.key == pygame.K_SPACE:
                    self.directions['up'] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.directions['right'] = False
                if event.key == pygame.K_a:
                    self.directions['left'] = False
                if event.key == pygame.K_SPACE:
                    self.directions['up'] = False

    def set_velocity(self):
        if self.directions['right']:
            self.velocity[0] = HORIZONTAL_SPEED
        if self.directions['left']:
            self.velocity[0] = -HORIZONTAL_SPEED
        if self.directions['up'] and self.on_ground:  # Jumping allowed only when the player is on the ground
            self.on_ground = False
            self.velocity[1] = -JUMP_HEIGHT

        if not self.directions['right'] and not self.directions['left']:
            self.velocity[0] = 0

    def horizontal_collision(self, chunks):
        if self.rect.left <= 0:
            self.rect.left = 0
        for chunk in chunks:
            for block in chunks[chunk]:
                if block.rect.colliderect(self.rect):
                    if self.velocity[0] > 0:
                        self.x = block.rect.left - self.rect.w
                    elif self.velocity[0] < 0:
                        self.x = block.rect.right
                    self.velocity[0] = 0

    def vertical_collision(self, chunks):
        for chunk in chunks:
            for block in chunks[chunk]:
                if block.rect.colliderect(self.rect):
                    if self.velocity[1] > 0:
                        self.y = block.rect.top - self.rect.h
                        self.on_ground = True
                    elif self.velocity[1] < 0:
                        self.y = block.rect.bottom
                    self.velocity[1] = 0

    def movement(self, chunks, dt):
        self.get_input()
        self.set_velocity()

        self.velocity[1] += GRAVITY * dt

        self.y += self.velocity[1] * dt
        self.rect.y = self.y
        self.vertical_collision(chunks=chunks)
        self.rect.y = self.y

        self.x += self.velocity[0] * dt
        self.rect.x = self.x
        self.horizontal_collision(chunks=chunks)
        self.rect.x = self.x

    def update(self, chunks, dt):
        self.movement(chunks=chunks, dt=dt)

    def render(self, screen, offset):
        screen.blit(self.image, (self.x - offset[0], self.y - offset[1]))
