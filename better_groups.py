import pygame


class BetterGroup(pygame.sprite.Group):
    def draw(self, surface):
        surface.fblits([(sprite.image, sprite.rect) for sprite in self.sprites()])

