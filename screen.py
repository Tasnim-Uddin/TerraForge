import pygame as pg
from all_entity_types import EntityTypes


class Screen:
    def __init__(self, game):
        self.game = game

        self.sprites = pg.sprite.Group()
        self.entity = EntityTypes(
            image=pg.image.load("assets/player.png").convert_alpha())  # convert_alpha to remove transparent background
        self.sprites.add(self.entity)  # adding the entity to the sprite group

    def render(self):
        self.game.window.fill("lightblue")  # getting the self.window variable from object self.game (in main.py)
        self.sprites.update()
        self.sprites.draw(surface=self.game.window)
