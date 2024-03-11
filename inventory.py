import pygame
import json
import os

from global_constants import *
from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self, screen, textures, inventory_name):
        self.screen = screen
        self.textures = textures

        self.inventory_items = self.load_inventory_from_json(inventory_name=inventory_name)

        self.active_row = 0
        self.active_column = 0
        self.selected_item = self.inventory_items[(self.active_row, self.active_column)]["item"]

        self.slot_font = pygame.font.Font(filename=None, size=20)
        self.quantity_font = pygame.font.Font(filename=None, size=30)

        self.inventory_expanded = False
        self.clicked_slot_position = None
        self.clicked_once = False

    def get_selected_item(self):
        return self.selected_item

    def add_item(self, item):
        for item_data in self.inventory_items.values():
            if item_data["item"] == item:
                item_data["quantity"] += 1
                return

        for item_data in self.inventory_items.values():
            if item_data["item"] is None:
                item_data["item"] = item
                item_data["quantity"] = 1
                return

    def remove_item(self, item):
        for item_data in self.inventory_items.values():
            if item_data["item"] == item:
                item_data["quantity"] -= 1
                if item_data["quantity"] <= 0:
                    item_data["item"] = None
                    item_data["quantity"] = None
                    return

    @staticmethod
    def item_type(item):
        try:
            return all_texture_data[item]["item_type"]
        except KeyError:
            return None

    def update(self):
        for event in EventManager.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.inventory_expanded = not self.inventory_expanded

                    if not self.inventory_expanded:
                        self.active_row = 0
                        self.active_column = 0

                        self.clicked_slot_position = None
                        self.clicked_once = False

            if event.type == pygame.KEYDOWN:
                for key in range(1, COLUMN_SLOTS + 1):
                    if event.key == getattr(pygame, f"K_{key}"):
                        self.active_row = 0
                        self.active_column = key - 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll wheel up
                    self.active_column -= 1
                elif event.button == 5:  # Scroll wheel down
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = pygame.mouse.get_pos()
                row_slot_number = mouse_position[1] // (BLOCK_SIZE * 2)
                column_slot_number = mouse_position[0] // (BLOCK_SIZE * 2)

                slot_position = (row_slot_number, column_slot_number)

                if not self.inventory_expanded:
                    if 0 <= column_slot_number < COLUMN_SLOTS and row_slot_number == 0:
                        if not self.clicked_once:
                            self.clicked_slot_position = slot_position
                            self.clicked_once = True
                        else:
                            if slot_position != self.clicked_slot_position:
                                slot1_key = self.clicked_slot_position
                                slot2_key = slot_position
                                self.inventory_items[slot1_key]["item"], self.inventory_items[slot2_key]["item"] = \
                                    self.inventory_items[slot2_key]["item"], self.inventory_items[slot1_key]["item"]

                                self.inventory_items[slot1_key]["quantity"], self.inventory_items[slot2_key]["quantity"] = \
                                    self.inventory_items[slot2_key]["quantity"], self.inventory_items[slot1_key]["quantity"]

                            self.clicked_slot_position = None
                            self.clicked_once = False

                if self.inventory_expanded:
                    if 0 <= column_slot_number < COLUMN_SLOTS and 0 <= row_slot_number < 3:
                        if not self.clicked_once:
                            self.clicked_slot_position = slot_position
                            self.clicked_once = True
                        else:
                            if slot_position != self.clicked_slot_position:
                                slot1_key = self.clicked_slot_position
                                slot2_key = slot_position
                                self.inventory_items[slot1_key]["item"], self.inventory_items[slot2_key]["item"] = \
                                    self.inventory_items[slot2_key]["item"], self.inventory_items[slot1_key]["item"]

                                self.inventory_items[slot1_key]["quantity"], self.inventory_items[slot2_key]["quantity"] = \
                                    self.inventory_items[slot2_key]["quantity"], self.inventory_items[slot1_key]["quantity"]

                            elif slot_position == self.clicked_slot_position:
                                pass

                            self.clicked_slot_position = None
                            self.clicked_once = False

        try:
            slot_position = (self.active_row, self.active_column)
        except IndexError:
            slot_position = (0, COLUMN_SLOTS - 1)
        self.selected_item = self.inventory_items[slot_position]["item"]

    def draw(self):
        pygame.draw.rect(surface=self.screen, color="#4444a4",
                         rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS,
                                          BLOCK_SIZE * 2))  # Draw inventory background
        if self.inventory_expanded:
            for row in range(1, 3):
                pygame.draw.rect(surface=self.screen, color="#4444a4",
                                 rect=pygame.Rect(0, row * BLOCK_SIZE * 2, (BLOCK_SIZE * 2) * COLUMN_SLOTS,
                                                  BLOCK_SIZE * 2))  # Draw inventory background

        padding_x = BLOCK_SIZE // 2
        padding_y = BLOCK_SIZE // 2

        for slot_position, item_data in self.inventory_items.items():
            true_item_row_slot_number = slot_position[0]

            row_slot_number = 0
            if self.inventory_expanded:
                row_slot_number = slot_position[0]

            column_slot_number = slot_position[1]

            # Highlight the selected slot
            if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                if slot_position == (self.active_row, self.active_column):
                    pygame.draw.rect(surface=self.screen, color="#fcec24",
                                     rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2,
                                                      row_slot_number * BLOCK_SIZE * 2, BLOCK_SIZE * 2, BLOCK_SIZE * 2))

            # Highlight the slots that are about to be switched
            if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                if self.clicked_once:
                    if slot_position == self.clicked_slot_position:  # or slot_number == self.active_slot:
                        pygame.draw.rect(surface=self.screen, color="white",
                                         rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2,
                                                          row_slot_number * BLOCK_SIZE * 2, BLOCK_SIZE * 2,
                                                          BLOCK_SIZE * 2))

            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2, row_slot_number * BLOCK_SIZE * 2,
                                              BLOCK_SIZE * 2, BLOCK_SIZE * 2),
                             width=1)  # Draw border

            if item_data["item"] is not None:
                if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                    self.screen.blit(
                        source=pygame.transform.scale(surface=self.textures[item_data["item"]], size=(BLOCK_SIZE, BLOCK_SIZE)),
                        dest=(padding_x + (BLOCK_SIZE * 2) * column_slot_number,
                         padding_y + (BLOCK_SIZE * 2) * true_item_row_slot_number))

                    quantity_text = self.quantity_font.render(text=str(item_data["quantity"]), antialias=True,
                                                              color="white")
                    self.screen.blit(source=quantity_text, dest=(
                        (BLOCK_SIZE * 2) * column_slot_number + 20, (BLOCK_SIZE * 2) * true_item_row_slot_number + 40))

        if not self.inventory_expanded:
            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS, BLOCK_SIZE * 2),
                             width=2)
            for column_slot_number in range(1, COLUMN_SLOTS + 1):
                slot_text = self.slot_font.render(text=str(column_slot_number), antialias=True, color="#c0c2c0")
                self.screen.blit(source=slot_text, dest=(
                    (BLOCK_SIZE * 2) * column_slot_number + 5, (BLOCK_SIZE * 2) * 1 + 5))

        if self.inventory_expanded:
            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * COLUMN_SLOTS, (BLOCK_SIZE * 2) * 3),
                             width=2)

    def get_inventory_to_save(self):
        saved_inventory = {}
        for slot_position in self.inventory_items:
            json_slot_position = ";".join(map(str, slot_position))  # Convert tuple to string
            saved_inventory[json_slot_position] = self.inventory_items[slot_position]
        return saved_inventory

    def save_inventory_to_json(self, inventory_name):
        inventory_path = os.path.join(PLAYER_SAVE_FOLDER, f"{inventory_name}.json")
        # Convert tuple keys to string representations
        serialised_inventory = {f"{slot_position[0]};{slot_position[1]}": slot for slot_position, slot in self.inventory_items.items()}
        # Save serialised inventory to a JSON file
        with open(inventory_path, "w") as json_file:
            json.dump(serialised_inventory, json_file)

    @staticmethod
    def load_inventory_from_json(inventory_name):
        inventory_path = os.path.join(PLAYER_SAVE_FOLDER, f"{inventory_name}.json")
        if os.path.exists(inventory_path):
            # Load serialised inventory from the JSON file
            with open(inventory_path, "r") as json_file:
                serialised_inventory = json.load(json_file)
            # Convert string keys back to tuples
            inventory_items = {tuple(map(int, slot_position.split(";"))): slot for slot_position, slot in serialised_inventory.items()}
        else:
            inventory_items = {(row, column): {"item": None, "quantity": None} for row in range(ROW_SLOTS) for column in range(COLUMN_SLOTS)}

            inventory_items[(0, 0)]["item"], inventory_items[(0, 0)]["quantity"] = "copper_sword", 1
            inventory_items[(0, 1)]["item"], inventory_items[(0, 1)]["quantity"] = "copper_pickaxe", 1
            inventory_items[(0, 2)]["item"], inventory_items[(0, 2)]["quantity"] = "copper_axe", 1

        return inventory_items
