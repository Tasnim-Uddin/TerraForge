import random

import pygame
from opensimplex import *

from global_constants import *
from event_manager import EventManager
from all_texture_data import block_texture_data
from player import Player
from block import Block


class Scene:
    def __init__(self, game):
        self.game = game

        self.block_textures = self.load_block_sprites()

        self.player = Player()

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.chunks = {
            # "x;y" : Block(), Block(), ...
            # "x;y" represents the chunk number as a row and column
        }

        self.surface_seed = OpenSimplex(random.randint(0, 999999999999999999999))
        # self.cave_seed = OpenSimplex(23432432432)

        self.cave_threshold = 0.3
        self.threshold_decrease_rate = 0.001

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

    def generate_chunk(self, chunk_offset):
        current_chunk_blocks = []
        for x in range(CHUNK_WIDTH):
            real_x = int(chunk_offset[
                             0] * CHUNK_WIDTH * BLOCK_SIZE + x * BLOCK_SIZE)  # exact x position of the block (in pixels)
            height_noise = int((self.surface_seed.noise2(x=real_x * 0.003, y=0) * 200) // BLOCK_SIZE * BLOCK_SIZE)

            for y in range(CHUNK_HEIGHT):
                real_y = int(chunk_offset[
                                 1] * CHUNK_HEIGHT * BLOCK_SIZE + y * BLOCK_SIZE)  # exact y position of the block (in pixels)

                air_in_cave = False

                cave_value = self.surface_seed.noise2(x=real_x * 0.003, y=real_y * 0.003)

                if cave_value > self.cave_threshold:
                    air_in_cave = True

                if real_y + height_noise == 0:
                    current_chunk_blocks.append(
                        Block(image=self.block_textures["grass"], position=(real_x, real_y)))
                elif 0 < (real_y + height_noise) <= 10 * BLOCK_SIZE:
                    current_chunk_blocks.append(
                        Block(image=self.block_textures["dirt"], position=(real_x, real_y)))
                if 10 * BLOCK_SIZE < (real_y + height_noise):
                    if not air_in_cave:
                        current_chunk_blocks.append(
                            Block(image=self.block_textures["stone"], position=(real_x, real_y)))

        return current_chunk_blocks

    # def generate_chunk(self, offset):  # fix caves getting cut horizontally
    #     current_chunk_blocks = []
    #     for x in range(CHUNK_WIDTH):
    #         real_x = offset[0] * CHUNK_WIDTH * BLOCK_SIZE + x * BLOCK_SIZE
    #
    #         surface_noise = int((self.surface_seed.noise2(x=real_x * 0.003, y=0.003) * 200) // BLOCK_SIZE * BLOCK_SIZE)
    #
    #         for y in range(CHUNK_HEIGHT):
    #             real_y = offset[1] * CHUNK_HEIGHT * BLOCK_SIZE + y * BLOCK_SIZE
    #
    #             threshold_decrease_rate = self.calculate_threshold_decrease_rate(y)
    #             cave_threshold = self.cave_threshold - real_y / (CHUNK_HEIGHT * BLOCK_SIZE) * threshold_decrease_rate
    #
    #             air_in_cave = False
    #             cave_value = self.cave_seed.noise2(x=real_x * 0.003, y=real_y * 0.003)
    #
    #             if cave_value > cave_threshold:
    #                 air_in_cave = True
    #
    #             if real_y + surface_noise == 0:
    #                 current_chunk_blocks.append(
    #                     Block(image=self.block_textures["grass"], position=(real_x, real_y)))
    #             elif 0 < (real_y + surface_noise) <= 10 * BLOCK_SIZE:
    #                 current_chunk_blocks.append(
    #                     Block(image=self.block_textures["dirt"], position=(real_x, real_y)))
    #             elif 5 * BLOCK_SIZE <= (real_y + surface_noise):
    #                 if not air_in_cave:
    #                     current_chunk_blocks.append(
    #                         Block(image=self.block_textures["stone"], position=(real_x, real_y)))
    #
    #     return current_chunk_blocks
    #
    # @staticmethod
    # def calculate_threshold_decrease_rate(y):
    #     return 0.0001 * (y ** 2)

    def break_block(self, surrounding_chunks):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (mouse_position[1] + self.camera_offset[1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        for chunk_position in surrounding_chunks:
            for block in surrounding_chunks[chunk_position]:
                if block.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                           mouse_position[1] + self.camera_offset[1]) and within_reach:
                    surrounding_chunks[chunk_position].remove(block)
                    print(f"block broken at: {block.position}")

    def place_block(self, surrounding_chunks):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (mouse_position[1] + self.camera_offset[1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        place_chunk_position = (f"{int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE))};"
                                f"{int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE))}")

        block_exists = False
        for chunk_position in surrounding_chunks:
            for block in surrounding_chunks[chunk_position]:
                if block.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                           mouse_position[1] + self.camera_offset[1]):
                    block_exists = True
                    break
            if block_exists:
                break

        if not block_exists and not self.player.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                                                  mouse_position[1] + self.camera_offset[
                                                                      1]) and within_reach:
            new_block = Block(image=self.block_textures["grass"],
                              position=(
                                  int(mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE * BLOCK_SIZE,
                                  int(mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE * BLOCK_SIZE)
                              )
            self.chunks[place_chunk_position].append(new_block)
            print(f"block placed at: {new_block.position}")

    def render(self, dt):
        self.precise_camera_offset[0] += (self.player.rect.centerx - self.precise_camera_offset[0] - WINDOW_WIDTH / 2) / HORIZONTAL_SCROLL_DELAY_FACTOR
        self.precise_camera_offset[1] += (self.player.rect.centery - self.precise_camera_offset[1] - WINDOW_HEIGHT / 2) / VERTICAL_SCROLL_DELAY_FACTOR

        if self.player.rect.centerx <= WINDOW_WIDTH / 2:  # checking for border on left side - TODO: check for right side
            self.precise_camera_offset[0] = 0

        self.camera_offset[0] = int(self.precise_camera_offset[0])
        self.camera_offset[1] = int(self.precise_camera_offset[1])

        self.game.screen.fill("lightblue")

        neighbour_chunk_offsets = [
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top right

            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # mid
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # right

            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom right
        ]

        surrounding_chunks = {}
        for offset in neighbour_chunk_offsets:
            if f"{offset[0]};{offset[1]}" not in self.chunks:
                self.chunks[f"{offset[0]};{offset[1]}"] = self.generate_chunk(offset)
            surrounding_chunks[f"{offset[0]};{offset[1]}"] = (self.chunks.get(f"{offset[0]};{offset[1]}", []))

            # fblits is newer and faster (documentation not updated yet)
            self.game.screen.fblits(
                [(block.image, (block.position[0] - self.camera_offset[0], block.position[1] - self.camera_offset[1]))
                 for block in self.chunks[f"{offset[0]};{offset[1]}"]])

        # for neighbour_keys in self.chunks.copy():  # TODO- find alternative for this as without this my memory usage goes up with every new chunk
        #     if neighbour_keys not in neighbour_chunk_offsets:
        #         self.chunks.pop(neighbour_keys)

        if EventManager.mouse_button_clicked(mouse_button=1):  # left mouse click
            self.break_block(surrounding_chunks=surrounding_chunks)

        if EventManager.mouse_button_clicked(mouse_button=3):  # right mouse click
            self.place_block(surrounding_chunks=surrounding_chunks)

        self.player.update(chunks=surrounding_chunks, dt=dt)
        self.player.render(screen=self.game.screen, offset=self.camera_offset)
