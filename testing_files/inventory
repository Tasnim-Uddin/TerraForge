import pygame
from globals import *
from world.itemdata import *
from utils.events import EventHandler
import json
from utils.controls import Controller
from crafting.recipes import base_recipes, table_recipes

class Inventory:
    def __init__(self, app, textures) -> None:
        self.app = app
        self.screen = self.app.screen
        self.textures = textures

        # vars
        self.slot_count = 5
        self.expanded_slot_count = 20 # includes 5 hotbar slots
        self.slots = []
        for index in range(self.expanded_slot_count):
            self.slots.append(Item())
        self.load_inventory()
        self.slot_rects: list[pygame.Rect] = self.gen_slot_positions()
        self.crafting_slot_rects: list[pygame.Rect] = self.gen_crafting_positions()

        # active slot
        self.active_slot_index = 0
        self.active_slot = self.slots[self.active_slot_index]

        # cursor
        self.cursor = Cursor(pygame.mouse.get_pos())

        # states
        self.expanded_inventory = False
        self.flipped = 0
        self.near_table = False

        # open chest
        self.active_chest: StorageBlock = None

        # font stuff
        self.font = pygame.font.Font(None, 25)

        # crafting
        self.available_recipes = self.gen_available_recipes()
        self.recipe_index_start = 0
    # --- DATA LOADING ---
    def load_inventory(self):
        with open('inventory/inventorydata.json', "r") as json_file:
            data = json.load(json_file)
        for index in range(self.expanded_slot_count):
            self.slots[index] = items[data[index]['name']].type(data[index]['name'], data[index]['quantity'])
    def gen_slot_positions(self) -> list:
        slot_rects = []

        x_offset = TILESIZE//4
        y_offset = TILESIZE//4
        column = 0
        row = 0
        for slot in self.slots:
            slot_rects.append(pygame.Rect(x_offset + column*TILESIZE*1.5, y_offset + row*TILESIZE*1.5, TILESIZE, TILESIZE))
            column += 1
            if column == 5:
                column = 0
                row += 1
        return slot_rects
    def gen_crafting_positions(self) -> list:
        crafting_slot_rects = []

        y_offset = TILESIZE*6.5
        x_offset = TILESIZE//2
        for index in range(4):
            crafting_slot_rects.append(pygame.Rect(x_offset, y_offset + index*TILESIZE*1.5, TILESIZE, TILESIZE))

        return crafting_slot_rects
    def close(self):
        data = [{'name':slot.name, 'quantity':slot.quantity} for slot in self.slots]
        with open('inventory/inventorydata.json', "w") as json_file:
            json.dump(data, json_file)
    # --- INPUT ---
    def input(self):
        

        if not self.expanded_inventory:
            if EventHandler.scroll_wheel_down():
                self.active_slot_index += 1
            if EventHandler.scroll_wheel_up():
                self.active_slot_index -= 1
            if self.active_slot_index < 0:
                self.active_slot_index = self.slot_count-1
            if self.active_slot_index > self.slot_count-1:
                self.active_slot_index = 0
        else:
            if EventHandler.scroll_wheel_down():
                self.recipe_index_start += 1
            if EventHandler.scroll_wheel_up():
                self.recipe_index_start -= 1
            if self.recipe_index_start < 0:
                self.recipe_index_start = len(self.available_recipes)-1
            if self.recipe_index_start > len(self.available_recipes)-1:
                self.recipe_index_start = 0

        # directional blocks
        if items[self.active_slot.name].type == DirectionalBlockItem:
            if EventHandler.keydown(pygame.K_r):
                self.flipped += 1
                if self.flipped > 3:
                    self.flipped = 0

        # expanded inventory controls
        if EventHandler.keydown(Controller.open_inventory):
            self.expanded_inventory = not self.expanded_inventory

        if self.expanded_inventory:
            if EventHandler.clicked(1):
                mouse_pos = self.cursor.position
                for index, slot in enumerate(self.slot_rects):
                    if slot.collidepoint(mouse_pos):
                        if self.cursor.name == "default": # if cursor is empty
                            self.cursor.name = self.slots[index].name
                            self.cursor.quantity = self.slots[index].quantity
                            self.slots[index].empty()
                        else: # if cursor is not empty
                            if self.cursor.name == self.slots[index].name:
                                self.slots[index].quantity += self.cursor.quantity
                                self.cursor.empty()
                            else:
                                new_name = self.cursor.name
                                new_quantity = self.cursor.quantity
                                self.cursor.name = self.slots[index].name
                                self.cursor.quantity = self.slots[index].quantity
                                self.slots[index] = items[new_name].type(new_name, new_quantity)
                # crafting
                for index in range(self.recipe_index_start, self.recipe_index_start+4):
                    if index < len(self.available_recipes) and (self.cursor.name == "default" or self.cursor.name == self.available_recipes[index]['output']) and self.crafting_slot_rects[index-self.recipe_index_start].collidepoint(mouse_pos):
                        self.cursor.name = self.available_recipes[index]['output']
                        self.cursor.quantity += self.available_recipes[index]['quantity']
                        self.remove_resources(self.available_recipes[index]['recipe'])
                        
                if self.active_chest:
                    for index, slot in enumerate(self.active_chest.slot_rects):
                        if slot.collidepoint(mouse_pos):
                            if self.cursor.name == "default": # if cursor is empty
                                self.cursor.name = self.active_chest.slots[index]['name']
                                self.cursor.quantity = self.active_chest.slots[index]['quantity']
                                self.active_chest.slots[index] = {'name':'default', 'quantity':0}
                            else: # if cursor is not empty
                                if self.cursor.name == self.active_chest.slots[index]['name']:
                                    self.active_chest.slots[index]['quantity'] += self.cursor.quantity
                                    self.cursor.empty()
                                else:
                                    new_name = self.cursor.name
                                    new_quantity = self.cursor.quantity
                                    self.cursor.name = self.active_chest.slots[index]['name']
                                    self.cursor.quantity = self.active_chest.slots[index]['quantity']
                                    self.active_chest.slots[index] = {'name':new_name, 'quantity':new_quantity}
                self.available_recipes = self.gen_available_recipes()
            # right click handling
            if EventHandler.clicked(3):
                for index, slot in enumerate(self.slots):
                    if slot.name != "default" and self.slot_rects[index].collidepoint(self.cursor.position):
                        if self.cursor.name == "default":
                            self.cursor.name = slot.name
                            if slot.quantity > 1:
                                self.cursor.quantity += slot.quantity//2
                                if slot.quantity % 2 > 0:
                                    slot.quantity = slot.quantity//2 + 1
                                else:
                                    slot.quantity = slot.quantity//2
                            else:
                                self.cursor.quantity = 1
                                slot.empty()
                        else:
                            self.cursor.quantity -= 1
                            slot.quantity += 1
                            if self.cursor.quantity < 1:
                                self.cursor.empty()
                    elif slot.name == "default" and self.cursor.name != "default" and self.slot_rects[index].collidepoint(self.cursor.position):
                        slot.name = self.cursor.name
                        slot.quantity += 1
                        self.cursor.quantity -= 1
                        if self.cursor.quantity < 1:
                            self.cursor.empty()
                self.available_recipes = self.gen_available_recipes()
                        
    # --- UTILS ---
    def add_item(self, name: str, amount = 1) -> int:
        amount_satisfied = 0 # in the future, will be used to calc picking up only portion of items
        first_available_slot = self.expanded_slot_count
        for index, slot in enumerate(self.slots):
            if slot.name == name:
                slot.quantity += amount
                amount_satisfied = amount
                return amount_satisfied
            if slot.name == "default":
                if index < first_available_slot:
                    first_available_slot = index
        if first_available_slot != self.expanded_slot_count:
            self.slots[first_available_slot] = items[name].type(name, amount)
            amount_satisfied = amount
        if amount_satisfied > 0:
            self.available_recipes = self.gen_available_recipes()
        return amount_satisfied
    def use_item(self, *args, **kwargs):
        if self.active_slot.name != "default":
            self.active_slot.use(*args, **kwargs)
        self.available_recipes = self.gen_available_recipes()
    def update(self):
        self.input()
        self.cursor.update()
        self.active_slot = self.slots[self.active_slot_index]
        
        # chest handling
        if self.active_chest and not self.active_chest.open:
            self.active_chest = None
    def draw(self):
        # transparent surface
        surf = pygame.Surface((TILESIZE*1.5, TILESIZE*1.5))
        surf.fill("gray")
        surf.set_alpha(128)
        # expanded inventory ? 
        visible_slot_count = self.slot_count
        if self.expanded_inventory:
            visible_slot_count = self.expanded_slot_count

        for index in range(visible_slot_count):
            pygame.draw.rect(self.screen, "gray", pygame.Rect(self.slot_rects[index].x-TILESIZE//4, self.slot_rects[index].y-TILESIZE//4, TILESIZE*1.5, TILESIZE*1.5), 2)
            # highlighting
            text_color = "white"
            if index == self.active_slot_index:
                text_color = "black"
                pygame.draw.rect(self.screen, "white", pygame.Rect(self.slot_rects[index].x-TILESIZE//4, self.slot_rects[index].y-TILESIZE//4, TILESIZE*1.5, TILESIZE*1.5))
            else:
                self.screen.blit(surf, (self.slot_rects[index].x - TILESIZE//4, self.slot_rects[index].y - TILESIZE//4))
            if self.slots[index].name != "default":
                self.screen.blit(self.textures[self.slots[index].name], self.slot_rects[index])
                if self.slots[index].quantity > 1:
                    self.text = self.font.render(str(self.slots[index].quantity), True, text_color, None)
                    self.screen.blit(self.text, self.slot_rects[index])
        # crafting
        if self.expanded_inventory:
            for index in range(self.recipe_index_start, self.recipe_index_start+4):
                slot = self.crafting_slot_rects[index-self.recipe_index_start]
                self.screen.blit(surf, (slot.x - TILESIZE//4, slot.y - TILESIZE//4))
                pygame.draw.rect(self.screen, "gray", pygame.Rect(slot.x - TILESIZE//4, slot.y - TILESIZE//4, TILESIZE*1.5, TILESIZE*1.5), 2)
                if index < len(self.available_recipes):
                    self.screen.blit(self.textures[self.available_recipes[index]['output']], self.crafting_slot_rects[index-self.recipe_index_start])
        # draw cursor
        if self.cursor.name != "default":
            self.screen.blit(self.textures[self.cursor.name], self.cursor.block_position)
            if self.cursor.quantity > 1:
                self.text = self.font.render(str(self.cursor.quantity), True, "white", None)
                self.screen.blit(self.text, (self.cursor.position[0]-TILESIZE//2, self.cursor.position[1]-TILESIZE//2))

        # chest
        if self.active_chest:
            for index, slot in enumerate(self.active_chest.slots):
                if slot['name'] != "default":
                    self.screen.blit(self.textures[slot['name']], self.active_chest.slot_rects[index])
                    if self.active_chest.slots[index]['quantity'] > 1:
                        self.text = self.font.render(str(self.active_chest.slots[index]['quantity']), True, text_color, None)
                        self.screen.blit(self.text, self.active_chest.slot_rects[index])
    def remove_resources(self, resources):
        for item, amount in resources.items():
            target_amount = amount
            for slot in self.slots:
                if slot.name == item:
                    slot.quantity -= target_amount
                    if slot.quantity <= 0:
                        target_amount = abs(slot.quantity)
                        slot.empty()
                        
    def gen_available_recipes(self):
        recipe_list = base_recipes
        if self.near_table:
            recipe_list = table_recipes
        recipes = []
        for recipe in recipe_list:
            necessary_items = len(recipe['recipe'])
            for item, amount in recipe['recipe'].items():
                target_amount = amount
                for slot in self.slots:
                    if slot.name == item:
                        target_amount -= slot.quantity
                        if target_amount < 1:
                            necessary_items -= 1
                            break
            if necessary_items <= 0:
                recipes.append(recipe)
        return recipes

class Cursor(Item):
    def __init__(self, position: tuple, name: str = "default", quantity: int = 0) -> None:
        super().__init__(name, quantity)
        self.position = position
    def update(self):
        self.position = pygame.mouse.get_pos()
    @property
    def block_position(self):
        return (self.position[0]-TILESIZE//2, self.position[1]-TILESIZE//2)