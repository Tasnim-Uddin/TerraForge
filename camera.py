import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self, camera: pygame.Vector2):
        super().__init__()
        self.camera = camera

    def draw(self, surface):
        surface.fblits(
            [(spr.image, spr.rect.topleft - self.camera) for spr in self.sprites()]
        )