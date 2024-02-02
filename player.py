import pygame

from global_constants import *
from event_manager import EventManager


class Player:
    def __init__(self):
        raw_image = pygame.image.load(file="assets/player.png").convert_alpha()
        self.image = pygame.transform.scale(
            surface=raw_image, size=(BLOCK_SIZE, BLOCK_SIZE * 2)
        )

        self.left_click = False
        self.right_click = False

        self.position = [(WORLD_WIDTH * BLOCK_SIZE) // 2, 500]
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
        if self.rect.left <= 0:
            self.rect.left = 0
        for chunk in chunks:
            for block in chunks[chunk]:
                if block.rect.colliderect(self.rect):
                    if self.velocity[0] > 0:
                        self.rect.right = block.rect.left
                    if self.velocity[0] < 0:
                        self.rect.left = block.rect.right

    def vertical_collision(self, chunks):
        for chunk in chunks:
            for block in chunks[chunk]:
                if block.rect.colliderect(self.rect):
                    if self.velocity[1] > 0:
                        self.on_ground = True
                        self.rect.bottom = block.rect.top
                    if self.velocity[1] < 0:
                        self.velocity[1] = -self.velocity[1]

    def movement(self, chunks):
        self.input()

        if self.velocity[1] <= TERMINAL_VELOCITY:
            self.velocity[1] += GRAVITY

        self.rect.x += self.velocity[0]
        self.horizontal_collision(chunks=chunks)
        self.rect.y += self.velocity[1]
        self.vertical_collision(chunks=chunks)

        self.position = self.rect

    def update(self, chunks):
        self.movement(chunks=chunks)

    def render(self, screen, offset):
        screen.blit(
            self.image, (self.position[0] - offset[0], self.position[1] - offset[1])
        )
