import pygame as pygame
import math
import sys

from global_constants import *
from event_manager import EventManager
from scene import Scene


class Game:
    def __init__(self):
        pygame.init()

        self.clock = pygame.time.Clock()

        self.running = True

        self.screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT), vsync=1)

        self.scene = Scene(screen=self.screen)

        self.font = pygame.font.Font(filename=None, size=60)

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
            self.screen.blit(self.font.render(text=f"FPS: {math.floor(self.clock.get_fps())}", antialias=True, color="white"), dest=(WINDOW_WIDTH-200, 10))
            pygame.display.update()
            self.clock.tick(FRAMES_PER_SECOND)


if __name__ == "__main__":
    Game().run()
