import pygame

from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self):
        self.inventory_items = {"slot1": {"item": "sword", "quantity": 1},
                                "slot2": {"item": "pickaxe", "quantity": 1},
                                "slot3": {"item": "axe", "quantity": 1},
                                "slot4": {"item": None, "quantity": None},
                                "slot5": {"item": None, "quantity": None},
                                "slot6": {"item": None, "quantity": None},
                                "slot7": {"item": None, "quantity": None},
                                "slot8": {"item": None, "quantity": None},
                                "slot9": {"item": None, "quantity": None},
                                }

        self.active_slot = 1
        self.selected_item = self.inventory_items[f"slot{self.active_slot}"]["item"]

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

    def is_block(self, item):
        try:
            if all_texture_data[item]["type"] == "block":
                return True
        except KeyError:
            return False

    def update(self):
        for i in range(1, 9):  # Check keys 1 to 10
            if EventManager.keydown(key=pygame.K_0 + i):
                self.active_slot = i
        try:
            slot_position = f"slot{self.active_slot}"
        except IndexError:
            slot_position = f"slot{len(self.inventory_items) - 1}"
        self.selected_item = self.inventory_items[slot_position]["item"]

