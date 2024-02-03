import pygame as pygame
import sys
import time

from global_constants import *
from event_manager import EventManager
from scene import Scene


class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.last_time = time.perf_counter()
        self.dt = 0

        self.running = True

        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.scene = Scene(game=self)

        self.font = pygame.font.Font(None, 32)

    def run(self):
        while self.running:

            dt = self.clock.tick(FRAMES_PER_SECOND) / 1000  # ms to s

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.QUIT or EventManager.quit_game():
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.scene.render(dt=dt)
            self.screen.blit(
                self.font.render(f"FPS: {self.clock.get_fps():.1f}", True, "white"),
                (10, 10),
            )
            pygame.display.update()


if __name__ == "__main__":
    Game().run()