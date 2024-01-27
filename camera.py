import pygame
from global_constants import *


class Camera:
    def __init__(self, player):
        self.player = player
        self.precise_offset = [0, 0]  # float
        self.offset = [0, 0]  # int

    def setmethod(self, method):
        self.method = method

    def scroll(self):
        self.method.scroll()


class CamScroll:
    def __init__(self, camera, player):
        self.camera = camera
        self.player = player

    def scroll(self):
        pass


class Follow(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera=camera, player=player)

    def scroll(self):
        self.camera.precise_offset[0] += (self.player.rect.x - self.camera.precise_offset[0] - (WINDOW_WIDTH / 2))
        self.camera.precise_offset[1] += (self.player.rect.y - self.camera.precise_offset[1] - (WINDOW_HEIGHT / 2))
        self.camera.offset[0] = int(self.camera.precise_offset[0])
        self.camera.offset[1] = int(self.camera.precise_offset[1])


class Border(CamScroll):
    def __init__(self, camera, player):
        CamScroll.__init__(self, camera=camera, player=player)

    def scroll(self):
        self.camera.precise_offset[0] += (self.player.rect.x - self.camera.precise_offset[0] - (WINDOW_WIDTH / 2))
        self.camera.precise_offset[1] += (self.player.rect.y - self.camera.precise_offset[1] - (WINDOW_HEIGHT / 2))
        self.camera.offset[0] = int(self.camera.precise_offset[0])
        self.camera.offset[1] = int(self.camera.precise_offset[1])
        self.camera.offset[0] = max(self.player.rect.left, self.camera.offset[0])
        self.camera.offset[0] = min(self.camera.offset[0], self.player.rect.right - WINDOW_WIDTH)
