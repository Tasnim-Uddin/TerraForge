import pygame as pg
from global_constants import *
from entity import Entity
from player import Player
import opensimplex
from all_sprites_data import block_texture_data


class Screen:
    def __init__(self, game):
        self.game = game

        self.all_sprites = pg.sprite.Group()
        self.block_sprites = pg.sprite.Group()

        self.world = []

        self.generate_world()

        self.all_sprites.add(self.block_sprites)
        self.player = Player(block_group=self.block_sprites, position=(10, 10))

        self.all_sprites.add(self.player)

    @staticmethod
    def load_block_sprites():
        textures = {}
        atlas = pg.transform.scale(pg.image.load(file="assets/blocks_atlas.png").convert_alpha(),
                                   size=(BLOCK_SIZE * BLOCKS_IN_ATLAS_X, BLOCK_SIZE * BLOCKS_IN_ATLAS_Y))

        for block_type, information in block_texture_data.items():
            textures[block_type] = pg.Surface.subsurface(atlas,
                                                         pg.Rect(information["position"][0] * BLOCK_SIZE,
                                                                 information["position"][1] * BLOCK_SIZE,
                                                                 information["size"][0],
                                                                 information["size"][1]))
        return textures

    @staticmethod
    def lock_to_block_size(value):
        return BLOCK_SIZE * round(value / BLOCK_SIZE)

    def generate_world(self):
        block_textures = self.load_block_sprites()
        for x in range(100):
            y = 300 + int((opensimplex.noise2(x=x * 0.1, y=0) + 1) * 50)
            y = self.lock_to_block_size(value=y)
            while y < 500:
                self.block_sprites.add(Entity(image=block_textures["grass"], position=(x * BLOCK_SIZE, y)))
                y += BLOCK_SIZE

    def render(self):
        self.game.window.fill("lightblue")  # getting the self.window variable from object self.game (in main.py)
        self.all_sprites.update()
        self.all_sprites.draw(surface=self.game.window)
