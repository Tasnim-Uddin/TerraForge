import math
import random

import pygame
from opensimplex import *

from player import Player
from inventory import *
from event_manager import EventManager
from global_constants import *
from slime_enemy import SlimeEnemy


class Scene:
    def __init__(self, screen, world_name, inventory_name):
        self.screen = screen

        self.block_textures = self.load_block_sprites()

        self.chunks = self.load_world_from_json(world_name=world_name)

        # {(chunk_x, chunk_y): {(block_x, block_y): "block_type"}}  block_type is "grass", "dirt", "stone", ...

        self.inventory = Inventory(screen=self.screen, textures=self.block_textures,
                                   inventory_name=inventory_name)

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.surface_seed = OpenSimplex(random.randint(0, 99999999))

        self.lower_cave_threshold = 0.015
        self.upper_cave_threshold = 0.7

        self.player = Player()

        self.enemies = []
        self.spawn_enemy()

    def spawn_enemy(self):
        new_enemy = SlimeEnemy()
        self.enemies.append(new_enemy)

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
            textures[item] = pygame.transform.scale(surface=textures[item], size=(BLOCK_SIZE, BLOCK_SIZE))
        return textures

    def generate_chunk(self, chunk_offset, key):
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
                    self.chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "grass"
                elif 0 < (real_y + height_noise) <= 10 * BLOCK_SIZE:
                    self.chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "dirt"
                if 10 * BLOCK_SIZE < (real_y + height_noise):
                    if not air_in_cave:
                        self.chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "stone"

    def break_block(self):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        break_chunk_position = (int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE)),
                                int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE)))

        break_block_position = (int((mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE),
                                int((mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE))

        try:
            breaking_item = self.chunks[break_chunk_position][break_block_position]
            if self.inventory.item_type(item=self.chunks[break_chunk_position][break_block_position]) == "block" and within_reach:
                self.inventory.add_item(item=breaking_item)
                del self.chunks[break_chunk_position][break_block_position]
        except KeyError:
            pass

    def place_block(self, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE <= REACH)

        place_chunk_position = (int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE)),
                                int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE)))

        place_block_position = (int((mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE),
                                int((mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE))

        block_exists = bool(place_chunk_position in self.chunks and place_block_position in self.chunks[place_chunk_position])

        # To make sure that the block cannot be placed within the block grid a player is on
        player_max_right = math.ceil(self.player.rect.right / BLOCK_SIZE) * BLOCK_SIZE
        player_min_left = (self.player.rect.left // BLOCK_SIZE) * BLOCK_SIZE
        player_min_top = (self.player.rect.top // BLOCK_SIZE) * BLOCK_SIZE
        player_max_bottom = math.ceil(self.player.rect.bottom / BLOCK_SIZE) * BLOCK_SIZE
        player_block_rect = pygame.Rect(player_min_left, player_min_top, player_max_right - player_min_left,
                                        player_max_bottom - player_min_top)

        if not block_exists and not player_block_rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                                                   mouse_position[1] + self.camera_offset[
                                                                       1]) and within_reach:
            self.chunks[place_chunk_position][place_block_position] = held_item
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
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top left
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top right

            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Left
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Middle
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Right

            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom left
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom
            (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
             int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom right
        ]

        surrounding_chunks = {}
        for offset in neighbour_chunk_offsets:
            if (offset[0], offset[1]) not in self.chunks:
                self.chunks[(offset[0], offset[1])] = {}
                self.generate_chunk(offset, key=(offset[0], offset[1]))
            if (offset[0], offset[1]) not in surrounding_chunks:
                surrounding_chunks[(offset[0], offset[1])] = []
            surrounding_chunks[(offset[0], offset[1])] = self.chunks.get((offset[0], offset[1]), [])

            # self.screen.fblits(
            #     [(self.block_textures[block],
            #                      (block_position[0] * BLOCK_SIZE -
            #                       self.camera_offset[0],
            #                       block_position[1] * BLOCK_SIZE -
            #                       self.camera_offset[1])
            #       )
            #      for block_position, block in surrounding_chunks[(offset[0], offset[1])]])

            for block_position, block in surrounding_chunks[(offset[0], offset[1])].items():
                self.screen.blit(self.block_textures[block],
                                 (block_position[0] * BLOCK_SIZE -
                                  self.camera_offset[0],
                                  block_position[1] * BLOCK_SIZE -
                                  self.camera_offset[1]))

        held_item = self.inventory.get_selected_item()

        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse click
                    if self.inventory.item_type(item=held_item) == "pickaxe":
                        self.break_block()
                if event.button == 3:  # right mouse click
                    if self.inventory.item_type(item=held_item) == "block":
                        self.place_block(held_item=held_item)


        for enemy in self.enemies:
            relative_chunk_position = (
                int(enemy.x // (CHUNK_WIDTH * BLOCK_SIZE)),
                int(enemy.y // (CHUNK_HEIGHT * BLOCK_SIZE))
            )
            # Check if the relative chunk position is in surrounding_chunks
            if relative_chunk_position in surrounding_chunks:
                enemy.attack_update(player=self.player, dt=dt)
                enemy.update(chunks=surrounding_chunks, dt=dt)
                enemy.draw(screen=self.screen, camera_offset=self.camera_offset)
                if self.inventory.item_type(item=held_item) == "sword":
                    self.player.attack(enemy=enemy, camera_offset=self.camera_offset, dt=dt)
            else:
                self.enemies.remove(enemy)

            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.inventory.add_item(item="slime")  # TODO: change stone to slime and add slime texture

        self.player.update(chunks=surrounding_chunks, dt=dt)
        self.player.draw(screen=self.screen, camera_offset=self.camera_offset)
        self.inventory.update()
        self.inventory.draw()

    def save_world_to_json(self, world_name):
        world_path = os.path.join(WORLD_SAVE_FOLDER, f"{world_name}.json")
        # Convert tuple keys to strings
        serialised_chunks = {f"{chunk_position[0]};{chunk_position[1]}": {f"{block_position[0]};{block_position[1]}": block for block_position, block in blocks_dict.items()} for chunk_position, blocks_dict in self.chunks.items()}
        # Save serialised chunks to a JSON file
        with open(world_path, "w") as json_file:
            json.dump(serialised_chunks, json_file)

    @staticmethod
    def load_world_from_json(world_name):
        world_path = os.path.join(WORLD_SAVE_FOLDER, f"{world_name}.json")
        if os.path.exists(world_path):

            # Load serialized chunks from the JSON file
            with open(world_path, "r") as json_file:
                serialised_chunks = json.load(json_file)
            # Convert string keys back to tuples
            chunks = {tuple(map(int, chunk_position.split(";"))): {tuple(map(int, block_position.split(";"))): block for block_position, block in blocks_dict.items()} for chunk_position, blocks_dict in serialised_chunks.items()}
        else:
            chunks = {}
        return chunks
