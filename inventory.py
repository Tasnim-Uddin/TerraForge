import pygame

from all_texture_data import all_texture_data
from event_manager import EventManager


class Inventory:
    def __init__(self):
        self.items = {"sword": 1,
                      "pickaxe": 1,
                      "axe": 1}

        self.selected_item = "sword"
        self.active_slot = 0

    def get_selected_item(self):
        return self.selected_item

    def add_item(self, item_type):
        if item_type in self.items:
            self.items[item_type] += 1
        else:
            self.items[item_type] = 1

    def remove_item(self, item_type, quantity=1):
        if item_type in self.items:
            self.items[item_type] -= quantity
            if self.items[item_type] <= 0:
                del self.items[item_type]

    def clear_item(self, item_type):
        if item_type in self.items and self.items[item_type] == 0:
            self.items.pop(item_type)

    @staticmethod
    def is_block(item):
        if all_texture_data[item]["type"] == "block":
            return True
        return False

    def update(self):
        items_list = list(self.items.keys())
        if EventManager.keydown(key=pygame.K_RIGHT):
            if self.active_slot < len(self.items) - 1:
                self.active_slot += 1
        if EventManager.keydown(key=pygame.K_LEFT):
            if self.active_slot > 0:
                self.active_slot -= 1
        try:
            self.selected_item = items_list[self.active_slot]
        except IndexError:
            self.selected_item = items_list[len(self.items) - 1]
