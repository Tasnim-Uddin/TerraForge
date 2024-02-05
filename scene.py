import random
from opensimplex import *

from global_constants import *
from player import Player
from entity import Entity
from inventory import *


class Scene:
    def __init__(self, screen):
        self.screen = screen

        self.block_textures = self.load_block_sprites()

        self.inventory = Inventory(screen=self.screen, textures=self.block_textures)

        self.player = Player()

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.chunks = {
            # "x;y" : Entity(), Entity(), ...
            # "x;y" represents the chunk number as a row and column
        }

        self.surface_seed = OpenSimplex(random.randint(0, 999999999999999999999))

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
                        Entity(block="grass", image=self.block_textures["grass"], position=(real_x, real_y)))
                elif 0 < (real_y + height_noise) <= 10 * BLOCK_SIZE:
                    current_chunk_blocks.append(
                        Entity(block="dirt", image=self.block_textures["dirt"], position=(real_x, real_y)))
                if 10 * BLOCK_SIZE < (real_y + height_noise):
                    if not air_in_cave:
                        current_chunk_blocks.append(
                            Entity(block="stone", image=self.block_textures["stone"], position=(real_x, real_y)))

        return current_chunk_blocks

    def break_block(self, surrounding_chunks, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = bool(int((((mouse_position[0] + self.camera_offset[0] - self.player.rect.centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.player.rect.centery) ** 2) ** 0.5) / BLOCK_SIZE) <= REACH)

        for chunk_position in surrounding_chunks:
            for block in surrounding_chunks[chunk_position]:
                if block.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                           mouse_position[1] + self.camera_offset[1]) and within_reach:
                    breaking_item = block.block
                    if held_item == "pickaxe" and self.inventory.is_block(item=breaking_item):
                        self.inventory.add_item(item=breaking_item)
                        surrounding_chunks[chunk_position].remove(block)

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
                if block.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                           mouse_position[1] + self.camera_offset[1]):
                    block_exists = True
                    break
            if block_exists:
                break

        if not block_exists and not self.player.rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                                                  mouse_position[1] + self.camera_offset[
                                                                      1]) and within_reach:
            if self.inventory.is_block(item=held_item):
                new_block = Entity(block=held_item, image=self.block_textures[held_item],
                                   position=(
                                       int(mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE * BLOCK_SIZE,
                                       int(mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE * BLOCK_SIZE)
                                   )
                self.chunks[place_chunk_position].append(new_block)
                self.inventory.remove_item(item=held_item)

    def draw(self, dt):
        self.precise_camera_offset[0] += (self.player.rect.centerx - self.precise_camera_offset[
            0] - WINDOW_WIDTH / 2) / HORIZONTAL_SCROLL_DELAY_FACTOR
        self.precise_camera_offset[1] += (self.player.rect.centery - self.precise_camera_offset[
            1] - WINDOW_HEIGHT / 2) / VERTICAL_SCROLL_DELAY_FACTOR

        if self.player.rect.centerx <= WINDOW_WIDTH / 2:  # checking for border on left side - TODO: check for right side
            self.precise_camera_offset[0] = 0

        self.camera_offset[0] = int(self.precise_camera_offset[0])
        self.camera_offset[1] = int(self.precise_camera_offset[1])

        self.screen.fill("#5c7cf4")

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
            self.screen.fblits(
                [(block.image, (block.position[0] - self.camera_offset[0], block.position[1] - self.camera_offset[1]))
                 for block in self.chunks[f"{offset[0]};{offset[1]}"]])

        held_item = self.inventory.get_selected_item()
        if EventManager.mouse_button_clicked(mouse_button=1):  # left mouse click
            self.break_block(surrounding_chunks=surrounding_chunks, held_item=held_item)

        if EventManager.mouse_button_clicked(mouse_button=3):  # right mouse click
            self.place_block(surrounding_chunks=surrounding_chunks, held_item=held_item)

        self.inventory.update()
        self.player.update(chunks=surrounding_chunks, dt=dt)
        self.player.render(screen=self.screen, offset=self.camera_offset)
        self.inventory.draw()
