class Inventory:
    def __init__(self):
        self.blocks = {"grass": 0, "dirt": 7}

    def get_all_blocks(self):
        return self.blocks

    def clear_block(self, block_type):
        if self.blocks[block_type] == 0:
            self.blocks.pop(block_type)


# player_inventory = Inventory()
# print(player_inventory.get_all_blocks())
# player_inventory.clear_block("grass")
# print(player_inventory.get_all_blocks())

hi = {}
print(len(hi))