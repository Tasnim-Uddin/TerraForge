import tracemalloc

import pygame as pygame
import sys
import time
from global_constants import *
from current_events import EventManager
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

        tracemalloc.start()

    def run(self):
        while self.running:

            self.dt = time.perf_counter() - self.last_time
            self.dt *= 1000
            self.last_time = time.perf_counter()
            if self.dt > 1:
                self.dt = 1

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.QUIT or EventManager.quit_game():
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.scene.render()
            print(tracemalloc.get_traced_memory())
            self.screen.blit(self.font.render(f"FPS: {self.clock.get_fps():.1f}", True, 'white'), (10, 10))
            pygame.display.update()
            self.clock.tick(FRAMES_PER_SECOND)  # runs at the FPS put in


if __name__ == "__main__":
    Game().run()

