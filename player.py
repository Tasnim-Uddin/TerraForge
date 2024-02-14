import pygame

from global_constants import *
from event_manager import EventManager
from entity import Entity


class Player(Entity):
    def __init__(self):
        idle_image = pygame.transform.scale(surface=pygame.image.load(file="assets/player.png").convert_alpha(),
                                            size=(BLOCK_SIZE, 2 * BLOCK_SIZE))
        right_image = pygame.transform.scale(surface=pygame.image.load(file="assets/right_player.png").convert_alpha(),
                                             size=(BLOCK_SIZE, 2 * BLOCK_SIZE))
        left_image = pygame.transform.scale(surface=pygame.image.load(file="assets/left_player.png").convert_alpha(),
                                             size=(BLOCK_SIZE, 2 * BLOCK_SIZE))
        super().__init__(idle_image=idle_image, left_image=left_image, right_image=right_image)

        self.attack_cooldown = 0
        self.attack_interval = 0.000000000000000000000001

        self.health = 100

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
        self.jump()

        if not self.directions["right"] and not self.directions["left"]:
            self.directions["idle"] = True
            self.velocity[0] = 0

    def jump(self):
        # Implement jumping only when on the ground
        if self.directions["up"] and self.on_ground:  # Jumping allowed only when the player is on the ground
            self.on_ground = False
            self.velocity[1] = -PLAYER_JUMP_HEIGHT

    def movement(self, chunks, block_textures, dt):
        super().movement(chunks=chunks, block_textures=block_textures, dt=dt)
        self.get_input()
        self.set_velocity()

    def draw_health_bar(self, screen, camera_offset):
        # Display health
        health_bar_width = 300
        health_bar_height = 50
        health_bar_color = (0, 255, 0)  # Green color for health bar
        lost_health_color = (255, 0, 0)  # Red color for lost health bar

        # Draw the background health bar (green) at the very top right of the screen
        health_bar_rect = pygame.Rect(WINDOW_WIDTH - health_bar_width - 10, 0, health_bar_width, health_bar_height)

        # Calculate the width of the lost health bar (red) based on the current health of the player
        lost_health_width = ((100 - self.health) / 100) * health_bar_width
        lost_health_rect = pygame.Rect(WINDOW_WIDTH - health_bar_width + (health_bar_width - lost_health_width),
                                       0, lost_health_width, health_bar_height)

        if 0 <= self.health <= 100:
            pygame.draw.rect(screen, health_bar_color, health_bar_rect)
            pygame.draw.rect(screen, lost_health_color, lost_health_rect)
        else:
            lost_health_rect = pygame.Rect(WINDOW_WIDTH - health_bar_width,
                                           0, health_bar_width, health_bar_height)

            pygame.draw.rect(screen, lost_health_color, lost_health_rect)

    def attack(self, enemy, dt):
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Iterate over enemies to check for attack range
                    distance_to_enemy = ((enemy.rect.centery - self.rect.centery)**2 + (enemy.rect.centerx - self.rect.centerx)**2) ** 0.5
                    if 0 <= distance_to_enemy <= BLOCK_SIZE:
                        # Check if attack cooldown has expired
                        if self.attack_cooldown <= 0:
                            enemy.health -= 30
                            # Reset the cooldown
                            self.attack_cooldown = self.attack_interval
                        else:
                            # Reduce the cooldown timer
                            self.attack_cooldown -= dt * 10
