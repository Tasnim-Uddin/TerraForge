import pygame
import re

from global_constants import *
from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self, screen, textures):
        self.screen = screen
        self.textures = textures

        self.inventory_items = {
            "slot0": {"item": "sword", "quantity": 1},
            "slot1": {"item": "pickaxe", "quantity": 1},
            "slot2": {"item": "axe", "quantity": 1},
            "slot3": {"item": None, "quantity": None},
            "slot4": {"item": None, "quantity": None},
            "slot5": {"item": None, "quantity": None},
            "slot6": {"item": None, "quantity": None},
            "slot7": {"item": None, "quantity": None},
            "slot8": {"item": None, "quantity": None},
        }

        self.active_slot = 0
        self.selected_item = self.inventory_items[f"slot{self.active_slot}"]["item"]

        self.font = pygame.font.Font(filename=None, size=30)

        self.clicked_slot = None  # Store the index of the clicked slot
        self.clicked_once = False  # Flag to track the first click

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
        except KeyError:
            return False

    def update(self):
        for i in range(1, 10):  # Check keys 1 to 9
            if EventManager.keydown(pygame.K_0 + i):
                self.active_slot = i - 1
        if EventManager.scroll_wheel_up():
            self.active_slot -= 1
        if EventManager.scroll_wheel_down():
            self.active_slot += 1
        if self.active_slot > len(self.inventory_items) - 1:
            self.active_slot = 0
        if self.active_slot < 0:
            self.active_slot = len(self.inventory_items) - 1

        if EventManager.right_mouse_click():
            mouse_position = pygame.mouse.get_pos()
            slot_number = mouse_position[0] // (BLOCK_SIZE * 2)
            if 0 <= slot_number < len(self.inventory_items) and 0 <= mouse_position[1] <= BLOCK_SIZE * 2:
                if not self.clicked_once:
                    self.clicked_slot = slot_number
                    self.clicked_once = True
                else:
                    if slot_number != self.clicked_slot:
                        slot1_key = f"slot{self.clicked_slot}"
                        slot2_key = f"slot{slot_number}"
                        self.inventory_items[slot1_key]["item"], self.inventory_items[slot2_key]["item"] = self.inventory_items[slot2_key]["item"], self.inventory_items[slot1_key]["item"]

                        self.inventory_items[slot1_key]["quantity"], self.inventory_items[slot2_key]["quantity"] = self.inventory_items[slot2_key]["quantity"], self.inventory_items[slot1_key]["quantity"]

                    elif slot_number == self.clicked_slot:
                        pass
                    self.clicked_slot = None
                    self.clicked_once = False

        try:
            slot_position = f"slot{self.active_slot}"
        except IndexError:
            slot_position = f"slot{len(self.inventory_items)}"
        self.selected_item = self.inventory_items[slot_position]["item"]

    def draw(self):
        pygame.draw.rect(surface=self.screen, color="#4444a4",
                         rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * len(self.inventory_items),
                                          BLOCK_SIZE * 2))  # Draw inventory background

        padding_x = BLOCK_SIZE // 2
        padding_y = BLOCK_SIZE // 2

        for slot, item_data in self.inventory_items.items():
            slot_number = int(re.search(pattern=r"slot(.+)", string=slot).group(1))

            # highlight the slots that are about to be switched
            if self.clicked_once:
                if slot_number == self.clicked_slot or slot_number == self.active_slot:
                    pygame.draw.rect(surface=self.screen, color="white",
                                     rect=pygame.Rect(slot_number * BLOCK_SIZE * 2, 0, BLOCK_SIZE * 2, BLOCK_SIZE * 2))

            # highlight the selected slot
            if slot_number == self.active_slot:
                pygame.draw.rect(surface=self.screen, color="#fcec24",
                                 rect=pygame.Rect(slot_number * BLOCK_SIZE * 2, 0, BLOCK_SIZE * 2, BLOCK_SIZE * 2))

            pygame.draw.rect(surface=self.screen, color="black",
                             rect=pygame.Rect(slot_number * BLOCK_SIZE * 2, 0, BLOCK_SIZE * 2, BLOCK_SIZE * 2),
                             width=1)  # draw border

            if item_data["item"] is not None:
                self.screen.blit(
                    pygame.transform.scale(surface=self.textures[item_data["item"]], size=(BLOCK_SIZE, BLOCK_SIZE)),
                    (padding_x + (BLOCK_SIZE * 2) * slot_number, padding_y))
                quantity_text = self.font.render(text=str(item_data["quantity"]), antialias=True, color="#fc0015")
                self.screen.blit(quantity_text, ((BLOCK_SIZE * 2) * slot_number + 5, 5))

        pygame.draw.rect(surface=self.screen, color="black",
                         rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * len(self.inventory_items), BLOCK_SIZE * 2),
                         width=2)  # adds extra border to left and right of hotbar so border thickness all the same across all slots
