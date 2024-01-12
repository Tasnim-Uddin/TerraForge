import pygame as pg
import sys
from global_constants import *
from current_events import CurrentEvents
from screen import Screen



class Game:
    def __init__(self):
        pg.init()

        self.clock = pg.time.Clock()

        self.running = True

        self.window = pg.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen = Screen(game=self)

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    sys.exit()

            pg.display.update()
            self.screen.render()
            self.clock.tick(FRAMES_PER_SECOND)  # runs at the FPS put in


if __name__ == "__main__":
    Game().run()
