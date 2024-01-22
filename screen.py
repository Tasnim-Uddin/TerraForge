import pygame as pg
from global_constants import *
from all_entity_types import Entity
from player import Player
import opensimplex
from all_sprites_data import block_texture_data
from camera import CameraGroup


class Screen:
    def __init__(self, game):
        self.game = game

        # self.world_blocks = pg.sprite.Group()
        # self.chunk_blocks = pg.sprite.Group()
        #
        # self.player = Player(block_group=self.chunk_blocks, position=(10, 10))
        #
        # self.camera_scroll = self.player.get_camera_scroll()
        # self.all_sprites = CameraGroup(camera=self.camera_scroll)
        #
        # self.all_sprites.add(self.player)
        #
        # self.world_data = {}
        # self.chunks = {}
        #
        # self.find_chunks_around_player()
        # self.all_sprites.add(self.chunk_blocks)

        self.all_sprites = pg.sprite.Group()
        self.world_blocks = pg.sprite.Group()

        self.player = Player(block_group=self.world_blocks, position=(10, 10))
        self.camera_scroll = self.player.get_camera_scroll()
        self.all_sprites.add(self.player)

        self.generate_world()
        self.all_sprites.add(self.world_blocks)

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
            self.world_blocks.add(Entity(image=block_textures["grass"], position=(x * BLOCK_SIZE, y)))
            while y < WINDOW_HEIGHT:
                self.world_blocks.add(
                    Entity(image=block_textures["dirt"], position=(x * BLOCK_SIZE, y + BLOCK_SIZE)))
                y += BLOCK_SIZE

    # def generate_world(self):
    #     block_textures = self.load_block_sprites()
    #     for x in range(WORLD_WIDTH):
    #         y = 300 + int((opensimplex.noise2(x=x * 0.1, y=0) + 1) * 50)
    #         y = self.lock_to_block_size(value=y)
    #         self.world_blocks.add(Entity(image=block_textures["grass"], position=(x * BLOCK_SIZE, y)))
    #         while y < WINDOW_HEIGHT:
    #             self.world_blocks.add(
    #                 Entity(image=block_textures["dirt"], position=(x * BLOCK_SIZE, y + BLOCK_SIZE)))
    #             y += BLOCK_SIZE
    #     return self.world_blocks
    #
    # def divide_to_chunks(self):
    #     for block in self.world_blocks.sprites():
    #         chunk_position = block.rect.x // CHUNK_WIDTH, block.rect.y // CHUNK_HEIGHT,
    #         x, y = str(chunk_position[0]), str(chunk_position[1])
    #         if chunk_position not in self.chunks:
    #             self.chunks[f"{x};{y}"] = pg.sprite.Group()
    #         self.chunks[f"{x};{y}"].add(block)
    #     return self.chunks

    # def find_chunks_around_player(self):
    #     self.generate_world()
    #     self.divide_to_chunks()
    #     player_chunk_position = f"{str(self.player.rect.x // CHUNK_WIDTH)};{self.player.rect.y // CHUNK_HEIGHT}"
    #     try:
    #         for block in self.chunks[player_chunk_position]:
    #             self.chunk_blocks.add(block)
    #     except KeyError:
    #         pass
    #     # self.chunk_blocks.update()
    #     # self.chunk_blocks.draw(surface=self.game.window)

    def apply_camera_scroll(self):
        for block in self.all_sprites:
            block.rect.x -= self.camera_scroll.x
            block.rect.y -= self.camera_scroll.y

    def render(self):
        self.game.window.fill("lightblue")  # getting the self.window variable from object self.game (in main.py)
        self.apply_camera_scroll()
        # self.find_chunks_around_player()
        self.all_sprites.update()
        self.all_sprites.draw(surface=self.game.window)
