import pygame
import re

from global_constants import *
from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self, screen, textures):
        self.screen = screen
        self.textures = textures

        self.inventory_items = {"slot0": {"item": "sword", "quantity": 1},
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

    def get_selected_item(self):
        return self.selected_item

    def add_item(self, item):
        for item_data in self.inventory_items.values():
            if item_data["item"] == item:
                item_data["quantity"] += 1
                return
            elif item_data["item"] is None:
                item_data["item"] = item
                item_data["quantity"] = 1
                return
        # for item_data in self.inventory_items.items():
        #     if item_data["item"] is None:
        #         item_data["item"] = item
        #         item_data["quantity"] = 1
        #         return

    def remove_item(self, item):
        # if item in self.items:
        #     self.items[item] -= 1
        #     if self.items[item] <= 0:
        #         self.items.pop(item)
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
            if EventManager.keydown(key=pygame.K_0 + i):
                self.active_slot = i - 1
        if EventManager.scroll_wheel_up():
            self.active_slot -= 1
        if EventManager.scroll_wheel_down():
            self.active_slot += 1
        if self.active_slot > len(self.inventory_items) - 1:
            self.active_slot = 0
        if self.active_slot < 0:
            self.active_slot = len(self.inventory_items) - 1
        try:
            slot_position = f"slot{self.active_slot}"
        except IndexError:
            slot_position = f"slot{len(self.inventory_items)}"
        self.selected_item = self.inventory_items[slot_position]["item"]

    def draw(self):
        pygame.draw.rect(surface=self.screen, color="#4444a4", rect=pygame.Rect(0, 0, (BLOCK_SIZE*2)*len(self.inventory_items), BLOCK_SIZE*2))  # slots

        padding_x = BLOCK_SIZE//2
        padding_y = BLOCK_SIZE//2

        for slot, item_data in self.inventory_items.items():
            slot_number = int(re.search(pattern=r"slot(.+)", string=slot).group(1))

            if slot_number == self.active_slot:
                pygame.draw.rect(surface=self.screen, color="#fcec24", rect=pygame.Rect(slot_number*BLOCK_SIZE*2, 0, BLOCK_SIZE*2, BLOCK_SIZE*2))  # highlight selected block

            pygame.draw.rect(surface=self.screen, color="black", rect=pygame.Rect(slot_number*BLOCK_SIZE*2, 0, BLOCK_SIZE*2, BLOCK_SIZE*2), width=1)  # border

            if item_data["item"] is not None:
                self.screen.blit(pygame.transform.scale_by(surface=self.textures[item_data["item"]], factor=(BLOCK_SIZE/all_texture_data[item_data["item"]]["size"][0], BLOCK_SIZE/all_texture_data[item_data["item"]]["size"][1])), (padding_x + (BLOCK_SIZE * 2) * slot_number, padding_y))
                quantity_text = self.font.render(text=str(item_data["quantity"]), antialias=True, color="#fc0015")
                self.screen.blit(quantity_text, ((BLOCK_SIZE * 2) * slot_number + 5, 5))

        pygame.draw.rect(surface=self.screen, color="black",
                         rect=pygame.Rect(0, 0, (BLOCK_SIZE * 2) * len(self.inventory_items), BLOCK_SIZE * 2), width=2)  # fix double border thickness from before around each slot