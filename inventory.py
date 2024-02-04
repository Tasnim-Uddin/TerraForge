from all_texture_data import all_texture_data

class Inventory:
    def __init__(self):
        self.items = {"sword": 1}

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

    def get_inventory(self):
        return self.items

    def get_selected_item_type(self):
        for item in self.items:
            if self.is_block(item=item):
                return item

    def clear_item(self, item_type):
        if item_type in self.items and self.items[item_type] == 0:
            del self.items[item_type]

    @staticmethod
    def is_block(item):
        if all_texture_data[item]["type"] == "block":
            return True
        return False

    def can_place(self, item_type):
        # Customize this method based on your logic for placing items
        return self.is_block(item_type)

    def use_item(self, item_type):
        # Customize this method based on your logic for using items
        pass
