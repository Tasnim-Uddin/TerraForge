import pygame as pygame
import sys

from global_constants import *
from event_manager import EventManager
from scene import Scene


class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.running = True

        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.scene = Scene(screen=self.screen)

        self.font = pygame.font.Font(filename=None, size=30)

    def run(self):
        while self.running:

            dt = self.clock.tick(FRAMES_PER_SECOND) / 1000  # ms to s

            EventManager.queue_events()
            for event in EventManager.events:
                if event.type == pygame.QUIT or EventManager.quit_game():
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.scene.draw(dt=dt)
            # self.game.blit(self.font.render(f"FPS: {self.clock.get_fps()}", True, "white"), (1000, 10))
            pygame.display.update()
            self.clock.tick(FRAMES_PER_SECOND)


if __name__ == "__main__":
    Game().run()
