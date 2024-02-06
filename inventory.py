import pygame
import re

from global_constants import *
from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self, screen, textures):
        self.screen = screen
        self.textures = textures

        self.inventory_items = {}

        for row in range(3):
            for column in range(9):
                key = f"{row};{column}"
                self.inventory_items[key] = {"item": None, "quantity": None}

        self.inventory_items["0;0"]["item"], self.inventory_items["0;0"]["quantity"] = "sword", 1
        self.inventory_items["0;1"]["item"], self.inventory_items["0;1"]["quantity"] = "pickaxe", 1
        self.inventory_items["0;2"]["item"], self.inventory_items["0;2"]["quantity"] = "axe", 1

        self.column_slots = 9
        self.row_slots = 3

        self.active_row = 0
        self.active_column = 0
        self.selected_item = self.inventory_items[f"{self.active_row};{self.active_column}"]["item"]

        self.font = pygame.font.Font(filename=None, size=30)

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
    def is_block(item):
        try:
            if all_texture_data[item]["type"] == "block":
                return True
            else:
                return False
        except KeyError:
            return False

    def update(self):
        if EventManager.keydown(key=pygame.K_e):
            self.inventory_expanded = not self.inventory_expanded

            if not self.inventory_expanded:
                self.active_row = 0
                self.active_column = 0

        for i in range(1, 10):  # Check keys 1 to 9
            if EventManager.keydown(pygame.K_0 + i):
                self.active_row = 0
                self.active_column = i - 1

        if EventManager.scroll_wheel_up():
            self.active_column -= 1
        if EventManager.scroll_wheel_down():
            self.active_column += 1

        if not self.inventory_expanded:
            if self.active_column > self.column_slots - 1:
                self.active_column = 0
            elif self.active_column < 0:
                self.active_column = self.column_slots - 1

        if self.inventory_expanded:
            if self.active_column > self.column_slots - 1:
                self.active_row += 1
                if self.active_row > self.row_slots - 1:
                    self.active_row = 0
                self.active_column = 0
            elif self.active_column < 0:
                self.active_row -= 1
                if self.active_row < 0:
                    self.active_row = self.row_slots - 1
                self.active_column = self.column_slots - 1

        if EventManager.left_mouse_click():
            mouse_position = pygame.mouse.get_pos()
            row_slot_number = mouse_position[1] // (BLOCK_SIZE * 2)
            column_slot_number = mouse_position[0] // (BLOCK_SIZE * 2)

            slot_position = f"{row_slot_number};{column_slot_number}"

            if not self.inventory_expanded:
                if 0 <= column_slot_number < self.column_slots and row_slot_number == 0:
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
                if 0 <= column_slot_number < self.column_slots and 0 <= row_slot_number < 3:
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
            slot_position = f"{self.active_row};{self.active_column}"
        except IndexError:
            slot_position = f"0;{self.column_slots - 1}"
        self.selected_item = self.inventory_items[slot_position]["item"]

    def draw(self):
        pygame.draw.rect(surface=self.screen, color="#4444a4",
                         rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * self.column_slots,
                                          BLOCK_SIZE * 2))  # Draw inventory background
        if self.inventory_expanded:
            for row in range(1, 3):
                pygame.draw.rect(surface=self.screen, color="#4444a4",
                                 rect=pygame.Rect(0, row * BLOCK_SIZE * 2, (BLOCK_SIZE * 2) * self.column_slots,
                                                  BLOCK_SIZE * 2))  # Draw inventory background

        padding_x = BLOCK_SIZE // 2
        padding_y = BLOCK_SIZE // 2

        for slot_position, item_data in self.inventory_items.items():
            true_item_row_slot_number = int(re.split(r';', slot_position)[0])

            row_slot_number = 0
            if self.inventory_expanded:
                row_slot_number = int(re.split(r';', slot_position)[0])

            column_slot_number = int(re.split(r';', slot_position)[1])

            # highlight the selected slot
            if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                if slot_position == f"{self.active_row};{self.active_column}":
                    pygame.draw.rect(surface=self.screen, color="#fcec24",
                                     rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2, row_slot_number * BLOCK_SIZE * 2, BLOCK_SIZE * 2, BLOCK_SIZE * 2))


            # highlight the slots that are about to be switched
            if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                if self.clicked_once:
                    if slot_position == self.clicked_slot_position:  # or slot_number == self.active_slot:
                        pygame.draw.rect(surface=self.screen, color="white",
                                         rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2, row_slot_number * BLOCK_SIZE * 2, BLOCK_SIZE * 2, BLOCK_SIZE * 2))


            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(column_slot_number * BLOCK_SIZE * 2, row_slot_number * BLOCK_SIZE * 2, BLOCK_SIZE * 2, BLOCK_SIZE * 2),
                             width=1)  # draw border

            if item_data["item"] is not None:
                if true_item_row_slot_number == 0 or (true_item_row_slot_number != 0 and self.inventory_expanded):
                    self.screen.blit(
                        pygame.transform.scale(surface=self.textures[item_data["item"]], size=(BLOCK_SIZE, BLOCK_SIZE)),
                        (padding_x + (BLOCK_SIZE * 2) * column_slot_number, padding_y + (BLOCK_SIZE * 2) * true_item_row_slot_number))
                    quantity_text = self.font.render(text=str(item_data["quantity"]), antialias=True, color="#fc0015")
                    self.screen.blit(quantity_text, ((BLOCK_SIZE * 2) * column_slot_number + 5, (BLOCK_SIZE * 2) * true_item_row_slot_number + 5))
                # elif true_item_row_slot_number != 0 and not self.inventory_expanded:
                #     pass


        # adds extra border around inventory so thickness is same across all slots and edges
        if not self.inventory_expanded:
            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * self.column_slots, BLOCK_SIZE * 2),
                             width=2)
        if self.inventory_expanded:
            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * self.column_slots, (BLOCK_SIZE * 2) * 3),
                             width=2)
