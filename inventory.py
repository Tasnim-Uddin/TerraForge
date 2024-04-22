import pygame
import json
import os

from global_constants import *
from all_texture_data import *
from event_manager import EventManager


class Inventory:
    def __init__(self, game, screen, textures):
        self.screen = screen
        self.textures = textures

        self.__inventory_name = game.get_player_name()
        self.__inventory_items = self.load_inventory_from_json()

        self.active_row = 0
        self.active_column = 0
        self.__selected_item = self.__inventory_items[
            (self.active_row, self.active_column)
        ]["item"]

        self.inventory_slot_font = pygame.font.Font(filename=None, size=20)
        self.inventory_quantity_font = pygame.font.Font(filename=None, size=30)

        self.inventory_expanded = False
        self.clicked_slot_position = None
        self.clicked_once = False

        self.crafting_table = False
        self.furnace = False
        self.current_available_recipes = base_crafting_recipes
        self.crafting_menu_opened = False
        self.crafting_selected_index = 0
        self.current_page = 0

        self.menu_surface = pygame.Surface((300, WINDOW_HEIGHT), pygame.SRCALPHA)
        self.menu_surface.fill((100, 100, 100, 128))

        # Create font objects outside the method
        self.title_font = pygame.font.Font(None, 36)
        self.crafting_quantity_font = pygame.font.Font(None, 24)
        self.crafting_sound = pygame.mixer.Sound(file="assets/sound/crafting.mp3")

    def get_selected_item(self):
        return self.__selected_item

    @staticmethod
    def get_item_type(item):
        try:
            return all_texture_data[item]["item_type"]
        except KeyError:
            return None

    def get_item_quantity(self, item):
        total_quantity = 0
        for item_data in self.__inventory_items.values():
            if item_data["item"] == item:
                total_quantity += item_data["quantity"]
        return total_quantity

    def add_item(self, item, quantity=1):
        if all_texture_data[item]["inventory_item"] != "default":
            item = all_texture_data[item]["inventory_item"]

        for item_data in self.__inventory_items.values():
            if item_data["item"] == item:
                item_data["quantity"] += quantity
                return

        for item_data in self.__inventory_items.values():
            if item_data["item"] is None:
                item_data["item"] = item
                item_data["quantity"] = quantity
                return

    def remove_item(self, item, quantity=1):
        for item_data in self.__inventory_items.values():
            if item_data["item"] == item:
                item_data["quantity"] -= quantity
                if item_data["quantity"] <= 0:
                    item_data["item"] = None
                    item_data["quantity"] = None
                    return

    def determine_crafting_table(
        self, player_position, neighbour_chunk_offsets, crafting_table_positions
    ):
        for offset in neighbour_chunk_offsets:
            if offset in crafting_table_positions:
                for position in crafting_table_positions[offset]:
                    distance = int(
                        (
                            (position[0] * BLOCK_SIZE - player_position[0]) ** 2
                            + (position[1] * BLOCK_SIZE - player_position[1]) ** 2
                        )
                        ** 0.5
                    )
                    if distance <= 5 * BLOCK_SIZE:
                        self.crafting_table = True
                        return
        self.crafting_table = False

    def determine_furnace(
        self, player_position, neighbour_chunk_offsets, furnace_positions
    ):
        for offset in neighbour_chunk_offsets:
            if offset in furnace_positions:
                for position in furnace_positions[offset]:
                    distance = int(
                        (
                            (position[0] * BLOCK_SIZE - player_position[0]) ** 2
                            + (position[1] * BLOCK_SIZE - player_position[1]) ** 2
                        )
                        ** 0.5
                    )
                    if distance <= 5 * BLOCK_SIZE:
                        self.furnace = True
                        return
        self.furnace = False

    def update(
        self,
        player_position,
        neighbour_chunk_offsets,
        crafting_table_positions,
        furnace_positions,
    ):
        max_num_recipes_per_page = (WINDOW_HEIGHT - 10) // 60
        total_recipes = len(self.current_available_recipes)
        total_pages = (
            total_recipes + max_num_recipes_per_page - 1
        ) // max_num_recipes_per_page
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.inventory_expanded = not self.inventory_expanded

                    if not self.inventory_expanded:
                        if self.active_row > 0:
                            self.active_row = 0
                            self.active_column = 0

                        self.clicked_slot_position = None
                        self.clicked_once = False

                if event.key == pygame.K_c:
                    self.crafting_menu_opened = not self.crafting_menu_opened

                    if not self.crafting_menu_opened:
                        self.crafting_selected_index = 0

                for key in range(1, COLUMN_SLOTS + 1):
                    if event.key == getattr(pygame, f"K_{key}"):
                        self.active_row = 0
                        self.active_column = key - 1

                if self.crafting_menu_opened:
                    self.determine_crafting_table(
                        player_position=player_position,
                        neighbour_chunk_offsets=neighbour_chunk_offsets,
                        crafting_table_positions=crafting_table_positions,
                    )
                    self.determine_furnace(
                        player_position=player_position,
                        neighbour_chunk_offsets=neighbour_chunk_offsets,
                        furnace_positions=furnace_positions,
                    )

                    if self.crafting_table and not self.furnace:
                        self.current_available_recipes = crafting_table_recipes
                    elif not self.crafting_table and self.furnace:
                        self.current_available_recipes = furnace_smelting_recipes
                    elif self.crafting_table and self.furnace:
                        self.current_available_recipes = all_crafting_recipes
                    else:
                        self.current_available_recipes = base_crafting_recipes

                    if event.key == pygame.K_LEFT:
                        if self.current_page != 0:
                            self.current_page = self.current_page - 1
                            self.crafting_selected_index = (
                                self.current_page * max_num_recipes_per_page
                            )

                    elif event.key == pygame.K_RIGHT:
                        if self.current_page != total_pages - 1:
                            self.current_page = self.current_page + 1
                            self.crafting_selected_index = (
                                self.current_page * max_num_recipes_per_page
                            )

                    if event.key == pygame.K_UP:
                        if (
                            self.crafting_selected_index
                            == self.current_page * max_num_recipes_per_page
                        ):
                            self.crafting_selected_index = min(
                                len(self.current_available_recipes) - 1,
                                (self.current_page + 1) * max_num_recipes_per_page - 1,
                            )
                        else:
                            self.crafting_selected_index -= 1
                    elif event.key == pygame.K_DOWN:
                        start_index = self.current_page * max_num_recipes_per_page
                        end_index = min(
                            start_index + max_num_recipes_per_page, total_recipes
                        )
                        num_recipes_current_page = len(
                            list(self.current_available_recipes.keys())[
                                start_index:end_index
                            ]
                        )
                        if (
                            self.crafting_selected_index
                            == self.current_page * max_num_recipes_per_page
                            + num_recipes_current_page
                            - 1
                        ):
                            self.crafting_selected_index = (
                                self.current_page * max_num_recipes_per_page
                            )
                        else:
                            self.crafting_selected_index += 1

                    start_index = self.current_page * max_num_recipes_per_page
                    end_index = min(
                        start_index + max_num_recipes_per_page, total_recipes
                    )
                    num_recipes_current_page = len(
                        list(self.current_available_recipes.keys())[
                            start_index:end_index
                        ]
                    )

                    if (
                        self.crafting_selected_index
                        > self.current_page * max_num_recipes_per_page
                        + num_recipes_current_page
                        - 1
                    ):
                        self.crafting_selected_index = (
                            self.current_page * max_num_recipes_per_page
                        )

                    if event.key == pygame.K_RETURN:
                        selected_recipe = list(self.current_available_recipes.keys())[
                            self.crafting_selected_index
                        ]
                        self.craft_item(selected_recipe)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.crafting_menu_opened:
                    if event.button == 1:
                        mouse_position = pygame.mouse.get_pos()
                        for index, (recipe_name, recipe) in enumerate(
                            self.current_available_recipes.items()
                        ):
                            recipe_image = self.textures[recipe["output"]["item"]]
                            menu_width = 300
                            menu_x = WINDOW_WIDTH - menu_width
                            menu_y = 60
                            recipe_image_rect = recipe_image.get_rect(
                                topleft=(
                                    menu_x + 20,
                                    menu_y
                                    + 50
                                    + index * (recipe_image.get_height() + 10),
                                )
                            )
                            if recipe_image_rect.collidepoint(mouse_position):
                                max_num_recipes_per_page = (WINDOW_HEIGHT - 10) // 60
                                self.crafting_selected_index = (
                                    index + self.current_page * max_num_recipes_per_page
                                )
                                break
                    elif event.button == 3:
                        mouse_position = pygame.mouse.get_pos()
                        for index, (recipe_name, recipe) in enumerate(
                            self.current_available_recipes.items()
                        ):
                            recipe_image = self.textures[recipe["output"]["item"]]
                            menu_width = 300
                            menu_x = WINDOW_WIDTH - menu_width
                            menu_y = 60
                            recipe_image_rect = recipe_image.get_rect(
                                topleft=(
                                    menu_x + 20,
                                    menu_y
                                    + 50
                                    + index * (recipe_image.get_height() + 10),
                                )
                            )
                            if recipe_image_rect.collidepoint(mouse_position):
                                max_num_recipes_per_page = (WINDOW_HEIGHT - 10) // 60
                                self.crafting_selected_index = (
                                    index + self.current_page * max_num_recipes_per_page
                                )
                                selected_recipe = list(
                                    self.current_available_recipes.keys()
                                )[self.crafting_selected_index]
                                self.craft_item(selected_recipe)
                                break
                    elif event.button == 4:  # Scroll wheel up
                        if (
                            self.crafting_selected_index
                            == self.current_page * max_num_recipes_per_page
                        ):
                            self.crafting_selected_index = min(
                                len(self.current_available_recipes) - 1,
                                (self.current_page + 1) * max_num_recipes_per_page - 1,
                            )
                        else:
                            self.crafting_selected_index -= 1
                    elif event.button == 5:  # Scroll wheel down
                        start_index = self.current_page * max_num_recipes_per_page
                        end_index = min(
                            start_index + max_num_recipes_per_page, total_recipes
                        )
                        num_recipes_current_page = len(
                            list(self.current_available_recipes.keys())[
                                start_index:end_index
                            ]
                        )
                        if (
                            self.crafting_selected_index
                            == self.current_page * max_num_recipes_per_page
                            + num_recipes_current_page
                            - 1
                        ):
                            self.crafting_selected_index = (
                                self.current_page * max_num_recipes_per_page
                            )
                        else:
                            self.crafting_selected_index += 1

                    start_index = self.current_page * max_num_recipes_per_page
                    end_index = min(
                        start_index + max_num_recipes_per_page, total_recipes
                    )
                    num_recipes_current_page = len(
                        list(self.current_available_recipes.keys())[
                            start_index:end_index
                        ]
                    )
                    if (
                        self.crafting_selected_index
                        > self.current_page * max_num_recipes_per_page
                        + num_recipes_current_page
                        - 1
                    ):
                        self.crafting_selected_index = (
                            self.current_page * max_num_recipes_per_page
                        )

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.crafting_menu_opened:
                    if event.button == 4:  # Scroll wheel up
                        self.active_column -= 1
                    elif event.button == 5:  # Scroll wheel down
                        self.active_column += 1

            if event.type == pygame.KEYDOWN:
                if not self.crafting_menu_opened:
                    if event.key == pygame.K_LEFT:
                        self.active_column -= 1
                    elif event.key == pygame.K_RIGHT:
                        self.active_column += 1

            if not self.inventory_expanded:
                if self.active_column > COLUMN_SLOTS - 1:
                    self.active_column = 0
                elif self.active_column < 0:
                    self.active_column = COLUMN_SLOTS - 1
            else:
                if self.active_column > COLUMN_SLOTS - 1:
                    self.active_row += 1
                    if self.active_row > ROW_SLOTS - 1:
                        self.active_row = 0
                    self.active_column = 0
                elif self.active_column < 0:
                    self.active_row -= 1
                    if self.active_row < 0:
                        self.active_row = ROW_SLOTS - 1
                    self.active_column = COLUMN_SLOTS - 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                row_slot_number = mouse_position[1] // (BLOCK_SIZE * 2)
                column_slot_number = mouse_position[0] // (BLOCK_SIZE * 2)

                slot_position = (row_slot_number, column_slot_number)

                if event.button == 1:
                    if not self.inventory_expanded:
                        if (
                            row_slot_number == 0
                            and 0 <= column_slot_number <= COLUMN_SLOTS - 1
                        ):
                            self.active_row = row_slot_number
                            self.active_column = column_slot_number

                if event.button == 3:
                    if not self.inventory_expanded:
                        if (
                            0 <= column_slot_number < COLUMN_SLOTS
                            and row_slot_number == 0
                        ):
                            if not self.clicked_once:
                                self.clicked_slot_position = slot_position
                                self.clicked_once = True
                            else:
                                if slot_position != self.clicked_slot_position:
                                    slot1_key = self.clicked_slot_position
                                    slot2_key = slot_position
                                    (
                                        self.__inventory_items[slot1_key]["item"],
                                        self.__inventory_items[slot2_key]["item"],
                                    ) = (
                                        self.__inventory_items[slot2_key]["item"],
                                        self.__inventory_items[slot1_key]["item"],
                                    )

                                    (
                                        self.__inventory_items[slot1_key]["quantity"],
                                        self.__inventory_items[slot2_key]["quantity"],
                                    ) = (
                                        self.__inventory_items[slot2_key]["quantity"],
                                        self.__inventory_items[slot1_key]["quantity"],
                                    )

                                self.clicked_slot_position = None
                                self.clicked_once = False

                    if self.inventory_expanded:
                        if (
                            0 <= column_slot_number < COLUMN_SLOTS
                            and 0 <= row_slot_number < ROW_SLOTS
                        ):
                            if not self.clicked_once:
                                self.clicked_slot_position = slot_position
                                self.clicked_once = True
                            else:
                                if slot_position != self.clicked_slot_position:
                                    slot1_key = self.clicked_slot_position
                                    slot2_key = slot_position
                                    (
                                        self.__inventory_items[slot1_key]["item"],
                                        self.__inventory_items[slot2_key]["item"],
                                    ) = (
                                        self.__inventory_items[slot2_key]["item"],
                                        self.__inventory_items[slot1_key]["item"],
                                    )

                                    (
                                        self.__inventory_items[slot1_key]["quantity"],
                                        self.__inventory_items[slot2_key]["quantity"],
                                    ) = (
                                        self.__inventory_items[slot2_key]["quantity"],
                                        self.__inventory_items[slot1_key]["quantity"],
                                    )

                                elif slot_position == self.clicked_slot_position:
                                    pass

                                self.clicked_slot_position = None
                                self.clicked_once = False

        try:
            slot_position = (self.active_row, self.active_column)
        except IndexError:
            slot_position = (0, COLUMN_SLOTS - 1)
        self.__selected_item = self.__inventory_items[slot_position]["item"]

    def craft_item(self, recipe_name):
        if recipe_name in self.current_available_recipes:
            recipe = self.current_available_recipes[recipe_name]
            input_information = recipe["input"]
            output_information = recipe["output"]

            # Check if the player has enough input items
            for item, quantity in zip(
                input_information["item"], input_information["quantity"]
            ):
                if self.get_item_quantity(item) < quantity:
                    print(f"You don't have enough {item} to craft {recipe_name}")
                    return

            # Deduct input items from inventory
            for item, quantity in zip(
                input_information["item"], input_information["quantity"]
            ):
                self.remove_item(item=item, quantity=quantity)

            # Add output items to inventory
            self.add_item(
                item=output_information["item"], quantity=output_information["quantity"]
            )
            self.crafting_sound.play()

            print(f"{recipe_name} crafted successfully!")
        else:
            print("Recipe not found")

    def draw_crafting(self):
        menu_x = WINDOW_WIDTH - 300
        menu_y = 60

        if self.crafting_menu_opened:
            self.screen.fblits([(self.menu_surface, (menu_x, menu_y))])
            title_text = self.title_font.render("Crafting Menu", True, (255, 255, 255))
            title_text_rect = title_text.get_rect(center=(menu_x + 150, menu_y + 20))
            self.screen.fblits([(title_text, title_text_rect)])

            max_num_recipes_per_page = (WINDOW_HEIGHT - 10) // 60
            total_recipes = len(self.current_available_recipes)
            total_pages = (
                total_recipes + max_num_recipes_per_page - 1
            ) // max_num_recipes_per_page
            self.current_page = min(self.current_page, total_pages - 1)
            start_index = self.current_page * max_num_recipes_per_page
            end_index = min(start_index + max_num_recipes_per_page, total_recipes)
            current_page_recipes = list(self.current_available_recipes.keys())[
                start_index:end_index
            ]

            recipe_y = menu_y + 50
            for index, recipe_name in enumerate(current_page_recipes):
                recipe = self.current_available_recipes[recipe_name]
                recipe_image = self.textures[recipe["output"]["item"]]
                recipe_image_rect = recipe_image.get_rect(
                    topleft=(menu_x + 20, recipe_y)
                )
                self.screen.fblits([(recipe_image, recipe_image_rect)])

                if index == self.crafting_selected_index - start_index:
                    highlight_rect = pygame.Rect(
                        recipe_image_rect.left - 2,
                        recipe_image_rect.top - 2,
                        recipe_image_rect.width + 4,
                        recipe_image_rect.height + 4,
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), highlight_rect, 2)

                required_items = recipe["input"]
                item_x = recipe_image_rect.right + 20

                for items, quantities in zip(
                    required_items["item"], required_items["quantity"]
                ):
                    quantity_text = self.crafting_quantity_font.render(
                        f"{quantities}", True, (255, 255, 255)
                    )
                    quantity_text_rect = quantity_text.get_rect(
                        left=item_x, centery=recipe_image_rect.centery
                    )
                    self.screen.fblits([(quantity_text, quantity_text_rect)])

                    item_image_surface = self.textures[items]
                    item_image_rect = item_image_surface.get_rect(
                        left=quantity_text_rect.right + 8,
                        centery=recipe_image_rect.centery,
                    )
                    item_image_surface = pygame.transform.scale(
                        item_image_surface,
                        (item_image_rect.height // 1.5, item_image_rect.height // 1.5),
                    )
                    self.screen.fblits([(item_image_surface, item_image_rect)])
                    item_x = item_image_rect.right + 10

                recipe_y += recipe_image.get_height() + 10

            prev_page_text = self.inventory_slot_font.render("<", True, (255, 255, 255))
            prev_page_rect = prev_page_text.get_rect(
                center=(menu_x + 15, menu_y + WINDOW_HEIGHT // 2 + 250)
            )
            pygame.draw.rect(self.screen, (100, 100, 100), prev_page_rect)
            self.screen.fblits([(prev_page_text, prev_page_rect)])

            next_page_text = self.inventory_slot_font.render(">", True, (255, 255, 255))
            next_page_rect = next_page_text.get_rect(
                center=(menu_x + 285, menu_y + WINDOW_HEIGHT // 2 + 250)
            )
            pygame.draw.rect(self.screen, (100, 100, 100), next_page_rect)
            self.screen.fblits([(next_page_text, next_page_rect)])

    def draw(self):
        pygame.draw.rect(
            surface=self.screen,
            color="#4444a4",
            rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS, BLOCK_SIZE * 2),
        )  # Draw inventory background
        if self.inventory_expanded:
            for row in range(1, ROW_SLOTS):
                pygame.draw.rect(
                    surface=self.screen,
                    color="#4444a4",
                    rect=pygame.Rect(
                        0,
                        row * BLOCK_SIZE * 2,
                        (BLOCK_SIZE * 2) * COLUMN_SLOTS,
                        BLOCK_SIZE * 2,
                    ),
                )  # Draw inventory background

        padding_x = BLOCK_SIZE // 2
        padding_y = BLOCK_SIZE // 2

        for slot_position, item_data in self.__inventory_items.items():
            true_item_row_slot_number = slot_position[0]

            row_slot_number = 0
            if self.inventory_expanded:
                row_slot_number = slot_position[0]

            column_slot_number = slot_position[1]

            # Highlight the selected slot
            if true_item_row_slot_number == 0 or (
                true_item_row_slot_number != 0 and self.inventory_expanded
            ):
                if slot_position == (self.active_row, self.active_column):
                    pygame.draw.rect(
                        surface=self.screen,
                        color="#fcec24",
                        rect=pygame.Rect(
                            column_slot_number * BLOCK_SIZE * 2,
                            row_slot_number * BLOCK_SIZE * 2,
                            BLOCK_SIZE * 2,
                            BLOCK_SIZE * 2,
                        ),
                    )

            # Highlight the slots that are about to be switched
            if true_item_row_slot_number == 0 or (
                true_item_row_slot_number != 0 and self.inventory_expanded
            ):
                if self.clicked_once:
                    if (
                        slot_position == self.clicked_slot_position
                    ):
                        pygame.draw.rect(
                            surface=self.screen,
                            color="#6ffc03",
                            rect=pygame.Rect(
                                column_slot_number * BLOCK_SIZE * 2,
                                row_slot_number * BLOCK_SIZE * 2,
                                BLOCK_SIZE * 2,
                                BLOCK_SIZE * 2,
                            ),
                        )

            pygame.draw.rect(
                surface=self.screen,
                color="black",
                rect=pygame.Rect(
                    column_slot_number * BLOCK_SIZE * 2,
                    row_slot_number * BLOCK_SIZE * 2,
                    BLOCK_SIZE * 2,
                    BLOCK_SIZE * 2,
                ),
                width=1,
            )  # Draw border

            if item_data["item"] is not None:
                if true_item_row_slot_number == 0 or (
                    true_item_row_slot_number != 0 and self.inventory_expanded
                ):
                    self.screen.fblits(
                        [
                            (
                                pygame.transform.scale(
                                    surface=self.textures[item_data["item"]],
                                    size=(BLOCK_SIZE, BLOCK_SIZE),
                                ),
                                (
                                    padding_x + (BLOCK_SIZE * 2) * column_slot_number,
                                    padding_y
                                    + (BLOCK_SIZE * 2) * true_item_row_slot_number,
                                ),
                            )
                        ]
                    )

                    quantity_text = self.inventory_quantity_font.render(
                        text=str(item_data["quantity"]), antialias=True, color="white"
                    )
                    self.screen.fblits(
                        [
                            (
                                quantity_text,
                                (
                                    (BLOCK_SIZE * 2) * column_slot_number + 10,
                                    (BLOCK_SIZE * 2) * true_item_row_slot_number + 40,
                                ),
                            )
                        ]
                    )

        if not self.inventory_expanded:
            pygame.draw.rect(
                surface=self.screen,
                color="black",
                rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS, BLOCK_SIZE * 2),
                width=2,
            )

        if self.inventory_expanded:
            pygame.draw.rect(
                surface=self.screen,
                color="black",
                rect=pygame.Rect(
                    0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS, (BLOCK_SIZE * 2) * ROW_SLOTS
                ),
                width=2,
            )

        for column_slot_number in range(1, COLUMN_SLOTS + 1):
            slot_text = self.inventory_slot_font.render(
                text=str(column_slot_number), antialias=True, color="#c0c2c0"
            )
            self.screen.fblits(
                [(slot_text, ((BLOCK_SIZE * 2) * (column_slot_number - 1) + 5, 5))]
            )

    def save_inventory_to_json(self):
        inventory_path = os.path.join(
            PLAYER_SAVE_FOLDER, f"{self.__inventory_name}.json"
        )
        # Convert tuple keys to string representations
        serialised_inventory = {}
        for slot_position, slot in self.__inventory_items.items():
            serialised_inventory[f"{slot_position[0]};{slot_position[1]}"] = slot
        # Save serialised inventory to a JSON file
        with open(inventory_path, "w") as json_file:
            json.dump(serialised_inventory, json_file)

    def load_inventory_from_json(self):
        inventory_path = os.path.join(
            PLAYER_SAVE_FOLDER, f"{self.__inventory_name}.json"
        )
        if os.path.exists(inventory_path):
            # Load serialised inventory from the JSON file
            with open(inventory_path, "r") as json_file:
                serialised_inventory = json.load(json_file)
            # Convert string keys back to tuples
            inventory_items = {}
            for slot_position, slot in serialised_inventory.items():
                slot_position = tuple(map(int, slot_position.split(";")))
                inventory_items[slot_position] = slot
        else:
            inventory_items = {}
            for row in range(ROW_SLOTS):
                for column in range(COLUMN_SLOTS):
                    position = (row, column)
                    inventory_items[position] = {"item": None, "quantity": None}

            inventory_items[(0, 0)]["item"], inventory_items[(0, 0)]["quantity"] = (
                "copper_sword",
                1,
            )
            inventory_items[(0, 1)]["item"], inventory_items[(0, 1)]["quantity"] = (
                "copper_pickaxe",
                1,
            )
            inventory_items[(0, 2)]["item"], inventory_items[(0, 2)]["quantity"] = (
                "copper_axe",
                1,
            )

        return inventory_items
