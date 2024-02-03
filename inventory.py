class Inventory:
    def __init__(self):
        self.blocks = {}

    def add_block(self, block_type):
        if block_type in self.blocks:
            self.blocks[block_type] += 1
        else:
            self.blocks[block_type] = 1

    def remove_block(self, block_type, quantity=1):
        self.blocks[block_type] -= quantity

    def get_inventory(self):
        return self.blocks

    def get_selected_block_type(self):
        if len(self.blocks) > 0:
            return next(iter(self.blocks))

    def clear_block(self, block_type):
        if self.blocks[block_type] == 0:
            self.blocks.pop(block_type)
