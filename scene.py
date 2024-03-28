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
        self.torch_positions = {}
        self.crafting_table_positions = {}
        self.furnace_positions = {}

        self.__inventory = Inventory(game=game, screen=self.screen, textures=self.all_textures)

        self.precise_camera_offset = [0, 0]
        self.camera_offset = [0, 0]

        self.surface_seed = OpenSimplex(random.randint(0, 99999999))

        self.lower_cave_threshold = 0.015
        self.upper_cave_threshold = 0.7

        self.__player = Player()

        self.__enemies = []

        self.block_sound = pygame.mixer.Sound(file="assets/sound/block.mp3")


    def get_player(self):
        return self.__player

    def get_inventory(self):
        return self.__inventory

    def __spawn_enemy(self):
        # enemies_around_player = random.randint(1, 4)
        player_chunk_x = int(self.__player.get_x() // (CHUNK_WIDTH * BLOCK_SIZE))
        # for _ in range(enemies_around_player):
        chunk_x_random = random.choice([-1, 1])
        for chunk in self.__chunks:
            if chunk[0] == chunk_x_random + player_chunk_x:
                possible_enemy_positions = []
                for block_position in self.__chunks[chunk]:
                    if self.__chunks[chunk][block_position] == "grass":
                        possible_enemy_positions.append((block_position[0] * BLOCK_SIZE, (block_position[1] - 1) * BLOCK_SIZE))
                if len(possible_enemy_positions) != 0:
                    enemy_position = random.choice(possible_enemy_positions)
                    enemy = SlimeEnemy()
                    enemy.set_x(x=enemy_position[0])
                    enemy.set_y(y=enemy_position[1])
                    self.__enemies.append(enemy)
                    return
    @staticmethod
    def load_textures():
        textures = {}
        atlas = pygame.image.load(file="assets/textures/texture_atlas.png").convert_alpha()

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
                        if random.random() < 0.07:
                            x_shift_start = -2
                            x_shift_end = 2
                            for y_shift_up in range(1, 7):  # Number of layers of tree (bottom to top)
                                if y_shift_up < 4:
                                    if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                        tree_key = (key[0], key[1] - 1)
                                        if tree_key not in self.missing_tree_positions:
                                            self.missing_tree_positions[tree_key] = {}
                                        self.missing_tree_positions[tree_key][
                                            (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_log"
                                    else:
                                        self.__chunks[key][
                                            (int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_log"
                                else:
                                    for x_shift in range(x_shift_start, x_shift_end + 1):
                                        if int(real_x / BLOCK_SIZE) + x_shift < key[0] * CHUNK_WIDTH:
                                            tree_key = (key[0] - 1, key[1])
                                            if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                                tree_key = (key[0] - 1, key[1] - 1)
                                            if tree_key not in self.missing_tree_positions:
                                                self.missing_tree_positions[tree_key] = {}
                                            self.missing_tree_positions[tree_key][
                                                (int(real_x / BLOCK_SIZE) + x_shift,
                                                 int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                        elif int(real_x / BLOCK_SIZE) + x_shift >= (key[0] + 1) * CHUNK_WIDTH:
                                            tree_key = (key[0] + 1, key[1])
                                            if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                                tree_key = (key[0] + 1, key[1] - 1)
                                            if tree_key not in self.missing_tree_positions:
                                                self.missing_tree_positions[tree_key] = {}
                                            self.missing_tree_positions[tree_key][
                                                (int(real_x / BLOCK_SIZE) + x_shift,
                                                 int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                        else:
                                            tree_key = key
                                            try:
                                                if int(real_y / BLOCK_SIZE) - y_shift_up < key[1] * CHUNK_HEIGHT:
                                                    tree_key = (key[0], key[1] - 1)
                                                self.__chunks[tree_key][
                                                    (int(real_x / BLOCK_SIZE) + x_shift,
                                                     int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"
                                            except KeyError:
                                                if tree_key not in self.missing_tree_positions:
                                                    self.missing_tree_positions[tree_key] = {}
                                                self.missing_tree_positions[tree_key][
                                                    (int(real_x / BLOCK_SIZE) + x_shift,
                                                     int(real_y / BLOCK_SIZE) - y_shift_up)] = "tree_leaf"

                                    x_shift_start += 1
                                    x_shift_end -= 1
                    elif DIRT_LEVEL < (real_y + height_noise) <= CAVE_LEVEL * BLOCK_SIZE:
                        self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "dirt"
                    elif CAVE_LEVEL * BLOCK_SIZE < (real_y + height_noise) <= DEEP_CAVE_LEVEL * BLOCK_SIZE:
                        if not air_in_cave:
                            if COAL_LEVEL * BLOCK_SIZE < (real_y + height_noise) and random.random() < COAL_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "coal_ore"
                            elif IRON_LEVEL * BLOCK_SIZE < (real_y + height_noise) and random.random() < IRON_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "iron_ore"
                            elif GOLD_LEVEL * BLOCK_SIZE < (real_y + height_noise) and random.random() < GOLD_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "gold_ore"
                            elif DIAMOND_LEVEL * BLOCK_SIZE < (real_y + height_noise) and random.random() < DIAMOND_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "diamond_ore"
                            else:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "stone"
                    elif DEEP_CAVE_LEVEL * BLOCK_SIZE < (real_y + height_noise):
                        if not air_in_cave:
                            if random.random() < COAL_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "deepslate_coal_ore"
                            elif random.random() < IRON_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "deepslate_iron_ore"
                            elif random.random() < GOLD_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "deepslate_gold_ore"
                            elif random.random() < DIAMOND_SPAWN_RATE:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "deepslate_diamond_ore"
                            else:
                                self.__chunks[key][(int(real_x / BLOCK_SIZE), int(real_y / BLOCK_SIZE))] = "deepslate"

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
            breaking_item_type = self.__inventory.get_item_type(item=breaking_item)
            held_item_type = self.__inventory.get_item_type(item=held_item)
            if within_reach:
                if breaking_item == "tree_leaf":
                    self.__inventory.add_item(item=breaking_item)
                    del self.__chunks[break_chunk_position][break_block_position]
                    self.block_sound.set_volume(0.5)
                    self.block_sound.play()
                    if random.random() < 0.05:
                        self.__inventory.add_item(item="apple")
                if held_item_type == "pickaxe" and (breaking_item_type == "block" or breaking_item_type == "wallpaper") and breaking_item != "tree_log" and breaking_item != "leaf_block":
                    self.__inventory.add_item(item=breaking_item)
                    del self.__chunks[break_chunk_position][break_block_position]
                    self.block_sound.set_volume(0.5)
                    self.block_sound.play()
                    if breaking_item == "torch":
                        self.torch_positions[break_chunk_position].remove(break_block_position)
                    elif breaking_item == "crafting_table":
                        self.crafting_table_positions[break_chunk_position].remove(break_block_position)
                    elif breaking_item == "furnace":
                        self.furnace_positions[break_chunk_position].remove(break_block_position)
                elif held_item_type == "axe" and breaking_item == "tree_log":
                    self.__inventory.add_item(item=breaking_item)
                    del self.__chunks[break_chunk_position][break_block_position]
                    self.block_sound.set_volume(0.5)
                    self.block_sound.play()
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

        # block_exists = True
        # if place_chunk_position in self.__chunks:
        #     if place_block_position in self.__chunks[place_chunk_position]:
        #         if self.__inventory.get_item_type(item=self.__chunks[place_chunk_position][place_block_position]) == "wallpaper":
        #             block_exists = False
        #     else:
        #         block_exists = False
        # else:
        #     block_exists = False


        # To make sure that the block cannot be placed within the block grid a player is on
        player_max_right = math.ceil(self.__player.get_rect().right / BLOCK_SIZE) * BLOCK_SIZE
        player_min_left = (self.__player.get_rect().left // BLOCK_SIZE) * BLOCK_SIZE
        player_min_top = (self.__player.get_rect().top // BLOCK_SIZE) * BLOCK_SIZE
        player_max_bottom = math.ceil(self.__player.get_rect().bottom / BLOCK_SIZE) * BLOCK_SIZE
        player_block_rect = pygame.Rect(player_min_left, player_min_top, player_max_right - player_min_left,
                                        player_max_bottom - player_min_top)

        if not block_exists  and within_reach and not player_block_rect.collidepoint(mouse_position[0] + self.camera_offset[0],mouse_position[1] + self.camera_offset[1]):
            self.block_sound.set_volume(0.5)
            self.block_sound.play()
            self.__chunks[place_chunk_position][place_block_position] = held_item
            self.__inventory.remove_item(item=held_item)
            if held_item == "torch":
                if place_chunk_position not in self.torch_positions:
                    self.torch_positions[place_chunk_position] = []
                self.torch_positions[place_chunk_position].append(place_block_position)
            elif held_item == "crafting_table":
                if place_chunk_position not in self.crafting_table_positions:
                    self.crafting_table_positions[place_chunk_position] = []
                self.crafting_table_positions[place_chunk_position].append(place_block_position)
            elif held_item == "furnace":
                if place_chunk_position not in self.furnace_positions:
                    self.furnace_positions[place_chunk_position] = []
                self.furnace_positions[place_chunk_position].append(place_block_position)

    def update_draw(self, dt):
        self.precise_camera_offset[0] += (self.__player.get_rect().centerx - self.precise_camera_offset[
            0] - WINDOW_WIDTH / 2) / HORIZONTAL_SCROLL_DELAY_FACTOR
        self.precise_camera_offset[1] += (self.__player.get_rect().centery - self.precise_camera_offset[
            1] - WINDOW_HEIGHT / 2) / VERTICAL_SCROLL_DELAY_FACTOR

        self.camera_offset[0] = int(self.precise_camera_offset[0])
        self.camera_offset[1] = int(self.precise_camera_offset[1])

        # Sky colour
        if int(self.__player.get_y()) <= 60 * BLOCK_SIZE:
            self.screen.fill("skyblue")
        elif 60 * BLOCK_SIZE < int(self.__player.get_y()) <= 200 * BLOCK_SIZE:
            self.screen.fill("#2c2c3c")
        elif 200 * BLOCK_SIZE < int(self.__player.get_y()) <= DEEP_CAVE_LEVEL * BLOCK_SIZE:
            self.screen.fill("#0c0c1c")
        else:
            self.screen.fill("black")

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
                if chunk_position in self.__chunks:
                    self.__chunks[chunk_position][position] = tree_block
                    surrounding_chunks[(chunk_position[0], chunk_position[1])] = self.__chunks.get((chunk_position[0], chunk_position[1]), [])
                    self.screen.fblits([(self.all_textures[tree_block], (
                    position[0] * BLOCK_SIZE - self.camera_offset[0],
                    position[1] * BLOCK_SIZE - self.camera_offset[1]))])
                    del self.missing_tree_positions[chunk_position][position]

        for offset in neighbour_chunk_offsets:
            for block_position, block in surrounding_chunks[(offset[0], offset[1])].items():
                if block == "torch":
                    if offset not in self.torch_positions:
                        self.torch_positions[offset] = []
                    if block_position not in self.torch_positions[offset]:
                        self.torch_positions[offset].append(block_position)
                    self.screen.fblits([(self.all_textures[block],
                                         (block_position[0] * BLOCK_SIZE -
                                          self.camera_offset[0],
                                          block_position[1] * BLOCK_SIZE -
                                          self.camera_offset[1]))])
                if block == "crafting_table":
                    if offset not in self.crafting_table_positions:
                        self.crafting_table_positions[offset] = []
                    if block_position not in self.crafting_table_positions[offset]:
                        self.crafting_table_positions[offset].append(block_position)
                if block == "furnace":
                    if offset not in self.furnace_positions:
                        self.furnace_positions[offset] = []
                    if block_position not in self.furnace_positions[offset]:
                        self.furnace_positions[offset].append(block_position)
                distance = int(((block_position[0] * BLOCK_SIZE - int(self.__player.get_x()))**2 + (block_position[1] * BLOCK_SIZE - int(self.__player.get_y()))**2)**0.5)
                if int(self.__player.get_y()) <= 200 * BLOCK_SIZE:
                    self.screen.fblits([(self.all_textures[block],
                                         (block_position[0] * BLOCK_SIZE -
                                          self.camera_offset[0],
                                          block_position[1] * BLOCK_SIZE -
                                          self.camera_offset[1]))])
                if offset in self.torch_positions:
                    for torch_position in self.torch_positions[offset]:
                        torch_distance = int(((torch_position[0] * BLOCK_SIZE - block_position[0] * BLOCK_SIZE)**2 + (torch_position[1] * BLOCK_SIZE - block_position[1] * BLOCK_SIZE)**2)**0.5)
                        if torch_distance <= 7 * BLOCK_SIZE:
                            self.screen.fblits([(self.all_textures[block],
                                                 (block_position[0] * BLOCK_SIZE -
                                                  self.camera_offset[0],
                                                  block_position[1] * BLOCK_SIZE -
                                                  self.camera_offset[1]))])
                if 200 * BLOCK_SIZE < int(self.__player.get_y()) <= DEEP_CAVE_LEVEL * BLOCK_SIZE and (distance <= 11 * BLOCK_SIZE or (self.__inventory.get_selected_item() == "torch" and distance <= 14 * BLOCK_SIZE)):
                    self.screen.fblits([(self.all_textures[block],
                                         (block_position[0] * BLOCK_SIZE -
                                          self.camera_offset[0],
                                          block_position[1] * BLOCK_SIZE -
                                          self.camera_offset[1]))])
                elif DEEP_CAVE_LEVEL * BLOCK_SIZE < int(self.__player.get_y()) and (distance <= 7 * BLOCK_SIZE or (self.__inventory.get_selected_item() == "torch" and distance <= 10 * BLOCK_SIZE)):
                    self.screen.fblits([(self.all_textures[block],
                                         (block_position[0] * BLOCK_SIZE -
                                          self.camera_offset[0],
                                          block_position[1] * BLOCK_SIZE -
                                          self.camera_offset[1]))])

        held_item = self.__inventory.get_selected_item()

        for event in EventManager.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left mouse click
                    if self.__inventory.get_item_type(item=held_item) == "sword":
                        sword_swing_sound = pygame.mixer.Sound(file="assets/sound/sword_swing.mp3")
                        sword_swing_sound.set_volume(0.2)
                        sword_swing_sound.play()
                    else:
                        self.__break_block(held_item=held_item)

                if event.button == 3:  # right mouse click
                    if self.__inventory.get_item_type(item=held_item) == "block" or self.__inventory.get_item_type(item=held_item) == "wallpaper":
                        self.__place_block(held_item=held_item)
                    if self.__inventory.get_item_type(item=held_item) == "food" and self.__player.get_health() < 100:
                        eat_sound = pygame.mixer.Sound(file="assets/sound/eat.mp3")
                        eat_sound.set_volume(0.5)
                        eat_sound.play()
                        self.__player.set_health(health=self.__player.get_health() + 5)
                        self.__inventory.remove_item(item=held_item)

        if random.random() < 0.01 and len(self.__enemies) < 1:
            self.__spawn_enemy()

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
        self.__inventory.update(player=self.__player, neighbour_chunk_offsets=neighbour_chunk_offsets, crafting_table_positions=self.crafting_table_positions, furnace_positions=self.furnace_positions)
        self.__inventory.draw()
        # self.__inventory.update_crafting()
        self.__inventory.draw_crafting()

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
