import math
import random

from opensimplex import *

from player import Player
from inventory import *
from event_manager import EventManager
from global_constants import *
from slime_enemy import SlimeEnemy


class Scene:
    def __init__(self, game):

        self.screen = game.screen

        self.__inventory_name = game.get_player_name()
        self.__world_name = game.get_world_name()

        self.all_textures = self.load_textures()

        self.__chunks = self.load_world_from_json()
        # {(chunk_x, chunk_y): {(block_x, block_y): "block_type"}}  block_type is "grass", "dirt", "stone", ...
        self.missing_tree_positions = {}

        self.__inventory = Inventory(game=game, screen=self.screen, textures=self.all_textures)

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.surface_seed = OpenSimplex(random.randint(0, 99999999))

        self.lower_cave_threshold = 0.015
        self.upper_cave_threshold = 0.7

        self.__player = Player()

        self.__enemies = []
        self.__spawn_enemy()

    def get_player(self):
        return self.__player

    def get_inventory(self):
        return self.__inventory

    def __spawn_enemy(self):
        new_enemy = SlimeEnemy()
        self.__enemies.append(new_enemy)

    @staticmethod
    def load_textures():
        textures = {}
        atlas = pygame.image.load(file="assets/textures/texture_sheet.png").convert_alpha()

        for item, information in all_texture_data.items():
            textures[item] = pygame.Surface.subsurface(atlas,
                                                       pygame.Rect(
                                                           information["position"][0],
                                                           information["position"][1],
                                                           information["size"][0],
                                                           information["size"][1]))
            textures[item] = pygame.transform.scale(surface=textures[item], size=(BLOCK_SIZE, BLOCK_SIZE))
        return textures

    def __generate_chunk(self, chunk_offset, key):
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

                if (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE)) not in self.__chunks[key]:

                    if real_y + height_noise == 0:
                        self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "grass"
                        # print("block: ", (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE)))
                        if random.random() < 0.07:

                            # for y_shift_up in range(1, 5):
                            #     if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                            #         if y_shift_up == 4:
                            #             self.__chunks[(key[0], key[1] - 1)][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                            #         else:
                            #             self.__chunks[(key[0], key[1] - 1)][
                            #                 (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                            #     else:
                            #         if y_shift_up == 4:
                            #             self.__chunks[(key[0], key[1])][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                            #         else:
                            #             self.__chunks[(key[0], key[1])][
                            #                 (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                            #
                            # # TODO: fix code so it works for leaf blocks on top of tree, like a pyramid shape. should have 2 for loops
                            # for x_shift in range(-1, 2):
                            #     if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                            #         self.__chunks[(key[0] - 1, key[1])][
                            #             (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE))] = "tree_leaf"
                            #     elif int(real_x / BLOCK_SIZE) + x_shift > key[0] * CHUNK_WIDTH:
                            #         self.__chunks[(key[0] + 1, key[1])][
                            #             (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE))] = "tree_leaf"
                            #     else:
                            #         self.__chunks[key][(int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE))] = "tree_leaf"

                            # for y_shift_up in range(1, 4):
                            #     # tree_key = (int(real_x / (BLOCK_SIZE * CHUNK_WIDTH)), int(((real_y / BLOCK_SIZE) - y_shift_up) / CHUNK_HEIGHT))
                            #     if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                            #         tree_key = (key[0], key[1] - 1)
                            #         if tree_key not in self.missing_tree_positions:
                            #             self.missing_tree_positions[tree_key] = {}
                            #         self.missing_tree_positions[tree_key][
                            #             (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                            #     else:
                            #         self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                            #
                            # x_shift_start = -2
                            # x_shift_end = 2
                            # for layer in range(4, 7):  # Number of iterations
                            #     all_x_shifts = range(x_shift_start, x_shift_end + 1)
                            #     for x_shift in all_x_shifts:
                            #         if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                            #             tree_key = (key[0] - 1, key[1])
                            #             if tree_key not in self.missing_tree_positions:
                            #                 self.missing_tree_positions[tree_key] = {}
                            #             self.missing_tree_positions[tree_key][
                            #                 (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #         elif int(real_x / BLOCK_SIZE) + x_shift > key[0] * CHUNK_WIDTH:
                            #             tree_key = (key[0] + 1, key[1])
                            #             if tree_key not in self.missing_tree_positions:
                            #                 self.missing_tree_positions[tree_key] = {}
                            #             self.missing_tree_positions[tree_key][
                            #                 (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #         else:
                            #             self.__chunks[key][
                            #                 (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #
                            #     x_shift_start += 1
                            #     x_shift_end -= 1

                            x_shift_start = -2
                            x_shift_end = 2
                            for y_shift_up in range(1, 7):  # Number of layers of tree (bottom to top)
                                if y_shift_up < 4:
                                    if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                        tree_key = (key[0], key[1] - 1)
                                        if tree_key not in self.missing_tree_positions:
                                            self.missing_tree_positions[tree_key] = {}
                                        self.missing_tree_positions[tree_key][
                                            (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                                    else:
                                        self.__chunks[key][
                                            (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree"
                                # else:  # TODO: fix leaves here
                                #     for x_shift in range(x_shift_start, x_shift_end + 1):
                                #         if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                                #             tree_key = (key[0] - 1, key[1])
                                #             if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                #                 tree_key = (key[0] - 1, key[1] - 1)
                                #             if tree_key not in self.missing_tree_positions:
                                #                 self.missing_tree_positions[tree_key] = {}
                                #             self.missing_tree_positions[tree_key][
                                #                 (int(real_x / BLOCK_SIZE) + x_shift,
                                #                  int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                #         elif int(real_x / BLOCK_SIZE) + x_shift > key[0] * CHUNK_WIDTH:
                                #             tree_key = (key[0] + 1, key[1])
                                #             if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                #                 tree_key = (key[0] + 1, key[1] - 1)
                                #             if tree_key not in self.missing_tree_positions:
                                #                 self.missing_tree_positions[tree_key] = {}
                                #             self.missing_tree_positions[tree_key][
                                #                 (int(real_x / BLOCK_SIZE) + x_shift,
                                #                  int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                #         else:
                                #             tree_key = key
                                #             if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                #                 tree_key = (key[0], key[1] - 1)
                                #             self.__chunks[tree_key][
                                #                 (int(real_x / BLOCK_SIZE) + x_shift,
                                #                  int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                #     x_shift_start += 1
                                #     x_shift_end -= 1

                            # for layer in range(1, 4):
                            #     for x_shift in range(-1, 2):
                            #         if layer == 2 and (x_shift == -1 or x_shift == 2):
                            #             continue
                            #         if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                            #             self.__chunks[(key[0] - 1, key[1])][(int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) + 4)] = "tree_leaf"

                            # start = -2
                            # end = 3
                            # for layer in range(4, 7):  # Number of iterations
                            #     all_x_shifts = range(start, end)
                            #     print(start, end)
                            #     for x_shift in all_x_shifts:
                            #         # print("Iteration:", layer, "x:", x_shift)
                            #         if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                            #             try:
                            #                 self.__chunks[(key[0] - 1, key[1])][
                            #                     (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #             except KeyError:
                            #                 print(int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)
                            #                 print("less")
                            #         elif int(real_x / BLOCK_SIZE) + x_shift > key[0] * CHUNK_WIDTH:
                            #             try:
                            #                 self.__chunks[(key[0] + 1, key[1])][
                            #                     (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #             except KeyError:
                            #                 print(int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)
                            #                 print("more")
                            #         else:
                            #                 self.__chunks[key][
                            #                     (int(real_x / BLOCK_SIZE) + x_shift, int(real_y / BLOCK_SIZE) - layer)] = "tree_leaf"
                            #     start += 1
                            #     end -= 1

                    elif 0 < (real_y + height_noise) <= 10 * BLOCK_SIZE:
                        self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "dirt"
                    if 10 * BLOCK_SIZE < (real_y + height_noise):
                        if not air_in_cave:
                            self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "stone"

        # # Generate trees
        # for _ in range(CHUNK_WIDTH):
        #     if random.random() < 2:
        #         tree_x = random.randint(1, CHUNK_WIDTH)
        #         tree_y = 0
        #
        #         real_tree_x = int(chunk_offset[0] * CHUNK_WIDTH * BLOCK_SIZE + tree_x * BLOCK_SIZE)
        #         real_tree_y = int(chunk_offset[1] * CHUNK_HEIGHT * BLOCK_SIZE + tree_y * BLOCK_SIZE)
        #
        #         # Ensure that the block beneath the potential tree location is grass
        #         if (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) + 1) in self.__chunks[key] and self.__chunks[key][
        #             (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) + 1)] == "grass":
        #             # Ensure that the tree doesn't overwrite existing blocks
        #             if (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE)) not in self.__chunks[key] and \
        #                 (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 1) not in self.__chunks[key] and \
        #                 (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 2) not in self.__chunks[key] and \
        #                 (int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 3) not in self.__chunks[key]:
        #                 self.__chunks[key][(int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE))] = "tree"
        #                 self.__chunks[key][(int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 1)] = "tree"
        #                 self.__chunks[key][(int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 2)] = "tree"
        #                 self.__chunks[key][(int(real_tree_x / BLOCK_SIZE), int(real_tree_y / BLOCK_SIZE) - 3)] = "tree_leaf"

    def __break_block(self, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = False
        distance = int((((mouse_position[0] + self.camera_offset[0] - self.__player.get_rect().centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.__player.get_rect().centery) ** 2) ** 0.5) / BLOCK_SIZE)
        if distance <= REACH:
            within_reach = True

        break_chunk_position = (int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE)),
                                int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE)))

        break_block_position = (int((mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE),
                                int((mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE))

        try:
            breaking_item = self.__chunks[break_chunk_position][break_block_position]
            if (self.__inventory.get_item_type(
                    item=self.__chunks[break_chunk_position][break_block_position]) == "block") and within_reach:
                if (self.__inventory.get_item_type(item=held_item) == "pickaxe" and "tree" not in self.__chunks[break_chunk_position][break_block_position]) or (self.__inventory.get_item_type(item=held_item) == "axe" and "tree" in self.__chunks[break_chunk_position][break_block_position]):
                    self.__inventory.add_item(item=breaking_item)
                    del self.__chunks[break_chunk_position][break_block_position]

        except KeyError:
            pass

    def __place_block(self, held_item):
        mouse_position = pygame.mouse.get_pos()

        within_reach = False
        distance = int((((mouse_position[0] + self.camera_offset[0] - self.__player.get_rect().centerx) ** 2 + (
                mouse_position[1] + self.camera_offset[
            1] - self.__player.get_rect().centery) ** 2) ** 0.5) / BLOCK_SIZE)
        if distance <= REACH:
            within_reach = True

        place_chunk_position = (int((mouse_position[0] + self.camera_offset[0]) // (CHUNK_WIDTH * BLOCK_SIZE)),
                                int((mouse_position[1] + self.camera_offset[1]) // (CHUNK_WIDTH * BLOCK_SIZE)))

        place_block_position = (int((mouse_position[0] + self.camera_offset[0]) // BLOCK_SIZE),
                                int((mouse_position[1] + self.camera_offset[1]) // BLOCK_SIZE))

        block_exists = bool(
            place_chunk_position in self.__chunks and place_block_position in self.__chunks[place_chunk_position])

        # To make sure that the block cannot be placed within the block grid a player is on
        player_max_right = math.ceil(self.__player.get_rect().right / BLOCK_SIZE) * BLOCK_SIZE
        player_min_left = (self.__player.get_rect().left // BLOCK_SIZE) * BLOCK_SIZE
        player_min_top = (self.__player.get_rect().top // BLOCK_SIZE) * BLOCK_SIZE
        player_max_bottom = math.ceil(self.__player.get_rect().bottom / BLOCK_SIZE) * BLOCK_SIZE
        player_block_rect = pygame.Rect(player_min_left, player_min_top, player_max_right - player_min_left,
                                        player_max_bottom - player_min_top)

        if not block_exists and within_reach and ("tree" in held_item or not player_block_rect.collidepoint(mouse_position[0] + self.camera_offset[0],
                                                                   mouse_position[1] + self.camera_offset[
                                                                       1])):
            self.__chunks[place_chunk_position][place_block_position] = held_item
            self.__inventory.remove_item(item=held_item)

    def update_draw(self, dt):
        self.precise_camera_offset[0] += (self.__player.get_rect().centerx - self.precise_camera_offset[
            0] - WINDOW_WIDTH / 2) / HORIZONTAL_SCROLL_DELAY_FACTOR
        self.precise_camera_offset[1] += (self.__player.get_rect().centery - self.precise_camera_offset[
            1] - WINDOW_HEIGHT / 2) / VERTICAL_SCROLL_DELAY_FACTOR

        self.camera_offset[0] = int(self.precise_camera_offset[0])
        self.camera_offset[1] = int(self.precise_camera_offset[1])

        # Sky colour
        self.screen.fill("#5c7cf4")

        # neighbour_chunk_offsets = [
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top left
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) + 1)),  # Top right
        #
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Left
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Middle
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE))),  # Right
        #
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) - 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom left
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE)),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom
        #     (int(self.player.x // (CHUNK_WIDTH * BLOCK_SIZE) + 1),
        #      int(self.player.y // (CHUNK_HEIGHT * BLOCK_SIZE) - 1)),  # Bottom right
        # ]

        neighbour_chunk_offsets = []
        for chunk_y_offset in range(-1, 2):
            for chunk_x_offset in range(-1, 2):
                neighbour_chunk_offsets.append((
                    int(self.__player.get_x() // (CHUNK_WIDTH * BLOCK_SIZE) + chunk_x_offset),
                    int(self.__player.get_y() // (CHUNK_HEIGHT * BLOCK_SIZE) + chunk_y_offset)
                ))

        surrounding_chunks = {}
        for offset in neighbour_chunk_offsets:
            if (offset[0], offset[1]) not in self.__chunks:
                self.__chunks[(offset[0], offset[1])] = {}
                self.__generate_chunk(chunk_offset=offset, key=(offset[0], offset[1]))
            if (offset[0], offset[1]) not in surrounding_chunks:
                surrounding_chunks[(offset[0], offset[1])] = []
            surrounding_chunks[(offset[0], offset[1])] = self.__chunks.get((offset[0], offset[1]), [])

        for chunk_position, block_information in list(self.missing_tree_positions.items()):
            for position, tree_block in list(block_information.items()):
                offset = (int(position[0] // CHUNK_WIDTH), int(position[1] // CHUNK_HEIGHT))
                print(position, offset)

                if chunk_position in self.__chunks:
                    self.__chunks[chunk_position][position] = tree_block
                    surrounding_chunks[(chunk_position[0], chunk_position[1])] = self.__chunks.get((chunk_position[0], chunk_position[1]), [])
                    self.screen.fblits([(self.all_textures[tree_block], (
                    position[0] * BLOCK_SIZE - self.camera_offset[0],
                    position[1] * BLOCK_SIZE - self.camera_offset[1]))])
                    del self.missing_tree_positions[chunk_position][position]

        for offset in neighbour_chunk_offsets:
            for block_position, block in surrounding_chunks[(offset[0], offset[1])].items():
                self.screen.fblits([(self.all_textures[block],
                                     (block_position[0] * BLOCK_SIZE -
                                      self.camera_offset[0],
                                      block_position[1] * BLOCK_SIZE -
                                      self.camera_offset[1]))])


        # self.missing_tree_positions = {}

        held_item = self.__inventory.get_selected_item()

        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse click
                    self.__break_block(held_item=held_item)
                    if self.__inventory.get_item_type(item=held_item) == "sword":
                        sword_swing_sound = pygame.mixer.Sound("assets/sound/sword_swing.mp3")
                        sword_swing_sound.set_volume(0.2)
                        sword_swing_sound.play()
                if event.button == 3:  # right mouse click
                    if self.__inventory.get_item_type(item=held_item) == "block":
                        self.__place_block(held_item=held_item)

        for enemy in self.__enemies:
            relative_chunk_position = (
                int(enemy.get_x() // (CHUNK_WIDTH * BLOCK_SIZE)),
                int(enemy.get_y() // (CHUNK_HEIGHT * BLOCK_SIZE))
            )
            # Check if the relative chunk position is in surrounding_chunks
            if relative_chunk_position in surrounding_chunks:
                enemy.attack_update(player=self.__player, dt=dt)
                enemy.update(chunks=surrounding_chunks, dt=dt)
                enemy.draw(screen=self.screen, camera_offset=self.camera_offset)
                if self.__inventory.get_item_type(item=held_item) == "sword":
                    self.__player.attack(enemy=enemy, camera_offset=self.camera_offset, dt=dt)
            else:
                self.__enemies.remove(enemy)

            if enemy.get_health() <= 0:
                self.__enemies.remove(enemy)
                self.__inventory.add_item(item="slime")

        self.__player.update(chunks=surrounding_chunks, dt=dt)
        self.__player.draw(screen=self.screen, camera_offset=self.camera_offset)
        self.__inventory.update()
        self.__inventory.draw()

    def save_world_to_json(self):
        world_path = os.path.join(WORLD_SAVE_FOLDER, f"{self.__world_name}.json")
        # Convert tuple keys to strings
        serialised_chunks = {}
        for chunk_position, blocks_dict in self.__chunks.items():
            chunk_key = f"{chunk_position[0]};{chunk_position[1]}"
            serialised_chunks[chunk_key] = {}

            for block_position, block in blocks_dict.items():
                block_key = f"{block_position[0]};{block_position[1]}"
                serialised_chunks[chunk_key][block_key] = block
        # Save serialised surrounding_chunks to a JSON file
        with open(world_path, "w") as json_file:
            json.dump(serialised_chunks, json_file)

    def load_world_from_json(self):
        world_path = os.path.join(WORLD_SAVE_FOLDER, f"{self.__world_name}.json")
        if os.path.exists(world_path):

            # Load serialized surrounding_chunks from the JSON file
            with open(world_path, "r") as json_file:
                serialised_chunks = json.load(json_file)
            # Convert string keys back to tuples
            chunks = {}
            for chunk_position, blocks_dict in serialised_chunks.items():
                chunk_position = tuple(map(int, chunk_position.split(";")))
                chunks[chunk_position] = {}

                for block_position, block in blocks_dict.items():
                    block_position = tuple(map(int, block_position.split(";")))
                    chunks[chunk_position][block_position] = block
        else:
            chunks = {}
        return chunks
