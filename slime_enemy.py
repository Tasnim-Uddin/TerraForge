import pygame
import random

from global_constants import *
from entity import Entity


class SlimeEnemy(Entity):
    def __init__(self):
        idle_image = pygame.transform.scale(surface=pygame.image.load(file="assets/textures/slime.png").convert_alpha(),
                                            size=(BLOCK_SIZE, BLOCK_SIZE))
        right_image = pygame.transform.scale(surface=pygame.image.load(file="assets/textures/right_slime.png").convert_alpha(),
                                             size=(BLOCK_SIZE, BLOCK_SIZE))
        left_image = pygame.transform.scale(surface=pygame.image.load(file="assets/textures/left_slime.png").convert_alpha(),
                                            size=(BLOCK_SIZE, BLOCK_SIZE))
        super().__init__(idle_image=idle_image, left_image=left_image, right_image=right_image)

        self.__x = 0

        self.__attack_distance = 10 * BLOCK_SIZE  # Define the distance at which the enemy starts attacking

        self.__direction_timer = 0
        self.__random_direction = None

        self._directions = {
            "left": False,
            "right": False,
            "idle": False
        }

        self.__attack_cooldown = 0

    def __random_movement(self):
        if self.__direction_timer <= 0:
            self.__direction_timer = random.randint(100, 150)  # Number of frames before the enemy changes direction
            self.__random_direction = random.choice(list(self._directions.keys()))
            self._directions[self.__random_direction] = True
        else:
            self.__direction_timer -= 1
            if self.__random_direction == "right":
                self._velocity[0] = ENEMY_HORIZONTAL_SPEED
                self._directions["left"] = False
            elif self.__random_direction == "left":
                self._velocity[0] = -ENEMY_HORIZONTAL_SPEED
                self._directions["right"] = False
            elif self.__random_direction == "idle":
                self._velocity[0] = 0
                self._directions["right"] = False
                self._directions["left"] = False
        self.__jump()

    def __jump(self):
        if self._on_ground:
            self._on_ground = False
            self._velocity[1] = -ENEMY_JUMP_HEIGHT

    def attack_update(self, player, dt):
        speed = ENEMY_HORIZONTAL_SPEED
        dx = player.get_rect().centerx - self._rect.centerx
        dy = player.get_rect().centery - self._rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance > self.__attack_distance:  # If player is out of attack range, perform random movement
            self.__random_movement()
        elif distance <= self.__attack_distance:  # If player is within attack range
            if distance != 0:
                self._velocity[0] = dx / distance * speed
                if self._velocity[0] < 0:
                    self._directions["left"] = True
                    self._directions["right"] = False
                elif self._velocity[0] > 0:
                    self._directions["right"] = True
                    self._directions["left"] = False
            elif distance == 0:
                self._velocity[0] = 0
                self._directions["idle"] = True
                self._directions["left"] = False
                self._directions["right"] = False
            self._velocity[1] += GRAVITY * dt
            self.__jump()
            if self._rect.colliderect(player.get_rect()):
                if self.__attack_cooldown <= 0:
                    player.set_health(health=player.get_health() - 5)
                    player_damage = pygame.mixer.Sound(file="assets/sound/player_damage.mp3")
                    player_damage.set_volume(0.1)
                    player_damage.play()
                    self.__attack_cooldown = SLIME_ATTACK_INTERVAL
        self.__attack_cooldown -= dt * 0.1
