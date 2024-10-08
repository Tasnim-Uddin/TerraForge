import pygame

from global_constants import *
from event_manager import EventManager
from entity import Entity


class Player(Entity):
    def __init__(self):
        idle_image = pygame.transform.scale(
            surface=pygame.image.load(
                file="assets/textures/player.png"
            ).convert_alpha(),
            size=(BLOCK_SIZE, 2 * BLOCK_SIZE),
        )
        right_image = pygame.transform.scale(
            surface=pygame.image.load(
                file="assets/textures/right_player.png"
            ).convert_alpha(),
            size=(BLOCK_SIZE, 2 * BLOCK_SIZE),
        )
        left_image = pygame.transform.scale(
            surface=pygame.image.load(
                file="assets/textures/left_player.png"
            ).convert_alpha(),
            size=(BLOCK_SIZE, 2 * BLOCK_SIZE),
        )
        super().__init__(
            idle_image=idle_image, left_image=left_image, right_image=right_image
        )

        self.__attack_cooldown = 0

    def __get_input(self):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self._directions["right"] = True
                if event.key == pygame.K_a:
                    self._directions["left"] = True
                if event.key == pygame.K_SPACE:
                    self._directions["up"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self._directions["right"] = False
                if event.key == pygame.K_a:
                    self._directions["left"] = False
                if event.key == pygame.K_SPACE:
                    self._directions["up"] = False

    def __set_velocity(self):
        if self._directions["right"]:
            self._velocity[0] = PLAYER_HORIZONTAL_SPEED
        if self._directions["left"]:
            self._velocity[0] = -PLAYER_HORIZONTAL_SPEED
        self.__jump()

        if not self._directions["right"] and not self._directions["left"]:
            self._directions["idle"] = True
            self._velocity[0] = 0

    def __jump(self):
        if self._directions["up"] and self._on_ground:
            self._on_ground = False
            self._velocity[1] = -PLAYER_JUMP_HEIGHT

    def _movement(self, surrounding_chunks):
        super()._movement(surrounding_chunks=surrounding_chunks)
        self.__get_input()
        self.__set_velocity()

    def draw_health_bar(self, screen, camera_offset):
        # Display health
        health_bar_width = 300
        health_bar_height = 50

        # Draw the background health bar (green) at the very top right of the screen
        health_bar_rect = pygame.Rect(
            WINDOW_WIDTH - health_bar_width, 0, health_bar_width, health_bar_height
        )

        # Calculate the width of the lost health bar (red) based on the current health of the player
        lost_health_width = ((100 - self._health) / 100) * health_bar_width
        lost_health_rect = pygame.Rect(
            WINDOW_WIDTH - health_bar_width + (health_bar_width - lost_health_width),
            0,
            lost_health_width,
            health_bar_height,
        )

        if 0 <= self._health <= MAX_HEALTH:
            pygame.draw.rect(surface=screen, color="green", rect=health_bar_rect)
            pygame.draw.rect(surface=screen, color="red", rect=lost_health_rect)
        else:
            lost_health_rect = pygame.Rect(
                WINDOW_WIDTH - health_bar_width, 0, health_bar_width, health_bar_height
            )

            pygame.draw.rect(surface=screen, color="red", rect=lost_health_rect)

    def attack(self, enemy, camera_offset):
        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Iterate over enemies to check for attack range
                    distance_to_enemy = (
                        (enemy.get_rect().centery - self._rect.centery) ** 2
                        + (enemy.get_rect().centerx - self._rect.centerx) ** 2
                    ) ** 0.5
                    mouse_position = pygame.mouse.get_pos()
                    mouse_distance_to_enemy = (
                        (
                            enemy.get_rect().centery
                            - (mouse_position[1] + camera_offset[1])
                        )
                        ** 2
                        + (
                            enemy.get_rect().centerx
                            - (mouse_position[0] + camera_offset[0])
                        )
                        ** 2
                    ) ** 0.5
                    if (
                        0 <= distance_to_enemy <= 5 * BLOCK_SIZE
                        and 0 <= mouse_distance_to_enemy <= 5 * BLOCK_SIZE
                    ):
                        # Check if attack cooldown has expired
                        if self.__attack_cooldown <= 0:
                            enemy.set_health(health=enemy.get_health() - 30)
                            # Reset the cooldown
                            self.__attack_cooldown = PLAYER_ATTACK_INTERVAL
                        else:
                            # Reduce the cooldown timer
                            self.__attack_cooldown -= 0.05

    @staticmethod
    def death_screen(screen):
        font = pygame.font.Font(filename=None, size=100)
        text_surface = font.render(text="wasted", antialias=True, color="red")
        text_rect = text_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )
        death_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        alpha = 0

        # Gradually increase the alpha value to create a smooth transition
        while alpha <= 50:
            death_surface.set_alpha(alpha)
            screen.fblits([(death_surface, (0, 0))])
            pygame.display.update()
            pygame.time.delay(20)
            alpha += 1

        pygame.time.delay(500)

        screen.fblits([(text_surface, text_rect)])
        pygame.display.update()

        pygame.time.delay(2000)
