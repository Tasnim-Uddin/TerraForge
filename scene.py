import pygame
from opensimplex import *
from perlin_noise import *

from global_constants import *
from all_texture_data import block_texture_data
from player import Player
from block import Block


class Scene:
    def __init__(self, game):
        self.game = game

        self.surface_seed = OpenSimplex(4032159)
        self.cave_noise = OpenSimplex(23432432432)

        self.block_textures = self.load_block_sprites()

        self.player = Player()

        self.precise_camera_scroll = [0, 0]
        self.camera_scroll = [0, 0]

        self.chunks = {
            # "x;y" : Block(), Block(), ...
            # "x;y" represents the chunk number as a row and column
        }

    @staticmethod
    def load_block_sprites():
        textures = {}
        atlas = pygame.transform.scale(pygame.image.load(file="assets/blocks_atlas.png").convert_alpha(),
                                       size=(BLOCK_SIZE * BLOCKS_IN_ATLAS_X, BLOCK_SIZE * BLOCKS_IN_ATLAS_Y))

        for block_type, information in block_texture_data.items():
            textures[block_type] = pygame.Surface.subsurface(atlas,
                                                             pygame.Rect(information["position"][0] * BLOCK_SIZE,
                                                                         information["position"][1] * BLOCK_SIZE,
                                                                         information["size"][0],
                                                                         information["size"][1]))
        return textures

    # def generate_chunk(self, offset):
    #     current_chunk_blocks = []
    #     for x in range(CHUNK_WIDTH):
    #         real_x = offset[0] * CHUNK_WIDTH * BLOCK_SIZE + x * BLOCK_SIZE
    #         height_noise = int((self.seed.noise2(x=real_x * 0.003, y=0) * 200) // BLOCK_SIZE * BLOCK_SIZE)
    #
    #         for y in range(CHUNK_HEIGHT):
    #             real_y = offset[1] * CHUNK_HEIGHT * BLOCK_SIZE + y * BLOCK_SIZE
    #
    #             if real_y + height_noise == 0:
    #                 current_chunk_blocks.append(
    #                     Block(image=self.block_textures["grass"], position=(real_x, real_y)))
    #             elif 0 < (real_y + height_noise) <= 5 * BLOCK_SIZE:
    #                 current_chunk_blocks.append(
    #                     Block(image=self.block_textures["dirt"], position=(real_x, real_y)))
    #             if 5 * BLOCK_SIZE < (real_y + height_noise) <= 20 * BLOCK_SIZE:
    #                 current_chunk_blocks.append(
    #                     Block(image=self.block_textures["stone"], position=(real_x, real_y)))
    #
    #     return current_chunk_blocks

    def generate_chunk(self, offset):
        current_chunk_blocks = []
        for x in range(CHUNK_WIDTH):
            real_x = offset[0] * CHUNK_WIDTH * BLOCK_SIZE + x * BLOCK_SIZE  # exact x position of the block (in pixels)
            height_noise = int((self.surface_seed.noise2(x=real_x * 0.003, y=0) * 200) // BLOCK_SIZE * BLOCK_SIZE)

            for y in range(CHUNK_HEIGHT):
                real_y = offset[1] * CHUNK_HEIGHT * BLOCK_SIZE + y * BLOCK_SIZE  # exact y position of the block (in pixels)

                air_in_cave = False

                if self.surface_seed.noise2(x=real_x * 0.003, y=real_y * 0.003) > CAVE_AIR_THRESHOLD:
                    air_in_cave = True

                if real_y + height_noise == 0:
                    current_chunk_blocks.append(
                        Block(image=self.block_textures["grass"], position=(real_x, real_y)))
                elif 0 < (real_y + height_noise) <= 5 * BLOCK_SIZE:
                    current_chunk_blocks.append(
                        Block(image=self.block_textures["dirt"], position=(real_x, real_y)))
                if 5 * BLOCK_SIZE < (real_y + height_noise):
                    if not air_in_cave > CAVE_AIR_THRESHOLD:
                        current_chunk_blocks.append(
                            Block(image=self.block_textures["stone"], position=(real_x, real_y)))

        return current_chunk_blocks

    # @staticmethod
    # def get_block_type(real_y, noise, cave_open):
    #     block_type = "air"
    #     if cave_open:
    #         block_type = "air"
    #     else:
    #         if real_y + noise == 0:
    #             block_type = "grass"
    #         elif 0 < (real_y + noise) <= 5 * BLOCK_SIZE:
    #             block_type = "dirt"
    #         elif 5 * BLOCK_SIZE < (real_y + noise) <= 20 * BLOCK_SIZE:
    #             block_type = "stone"
    #
    #     return block_type

    def render(self):
        self.precise_camera_scroll[0] = (self.player.rect.x - WINDOW_WIDTH / 2 + self.player.rect.width / 2)
        self.precise_camera_scroll[1] = self.player.rect.y - WINDOW_HEIGHT / 2 + self.player.rect.height / 2

        if self.player.rect.centerx <= WINDOW_WIDTH / 2:  # checking for border on left side - #TODO check for right side
            self.precise_camera_scroll[0] = 0

        self.camera_scroll[0] = self.precise_camera_scroll[0]
        self.camera_scroll[1] = self.precise_camera_scroll[1]

        self.game.screen.fill("lightblue")

        neighbour_chunk_offsets = [
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top left
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top right

            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # left
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # mid
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # right

            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom left
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom right
        ]

        surrounding_chunks = {}
        for offset in neighbour_chunk_offsets:
            if f"{offset[0]};{offset[1]}" not in self.chunks:
                self.chunks[f"{offset[0]};{offset[1]}"] = self.generate_chunk(offset)
            self.game.screen.fblits(
                [(block.image, (block.position[0] - self.camera_scroll[0], block.position[1] - self.camera_scroll[1]))
                 for block in self.chunks[f"{offset[0]};{offset[1]}"]])
            surrounding_chunks[f"{offset[0]};{offset[1]}"] = (self.chunks.get(f"{offset[0]};{offset[1]}", []))

        # for neighbour_keys in self.chunks.copy():  # TODO- find alternative for this as without this my memory usage goes up with every new chunk
        #     if neighbour_keys not in neighbour_chunk_offsets:
        #         self.chunks.pop(neighbour_keys)

        self.player.movement(chunks=surrounding_chunks)
        self.player.render(screen=self.game.screen, offset=self.camera_scroll)
