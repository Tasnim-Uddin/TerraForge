import random

import pygame
from opensimplex import *

from player import Player
from entity import *
from inventory import *


class Scene:
    def __init__(self, screen):
        self.screen = screen

        self.block_textures = self.load_block_sprites()

        self.inventory = Inventory(screen=self.screen, textures=self.block_textures)

        self.player = Player()

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.chunks = {}

        self.surface_seed = OpenSimplex(random.randint(0, 0))

        self.lower_cave_threshold = 0.015
        self.upper_cave_threshold = 0.7

    @staticmethod
    def load_block_sprites():
        textures = {}
        atlas = pygame.image.load(file="assets/texture_sheet.png").convert_alpha()

        for item, information in all_texture_data.items():
            textures[item] = pygame.Surface.subsurface(atlas,
                                                       pygame.Rect(
                                                           information["position"][0],
                                                           information["position"][1],
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

                if self.lower_cave_threshold < cave_value < self.upper_cave_threshold:
                    air_in_cave = True

                if real_y + height_noise == 0:
                    current_chunk_blocks.append(
                        Entity(block="grass", position=(real_x / BLOCK_SIZE, real_y / BLOCK_SIZE)))
                elif 0 < (real_y + height_noise) <= 10 * BLOCK_SIZE:
                    current_chunk_blocks.append(
                        Entity(block="dirt", position=(real_x / BLOCK_SIZE, real_y / BLOCK_SIZE)))
                if 10 * BLOCK_SIZE < (real_y + height_noise):
                    if not air_in_cave:
                        current_chunk_blocks.append(
                            Entity(block="stone", position=(real_x / BLOCK_SIZE, real_y / BLOCK_SIZE)))

        return current_chunk_blocks

    def break_block(self, surrounding_chunks, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        break_chunk_position = (f"{int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE))};"
                                f"{int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE))}")

        for chunk_position in surrounding_chunks:
            for block in surrounding_chunks[chunk_position]:
                if pygame.Rect(block.rect.x * BLOCK_SIZE, block.rect.y * BLOCK_SIZE, block.rect.width,
                               block.rect.height).collidepoint(mouse_position[0] + self.camera_offset[0],
                                                               mouse_position[1] + self.camera_offset[
                                                                   1]) and within_reach:
                    breaking_item = block.block
                    if held_item == "pickaxe" and self.inventory.is_block(item=breaking_item):
                        self.inventory.add_item(item=breaking_item)
                        print("surrounding_chunks", block in surrounding_chunks[break_chunk_position])
                        print("self.chunks", block in self.chunks[break_chunk_position])
                        print(block.block, block.position)
                        for current_block in self.chunks[break_chunk_position]:
                            if current_block.block == block.block and current_block.position == block.position:
                                self.chunks[break_chunk_position].remove(current_block)
                                break

    def place_block(self, surrounding_chunks, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        place_chunk_position = (f"{int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE))};"
                                f"{int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE))}")

        block_exists = False
        for chunk_position in surrounding_chunks:
            for block in surrounding_chunks[chunk_position]:
                if pygame.Rect(block.rect.x * BLOCK_SIZE, block.rect.y * BLOCK_SIZE, block.rect.width,
                               block.rect.height).collidepoint(mouse_position[0] + self.camera_offset[0],
                                                               mouse_position[1] + self.camera_offset[
                                                                   1]):
                    block_exists = True
                    break
            if block_exists:
                break

        if not block_exists and not self.player.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                                                  mouse_position[1] + self.camera_offset[
                                                                      1]) and within_reach:
            if self.inventory.is_block(item=held_item):
                new_block = Entity(block=held_item,
                                   position=(
                                       int(mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE,
                                       int(mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE)
                                   )
                self.chunks[place_chunk_position].append(new_block)
                self.inventory.remove_item(item=held_item)

    def draw(self, dt):
        self.precise_camera_offset[0] += (self.player.rect.centerx - self.precise_camera_offset[
            0] - WINDOW_WIDTH / 2) / HORIZONTAL_SCROLL_DELAY_FACTOR
        self.precise_camera_offset[1] += (self.player.rect.centery - self.precise_camera_offset[
            1] - WINDOW_HEIGHT / 2) / VERTICAL_SCROLL_DELAY_FACTOR

        if self.player.rect.centerx <= WINDOW_WIDTH / 2:  # Checking for the border on the left side - TODO: Check for the right side
            self.precise_camera_offset[0] = 0

        self.camera_offset[0] = int(self.precise_camera_offset[0])
        self.camera_offset[1] = int(self.precise_camera_offset[1])

        # Sky colour
        self.screen.fill("#5c7cf4")

        neighbour_chunk_offsets = [
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # Top left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # Top
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # Top right

            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # Left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # Middle
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)),  # Right

            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # Bottom left
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # Bottom
            (self.player.rect.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.rect.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # Bottom right
        ]
        surrounding_chunks = {}
        for offset in neighbour_chunk_offsets:
            if f"{offset[0]};{offset[1]}" not in self.chunks:
                self.chunks[f"{offset[0]};{offset[1]}"] = self.generate_chunk(offset)
            if f"{offset[0]};{offset[1]}" not in surrounding_chunks:
                surrounding_chunks[f"{offset[0]};{offset[1]}"] = []
            for block_data in self.chunks.get(f"{offset[0]};{offset[1]}", []):
                block = block_data.block
                image = pygame.transform.scale(surface=self.block_textures[block_data.block],
                                               size=(BLOCK_SIZE, BLOCK_SIZE))
                rect = image.get_rect(topleft=(block_data.position[0], block_data.position[1]))
                surrounding_chunks[f"{offset[0]};{offset[1]}"].append(
                    ComplexEntity(block=block, position=block_data.position, image=image,
                                  rect=rect))  # [0]: block (e.g. "grass"), [1]: pygame image, [2]: rect

            # fblits is newer and faster (documentation not updated yet as of coding)
            self.screen.fblits(
                [(block.image,
                  (
                  block.rect.x * BLOCK_SIZE - self.camera_offset[0], block.rect.y * BLOCK_SIZE - self.camera_offset[1]))
                 for block in surrounding_chunks[f"{offset[0]};{offset[1]}"]])

        held_item = self.inventory.get_selected_item()

        if EventManager.left_mouse_click():
            self.break_block(surrounding_chunks=surrounding_chunks, held_item=held_item)

        if EventManager.right_mouse_click():
            self.place_block(surrounding_chunks=surrounding_chunks, held_item=held_item)

        self.inventory.update()
        self.player.update(chunks=surrounding_chunks, dt=dt)
        self.player.render(screen=self.screen, offset=self.camera_offset)
        self.inventory.draw()
