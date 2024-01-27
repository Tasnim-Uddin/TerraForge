from global_constants import *


class Camera:
    def __init__(self):
        self.scroll = [0, 0]
        self.applied_scroll = [0, 0]

    def update(self, player):
        horizontal_shift = (player.rect.x - self.scroll[0] - WINDOW_WIDTH / 2) / 1
        vertical_shift = player.rect.y - self.scroll[1] - WINDOW_HEIGHT / 2

        self.scroll[0] += horizontal_shift
        self.scroll[1] += vertical_shift

        self.applied_scroll = self.scroll.copy()
        self.applied_scroll[0] = int(self.applied_scroll[0])
        self.applied_scroll[1] = int(self.applied_scroll[1])
