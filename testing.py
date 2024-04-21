import random
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch, mock_open, call, Mock
import json
import os

import pygame

from global_constants import *
from main import Game
from scene import Scene
from inventory import Inventory
from entity import Entity
from player import Player
from slime_enemy import SlimeEnemy
from client import Client
from server import Server


class TestGame(unittest.TestCase):
    def setUp(self):
        # Initialize the Game object
        self.game = Game()

    def test_validate_username_text_input(self):
        # Test validate_username_text_input method
        # Test when username length is within the valid range
        self.game._Game__username = "test"
        self.assertFalse(self.game.validate_username_text_input())

        # Test when username length is too short
        self.game._Game__username = "tes"
        self.assertFalse(self.game.validate_username_text_input())

        # Test when username length is too long
        self.game._Game__username = "testtesttesttesttesttest"
        self.assertFalse(self.game.validate_username_text_input())

        # Test when username length is exactly at the lower bound
        self.game._Game__username = "test1"
        self.assertTrue(self.game.validate_username_text_input())

        # Test when username length is exactly at the upper bound
        self.game._Game__username = "testtesttesttesttest"
        self.assertTrue(self.game.validate_username_text_input())

    def test_validate_password_text_input(self):
        # Test validate_password_text_input method
        # Test when password meets criteria
        self.assertTrue(self.game.validate_password_text_input("Test@1234"))

        # Test when password is too short
        self.assertFalse(self.game.validate_password_text_input("Test1"))

        # Test when password is too long
        self.assertFalse(self.game.validate_password_text_input("TestTestTestTestTestTestTestTestTestTestTestTest"))

        # Test when password has no uppercase letter
        self.assertFalse(self.game.validate_password_text_input("test@1234"))

        # Test when password has no lowercase letter
        self.assertFalse(self.game.validate_password_text_input("TEST@1234"))

        # Test when password has no digit
        self.assertFalse(self.game.validate_password_text_input("Test@Test"))

        # Test when password has no special character
        self.assertFalse(self.game.validate_password_text_input("Test1234"))

    def test_validate_player_text_input(self):
        # Test validate_player_text_input method
        # Test when player name is within the valid range
        self.game._Game__player_name = "test"
        self.assertFalse(self.game.validate_player_text_input())

        # Test when player name is too short
        self.game._Game__player_name = "tes"
        self.assertFalse(self.game.validate_player_text_input())

        # Test when player name is too long
        self.game._Game__player_name = "testtesttesttesttesttest"
        self.assertFalse(self.game.validate_player_text_input())

        # Test when player name length is exactly at the lower bound
        self.game._Game__player_name = "test1"
        self.assertTrue(self.game.validate_player_text_input())

        # Test when player name length is exactly at the upper bound
        self.game._Game__player_name = "testtesttesttesttest"
        self.assertTrue(self.game.validate_player_text_input())

    def test_validate_world_text_input(self):
        # Test validate_world_text_input method
        # Test when world name is within the valid range
        self.game._Game__world_name = "test"
        self.assertFalse(self.game.validate_world_text_input())

        # Test when world name is too short
        self.game._Game__world_name = "tes"
        self.assertFalse(self.game.validate_world_text_input())

        # Test when world name is too long
        self.game._Game__world_name = "testtesttesttesttesttest"
        self.assertFalse(self.game.validate_world_text_input())

        # Test when world name length is exactly at the lower bound
        self.game._Game__world_name = "test1"
        self.assertTrue(self.game.validate_world_text_input())

        # Test when world name length is exactly at the upper bound
        self.game._Game__world_name = "testtesttesttesttest"
        self.assertTrue(self.game.validate_world_text_input())


class TestScene(unittest.TestCase):
    def setUp(self):
        # Initialize the Game object
        self.game = Game()
        # Initialize the Scene object
        self.scene = Scene(game=self.game)

    def test_get_player(self):
        # Test get_player method
        player = self.scene.get_player()
        self.assertTrue(isinstance(player, Player))

    def test_get_inventory(self):
        # Test get_inventory method
        inventory = self.scene.get_inventory()
        self.assertTrue(isinstance(inventory, Inventory))

    def test_spawn_enemy(self):
        # Test __spawn_enemy method
        # Mock player's x position
        # Mock chunk positions and block positions
        self.scene._Scene__player.set_x(x=0)
        self.scene._Scene__chunks = {(-1, 0): {(-5, 0): "grass"}, (0, 0): {(0, 0): "grass"}, (1, 0): {(40, 0): "grass"}}

        # Ensure at least one enemy is spawned
        self.scene._Scene__spawn_enemy()
        self.assertTrue(len(self.scene._Scene__enemies) > 0)

    def test_generate_chunk(self):
        # Prepare mock data
        self.scene._Scene__chunks = {(0, 0): {}}

        self.scene.lower_cave_threshold = 0.015
        self.scene.upper_cave_threshold = 0.7

        # Call the method
        chunk_offset = (0, 0)
        key = (0, 0)
        self.scene._Scene__generate_chunk(chunk_offset)

        # Assertions based on the expected behavior of __generate_chunk

        # Example: Ensure that the chunk contains some blocks
        self.assertTrue(len(self.scene._Scene__chunks[key]) > 0)

        # Example: Ensure that the chunk contains expected block types based on conditions
        for block_position, block_type in self.scene._Scene__chunks[key].items():
            # Check the block type based on its position and the specified conditions in __generate_chunk
            real_x = block_position[0] * BLOCK_SIZE
            real_y = block_position[1] * BLOCK_SIZE
            height_noise = int((self.scene.world_seed.noise2(x=real_x * 0.003, y=0) * 200) // BLOCK_SIZE * BLOCK_SIZE)
            cave_value = 0.05

            if real_y + height_noise == 0:
                self.assertEqual(block_type, "grass")
            elif DIRT_LEVEL < (real_y + height_noise) <= CAVE_LEVEL * BLOCK_SIZE:
                self.assertEqual(block_type, "dirt")
            elif CAVE_LEVEL * BLOCK_SIZE < (real_y + height_noise) <= DEEP_CAVE_LEVEL * BLOCK_SIZE:
                # Determine the expected block type based on probabilities and thresholds
                if self.scene.lower_cave_threshold < cave_value < self.scene.upper_cave_threshold:
                    self.assertIn(block_type,
                                  ["stone", "coal_ore", "iron_ore", "gold_ore", "emerald_ore", "diamond_ore"])
                else:
                    self.assertEqual(block_type, "stone")
            elif DEEP_CAVE_LEVEL * BLOCK_SIZE < (real_y + height_noise):
                # Determine the expected block type based on probabilities and thresholds
                if random.random() < COAL_SPAWN_RATE:
                    self.assertEqual(block_type, "deepslate_coal_ore")
                elif random.random() < IRON_SPAWN_RATE:
                    self.assertEqual(block_type, "deepslate_iron_ore")
                elif random.random() < GOLD_SPAWN_RATE:
                    self.assertEqual(block_type, "deepslate_gold_ore")
                elif random.random() < EMERALD_SPAWN_RATE:
                    self.assertEqual(block_type, "deepslate_emerald_ore")
                elif random.random() < DIAMOND_SPAWN_RATE:
                    self.assertEqual(block_type, "deepslate_diamond_ore")
                else:
                    self.assertEqual(block_type, "deepslate")

    def test_check_door(self):
        # Mock necessary attributes and methods
        self.scene._Scene__player._rect.x = 3 * BLOCK_SIZE
        self.scene._Scene__player._rect.y = 3 * BLOCK_SIZE
        self.scene.camera_offset = (0, 0)

        pygame.mouse.set_pos((0, 0))
        self.scene._Scene__chunks = {
            (0, 0): {(0, 0): "top_oak_door_open", (0, 1): "bottom_oak_door_open"}
        }
        # Call the method
        self.scene.check_door()
        # Assert expected changes
        self.assertEqual(self.scene._Scene__chunks[(0, 0)][(0, 0)], "top_oak_door_closed")
        self.assertEqual(self.scene._Scene__chunks[(0, 0)][(0, 1)], "bottom_oak_door_closed")

        pygame.mouse.set_pos((0, 0))
        self.scene._Scene__chunks = {
            (0, 0): {(0, 0): "top_oak_door_closed", (0, 1): "bottom_oak_door_closed"}
        }
        # Call the method
        self.scene.check_door()
        # Assert expected changes
        self.assertEqual(self.scene._Scene__chunks[(0, 0)][(0, 0)], "top_oak_door_open")
        self.assertEqual(self.scene._Scene__chunks[(0, 0)][(0, 1)], "bottom_oak_door_open")

        self.scene._Scene__player._rect.x = 6 * BLOCK_SIZE
        self.scene._Scene__player._rect.y = 6 * BLOCK_SIZE

        pygame.mouse.set_pos((0, 0))
        self.scene._Scene__chunks = {
            (0, 0): {(0, 0): "top_oak_door_open", (0, 1): "bottom_oak_door_open"}
        }
        # Call the method
        self.scene.check_door()
        # Assert expected changes
        self.assertNotEqual(self.scene._Scene__chunks[(0, 0)][(0, 0)], "top_oak_door_closed")
        self.assertNotEqual(self.scene._Scene__chunks[(0, 0)][(0, 1)], "bottom_oak_door_closed")

        pygame.mouse.set_pos((0, 0))
        self.scene._Scene__chunks = {
            (0, 0): {(0, 0): "top_oak_door_closed", (0, 1): "bottom_oak_door_closed"}
        }
        # Call the method
        self.scene.check_door()
        # Assert expected changes
        self.assertNotEqual(self.scene._Scene__chunks[(0, 0)][(0, 0)], "top_oak_door_open")
        self.assertNotEqual(self.scene._Scene__chunks[(0, 0)][(0, 1)], "bottom_oak_door_open")

    def test___break_block(self):
        # Mock necessary attributes and methods
        self.scene._Scene__player._rect.x = 6 * BLOCK_SIZE
        self.scene._Scene__player._rect.y = 6 * BLOCK_SIZE
        self.scene.camera_offset = (0, 0)
        pygame.mouse.set_pos((10 * BLOCK_SIZE, 10 * BLOCK_SIZE))
        self.scene._Scene__chunks = {
            (0, 0): {(10, 10): "stone"}
        }
        self.scene._Scene__inventory.__selected_item = "copper_pickaxe"
        # Call the method with different scenarios

        # Scenario 1: Breaking a stone block with a pickaxe
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])

        # Scenario 2: Breaking a torch with a pickaxe
        self.scene._Scene__chunks[(0, 0)][(10, 10)] = "torch"
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])
        self.assertNotIn((0, 0), self.scene.torch_positions)

        # Scenario 3: Breaking a tree log with an axe
        self.scene._Scene__chunks[(0, 0)][(10, 10)] = "tree_log"
        self.scene._Scene__break_block(held_item="copper_axe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])

        # Scenario 4: Breaking a top oak door with a pickaxe
        self.scene._Scene__chunks = {
            (0, 0): {(10, 10): "top_oak_door_open", (10, 11): "bottom_oak_door_open"}
        }
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])
        self.assertNotIn((10, 11), self.scene._Scene__chunks[(0, 0)])

        # Scenario 5: Breaking a top oak door with a pickaxe
        self.scene._Scene__chunks = {
            (0, 0): {(10, 10): "top_oak_door_closed", (10, 11): "bottom_oak_door_closed"}
        }
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])
        self.assertNotIn((10, 11), self.scene._Scene__chunks[(0, 0)])

        # Scenario 6: Breaking a tree leaf with a pickaxe
        self.scene._Scene__chunks = {
            (0, 0): {(10, 10): "tree_leaf"}
        }
        self.scene._Scene__inventory._Inventory__inventory_items = {(0, 0): {"item": "copper_pickaxe", "quantity": 1},
                                                                    (0, 1): {"item": None, "quantity": None}}
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])

        with patch('random.random', return_value=0.03):
            self.assertTrue("apple", self.scene._Scene__inventory._Inventory__inventory_items[(0, 1)]["item"])
            self.assertTrue("1", self.scene._Scene__inventory._Inventory__inventory_items[(0, 1)]["quantity"])

        # Scenario 7: Breaking a crafting table with a pickaxe
        self.scene._Scene__chunks[(0, 0)][(10, 10)] = "crafting_table"
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])

        # Scenario 8: Breaking a furnace with a pickaxe
        self.scene._Scene__chunks[(0, 0)][(10, 10)] = "furnace"
        self.scene._Scene__break_block(held_item="copper_pickaxe")
        self.assertNotIn((10, 10), self.scene._Scene__chunks[(0, 0)])

    def test___place_block(self):
        # Scenario 1: Placing a block where no block exists
        self.scene._Scene__player._rect.x = 6 * BLOCK_SIZE
        self.scene._Scene__player._rect.y = 6 * BLOCK_SIZE
        self.scene.camera_offset = (0, 0)

        self.scene._Scene__chunks = {
            (0, 0): {}
        }

        pygame.mouse.set_pos((10 * BLOCK_SIZE, 10 * BLOCK_SIZE))
        self.scene._Scene__inventory.__selected_item = "stone"
        self.scene._Scene__place_block(held_item="stone")
        self.assertIn((10, 10), self.scene._Scene__chunks[(0, 0)])

        # Scenario 2: Placing a block when out of reach
        self.scene._Scene__chunks[(0, 0)] = {}
        pygame.mouse.set_pos((20 * BLOCK_SIZE, 20 * BLOCK_SIZE))
        self.scene._Scene__place_block(held_item="stone")
        self.assertNotIn((20, 20), self.scene._Scene__chunks[(0, 0)])

        # Scenario 3: Placing a block when the player is colliding with the block grid
        self.scene._Scene__chunks[(0, 0)] = {}
        pygame.mouse.set_pos((6 * BLOCK_SIZE, 6 * BLOCK_SIZE))
        self.scene._Scene__place_block(held_item="stone")
        self.assertNotIn((6, 6), self.scene._Scene__chunks[(0, 0)])

        pygame.mouse.set_pos((7 * BLOCK_SIZE, 7 * BLOCK_SIZE))

        # Scenario 4: Placing a torch
        self.scene._Scene__chunks[(0, 0)] = {}
        self.scene._Scene__inventory.__selected_item = "torch"
        self.scene._Scene__place_block(held_item="torch")
        self.assertIn((7, 7), self.scene._Scene__chunks[(0, 0)])
        self.assertIn((0, 0), self.scene.torch_positions)

        # Scenario 5: Placing a crafting table
        self.scene._Scene__chunks[(0, 0)] = {}
        self.scene._Scene__inventory.__selected_item = "crafting_table"
        self.scene._Scene__place_block(held_item="crafting_table")
        self.assertIn((7, 7), self.scene._Scene__chunks[(0, 0)])
        self.assertIn((0, 0), self.scene.crafting_table_positions)

        # Scenario 6: Placing a furnace
        self.scene._Scene__chunks[(0, 0)] = {}
        self.scene._Scene__inventory.__selected_item = "furnace"
        self.scene._Scene__place_block(held_item="furnace")
        self.assertIn((7, 7), self.scene._Scene__chunks[(0, 0)])
        self.assertIn((0, 0), self.scene.furnace_positions)

        # Scenario 7: Placing an oak door from the inventory
        self.scene._Scene__chunks[(0, 0)] = {}
        self.scene._Scene__inventory.__selected_item = "oak_door_inventory"
        self.scene._Scene__place_block(held_item="oak_door_inventory")
        self.assertIn((7, 7), self.scene._Scene__chunks[(0, 0)])

    def test_save_world_to_json(self):
        # Mock world name and chunk data
        self.scene._Scene__world_name = "test_world"
        self.scene.world_seed_value = 12345
        self.scene._Scene__chunks = {
            (0, 0): {(0, 0): "stone", (1, 1): "dirt"},
            (1, 0): {(35, 0): "grass", (49, 2): "tree_log"}
        }

        # Mock the open function to prevent writing to the actual file system
        with patch("builtins.open", mock_open()) as mock_file:
            # Call the method
            self.scene.save_world_to_json()

            # Check file creation
            world_path = os.path.join(WORLD_SAVE_FOLDER, "test_world.json")
            mock_file.assert_called_once_with(world_path, "w")

            # Verify write calls
            handle = mock_file()
            assert handle.write.call_count == 33

            # Capture the content written to the file
            written_content_parts = [call_args[0][0] for call_args in mock_file().write.call_args_list]

            # Concatenate the parts to reconstruct the full JSON string
            written_content = "".join(written_content_parts)

            # Check if the written content matches the expected content
            expected_content = json.dumps({"world_seed_value": 12345, "chunks": {
                "0;0": {"0;0": "stone", "1;1": "dirt"},
                "1;0": {"35;0": "grass", "49;2": "tree_log"}
            }})
            assert written_content == expected_content

    def test_load_world_from_json(self):
        # Mock world name
        self.scene._Scene__world_name = "test_world"

        # Prepare mock serialized chunk data
        mock_serialized_world_data = {"world_seed_value": 12345, "chunks": {
                "0;0": {"0;0": "stone", "1;1": "dirt"},
                "1;0": {"35;0": "grass", "49;2": "tree_log"}
            }}

        # Mock the existence of the JSON file and its content
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_serialized_world_data))) as mock_file:
                # Call the method
                world_seed_value, chunks = self.scene.load_world_from_json()

                # Check if the file path is constructed correctly
                world_path = os.path.join(WORLD_SAVE_FOLDER, "test_world.json")
                os.path.exists.assert_called_once_with(world_path)

                # Verify that the file is opened and loaded correctly
                mock_file.assert_called_once_with(world_path, "r")
                mock_file().read.assert_called_once()

                # Verify the loaded chunk data
                expected_world_seed_value = 12345
                expected_chunks = {
                    (0, 0): {(0, 0): "stone", (1, 1): "dirt"},
                    (1, 0): {(35, 0): "grass", (49, 2): "tree_log"}
                }
                assert world_seed_value == expected_world_seed_value, "Loaded world seed value does not match expected data"
                assert chunks == expected_chunks, "Loaded chunks do not match expected data"


class TestInventory(unittest.TestCase):

    def setUp(self):
        # Mock game, screen, and textures
        game = Game()
        screen = pygame.Surface((800, 600))  # Mock screen
        textures = {}  # Mock textures

        self.inventory = Inventory(game, screen, textures)

    def test_get_selected_item(self):
        # Initially selected item should be None
        self.assertEqual("copper_sword", self.inventory.get_selected_item())

    def test_get_item_type(self):
        # Test getting item type for existing item
        item_type = self.inventory.get_item_type("stone")
        self.assertEqual(item_type, "block")

        # Test getting item type for non-existing item
        item_type = self.inventory.get_item_type("non_existing_item")
        self.assertIsNone(item_type)

    def test_add_item(self):
        # Test adding item to empty inventory
        self.inventory.add_item("dirt")
        self.assertEqual(self.inventory._Inventory__inventory_items[(0, 3)]["item"], "dirt")
        self.assertEqual(self.inventory._Inventory__inventory_items[(0, 3)]["quantity"], 1)

        # Test adding quantity to existing item
        self.inventory.add_item(item="dirt", quantity=2)
        self.assertEqual(self.inventory._Inventory__inventory_items[(0, 3)]["quantity"], 3)

    def test_remove_item(self):
        # Test removing item from inventory
        self.inventory._Inventory__inventory_items[(0, 3)] = {"item": "dirt", "quantity": 1}
        self.inventory.remove_item("dirt")
        self.assertIsNone(self.inventory._Inventory__inventory_items[(0, 3)]["item"])
        self.assertIsNone(self.inventory._Inventory__inventory_items[(0, 3)]["quantity"])

    def test_determine_crafting_table(self):
        # Define player position, neighbour_chunk_offsets, and crafting_table_positions
        player_position = (0, 0)
        neighbour_chunk_offsets = [(0, 0)]
        crafting_table_positions = {(0, 0): [(0, 3)]}

        # Test when player is near crafting table
        self.inventory.determine_crafting_table(player_position, neighbour_chunk_offsets, crafting_table_positions)
        self.assertTrue(self.inventory.crafting_table)

        # Test when player is not near crafting table
        player_position = (50 * BLOCK_SIZE, 50 * BLOCK_SIZE)  # Set player far away
        self.inventory.determine_crafting_table(player_position, neighbour_chunk_offsets, crafting_table_positions)
        self.assertFalse(self.inventory.crafting_table)

    def test_determine_furnace(self):
        # Define player position, neighbour_chunk_offsets, and furnace_positions
        player_position = (0, 0)
        neighbour_chunk_offsets = [(0, 0)]
        furnace_positions = {(0, 0): [(0, 3)]}

        # Test when player is near furnace
        self.inventory.determine_furnace(player_position, neighbour_chunk_offsets, furnace_positions)
        self.assertTrue(self.inventory.furnace)

        # Test when player is not near furnace
        player_position = (50 * BLOCK_SIZE, 50 * BLOCK_SIZE)  # Set player far away
        self.inventory.determine_furnace(player_position, neighbour_chunk_offsets, furnace_positions)
        self.assertFalse(self.inventory.furnace)

    def test_craft_item(self):
        # Set up initial inventory state with required input items
        self.inventory._Inventory__inventory_items = {(0, 0): {"item": "stick", "quantity": 1},
                                                      (0, 1): {"item": "coal", "quantity": 1},
                                                      (0, 3): {"item": None, "quantity": None}}

        # Define the modified crafting recipe for torch
        recipe = {
            "input": {"item": ["stick", "coal"], "quantity": [1, 1]},
            "output": {"item": "torch", "quantity": 4}
        }

        # Set current_available_recipes to contain the modified recipe
        self.inventory.current_available_recipes = {"torch": recipe}

        # Call craft_item method with the recipe name
        with patch("builtins.print") as mock_print:
            self.inventory.craft_item("torch")

            # Assert that the print statements indicate successful crafting
            mock_print.assert_called_once_with("torch crafted successfully!")

            # Assert that the inventory state is updated correctly after crafting
            self.assertEqual(self.inventory.get_item_quantity("stick"), 0)  # 1 - 1 = 0
            self.assertEqual(self.inventory.get_item_quantity("coal"), 0)  # 1 - 1 = 0
            self.assertEqual(self.inventory.get_item_quantity("torch"), 4)  # 0 + 4 = 4

        self.inventory.remove_item(item="torch", quantity=4)

        # Set current_available_recipes to contain the torch recipe
        self.inventory.current_available_recipes = {"torch": recipe}

        # Call craft_item method with the recipe name
        with patch("builtins.print") as mock_print:
            self.inventory.craft_item("torch")

            # Assert that the print statement indicates insufficient items
            mock_print.assert_called_once_with("You don't have enough stick to craft torch")

            # Assert that the inventory state remains unchanged after failed crafting
            self.assertEqual(self.inventory.get_item_quantity("stick"), 0)  # Should remain 0
            self.assertEqual(self.inventory.get_item_quantity("coal"), 0)  # Should remain 0
            self.assertEqual(self.inventory.get_item_quantity("torch"), 0)  # Should remain 0

    def test_save_inventory_to_json(self):
        self.inventory._Inventory__inventory_name = "test_inventory"
        self.inventory._Inventory__inventory_items = {
            (0, 0): {"item": "copper_sword", "quantity": 1},
            (0, 1): {"item": "copper_pickaxe", "quantity": 1},
            (0, 2): {"item": "copper_axe", "quantity": 1}
        }
        # Mock the open function to prevent writing to the actual file system
        with patch("builtins.open", mock_open()) as mock_file:
            # Call the method
            self.inventory.save_inventory_to_json()

            # Check file creation
            inventory_path = os.path.join(PLAYER_SAVE_FOLDER, f"{self.inventory._Inventory__inventory_name}.json")
            mock_file.assert_called_once_with(inventory_path, "w")

            # Verify write calls
            handle = mock_file()
            print(handle.write.call_count)
            assert handle.write.call_count == 37

            # # Capture the content written to the file
            # written_content = handle.write.call_args[0][0]

            written_content_parts = [call_args[0][0] for call_args in mock_file().write.call_args_list]

            # Concatenate the parts to reconstruct the full JSON string
            written_content = "".join(written_content_parts)

            # Check if the written content matches the expected content
            expected_content = json.dumps({
                "0;0": {"item": "copper_sword", "quantity": 1},
                "0;1": {"item": "copper_pickaxe", "quantity": 1},
                "0;2": {"item": "copper_axe", "quantity": 1}
            })
            assert written_content == expected_content

    def test_load_inventory_from_json(self):
        self.inventory._Inventory__inventory_name = "test_inventory"

        # Prepare mock serialized inventory data
        mock_serialized_inventory = {
            "0;0": {"item": "copper_sword", "quantity": 1},
            "0;1": {"item": "copper_pickaxe", "quantity": 1},
            "0;2": {"item": "copper_axe", "quantity": 1}
        }

        # Mock the existence of the JSON file and its content
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(mock_serialized_inventory))) as mock_file:
                # Call the method
                inventory_items = self.inventory.load_inventory_from_json()

                # Check if the file path is constructed correctly
                inventory_path = os.path.join(PLAYER_SAVE_FOLDER, f"{self.inventory._Inventory__inventory_name}.json")
                os.path.exists.assert_called_once_with(inventory_path)

                # Verify that the file is opened and loaded correctly
                mock_file.assert_called_once_with(inventory_path, "r")
                mock_file().read.assert_called_once()

                # Verify the loaded inventory items
                expected_inventory_items = {
                    (0, 0): {"item": "copper_sword", "quantity": 1},
                    (0, 1): {"item": "copper_pickaxe", "quantity": 1},
                    (0, 2): {"item": "copper_axe", "quantity": 1}
                }
                assert inventory_items == expected_inventory_items, "Loaded inventory items do not match expected data"


class TestEntity(unittest.TestCase):

    def setUp(self):
        # Mock idle, left, and right images
        self.idle_image = MagicMock()
        self.left_image = MagicMock()
        self.right_image = MagicMock()

        # Create an instance of Entity
        self.entity = Entity(self.idle_image, self.left_image, self.right_image)

    def test_initialization(self):
        self.assertEqual(self.entity.idle_image, self.idle_image)
        self.assertEqual(self.entity.left_image, self.left_image)
        self.assertEqual(self.entity.right_image, self.right_image)
        self.assertEqual(self.entity._x, 0)
        self.assertEqual(self.entity._y, 0)
        self.assertEqual(self.entity._velocity, [0, 0])
        self.assertEqual(self.entity._directions, {"left": False, "right": False, "up": False, "idle": False})
        self.assertEqual(self.entity._on_ground, False)
        self.assertEqual(self.entity._surrounding_blocks, [])
        self.assertEqual(self.entity._surrounding_block_rects, [])
        self.assertEqual(self.entity._health, MAX_HEALTH)

    def test_get_surrounding_blocks(self):
        # Mock surrounding chunks
        surrounding_chunks = {
            (0, 0): {(0, 0): "grass", (1, 1): "dirt"},
            (0, 1): {(1, 0): "stone", (2, 2): "wood"}
        }
        # Call the method
        self.entity._get_surrounding_blocks(surrounding_chunks)

        # Assert that surrounding blocks and block rects are correctly set
        self.assertNotEqual(self.entity._surrounding_blocks, [])
        self.assertNotEqual(self.entity._surrounding_block_rects, [])

    def test_get_x(self):
        # Set x to a known value
        self.entity._x = 10
        # Call the method
        x = self.entity.get_x()

        # Assert that the returned value matches the known value
        self.assertEqual(x, 10)

    def test_get_y(self):
        # Set y to a known value
        self.entity._y = 20
        # Call the method
        y = self.entity.get_y()

        # Assert that the returned value matches the known value
        self.assertEqual(y, 20)

    def test_set_x(self):
        # Set x to a known value
        self.entity.set_x(30)

        # Assert that x is correctly set
        self.assertEqual(self.entity._x, 30)

    def test_set_y(self):
        # Set y to a known value
        self.entity.set_y(40)

        # Assert that y is correctly set
        self.assertEqual(self.entity._y, 40)

    def test_get_velocity(self):
        # Call the method
        velocity = self.entity.get_velocity()

        # Assert that velocity is returned correctly
        self.assertEqual(velocity, [0, 0])

    def test_get_rect(self):
        # Call the method
        rect = self.entity.get_rect()

        # Assert that the rect is returned correctly
        self.assertIsInstance(rect, pygame.Rect)

    def test_get_health(self):
        # Call the method
        health = self.entity.get_health()

        # Assert that the health is returned correctly
        self.assertEqual(health, MAX_HEALTH)

    def test_set_health(self):
        # Set health to a known value
        self.entity.set_health(80)

        # Assert that health is correctly set
        self.assertEqual(self.entity._health, 80)

        # Test upper bound
        self.entity.set_health(120)
        self.assertEqual(self.entity._health, 100)

        # Test lower bound
        self.entity.set_health(-20)
        self.assertEqual(self.entity._health, 0)


class TestPlayer(unittest.TestCase):

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.player = Player()

    def tearDown(self):
        pygame.quit()

    def test_initialization(self):
        # Check if the player is properly initialized
        self.assertIsInstance(self.player, Player)

    def test_set_velocity(self):
        # Test setting velocity when moving right
        self.player._directions = {"right": True, "left": False, "up": False, "idle": False}
        self.player._Player__set_velocity()
        self.assertEqual(self.player._velocity[0], PLAYER_HORIZONTAL_SPEED)

        # Test setting velocity when moving left
        self.player._directions = {"right": False, "left": True, "up": False, "idle": False}
        self.player._Player__set_velocity()
        self.assertEqual(self.player._velocity[0], -PLAYER_HORIZONTAL_SPEED)

        # Test setting velocity when no direction keys are pressed
        self.player._directions = {"right": False, "left": False, "up": False, "idle": False}
        self.player._Player__set_velocity()
        self.assertEqual(self.player._velocity[0], 0)

    def test_jump(self):
        # Test jump when on ground and up key is pressed
        self.player._directions = {"up": True}
        self.player._on_ground = True
        self.player._Player__jump()
        self.assertEqual(self.player._velocity[1], -PLAYER_JUMP_HEIGHT)

        self.player._velocity[1] = 0
        # Test jump when on ground and up key is not pressed
        self.player._directions = {"up": False}
        self.player._on_ground = True
        self.player._Player__jump()
        self.assertEqual(self.player._velocity[1], 0)

        # Test jump when not on ground and up key is pressed
        self.player._directions = {"up": True}
        self.player._on_ground = False
        self.player._Player__jump()
        self.assertEqual(self.player._velocity[1], 0)


class TestSlimeEnemy(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.slime_enemy = SlimeEnemy()

    def tearDown(self):
        pygame.quit()

    def test_init(self):
        # Test initialization of SlimeEnemy instance
        self.assertIsNotNone(self.slime_enemy.idle_image)
        self.assertIsNotNone(self.slime_enemy.right_image)
        self.assertIsNotNone(self.slime_enemy.left_image)
        self.assertEqual(self.slime_enemy._x, 0)
        self.assertEqual(self.slime_enemy._y, 0)
        self.assertIsInstance(self.slime_enemy._rect, pygame.Rect)
        self.assertEqual(len(self.slime_enemy._velocity), 2)
        self.assertIsInstance(self.slime_enemy._directions, dict)
        self.assertFalse(self.slime_enemy._on_ground)
        self.assertEqual(self.slime_enemy._SlimeEnemy__attack_distance, 10 * 32)
        self.assertEqual(self.slime_enemy._SlimeEnemy__direction_timer, 0)
        self.assertIsNone(self.slime_enemy._SlimeEnemy__random_direction)
        self.assertEqual(self.slime_enemy._SlimeEnemy__attack_cooldown, 0)

    def test_random_movement(self):
        # Test __random_movement method
        initial_directions = self.slime_enemy._directions.copy()
        self.slime_enemy._on_ground = True
        self.slime_enemy._SlimeEnemy__random_movement()
        self.assertNotEqual(self.slime_enemy._directions, initial_directions)

    def test_jump(self):
        # Test __jump method
        self.slime_enemy._on_ground = True
        self.slime_enemy._SlimeEnemy__jump()
        self.assertFalse(self.slime_enemy._on_ground)

    def test_attack_update(self):
        # Test attack_update method
        player_mock = Mock()
        player_mock.get_rect.return_value = pygame.Rect(0, 0, 32, 32)
        player_mock.get_health.return_value = 100
        self.slime_enemy.attack_update(player_mock)
        self.assertGreaterEqual(player_mock.set_health.call_count, 0)

        # Test changes in direction and velocity
        initial_directions = self.slime_enemy._directions.copy()
        initial_velocity = self.slime_enemy._velocity.copy()
        self.slime_enemy._on_ground = True
        self.slime_enemy.attack_update(player_mock)
        self.assertNotEqual(self.slime_enemy._velocity, initial_velocity)

        # Test cooldown reduction
        initial_cooldown = self.slime_enemy._SlimeEnemy__attack_cooldown
        self.slime_enemy.attack_update(player_mock)
        self.assertLessEqual(self.slime_enemy._SlimeEnemy__attack_cooldown, initial_cooldown)

        # Test behavior when player is within attack range
        player_mock.get_rect.return_value = pygame.Rect(50, 0, 32, 32)
        self.slime_enemy.attack_update(player_mock)
        self.assertGreaterEqual(player_mock.set_health.call_count, 1)


class TestClient(unittest.TestCase):

    @patch('requests.post')
    def test_register_user(self, mock_post):
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "recovery code": "123456"}
        mock_post.return_value = mock_response

        # Instantiate the client
        client = Client()
        client.server_url = "http://localhost:5000"

        # Test registration
        success, recovery_code = client.register_user("test_user", "password")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(recovery_code, "123456")

        # Ensure requests.post was called with correct URL and data
        mock_post.assert_called_once_with("http://localhost:5000/register",
                                          json={"username": "test_user", "password": "password"})

    @patch('requests.post')
    def test_authenticate_user(self, mock_post):
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"authenticated": True}
        mock_post.return_value = mock_response

        # Instantiate the client
        client = Client()
        client.server_url = "http://localhost:5000"

        # Test authentication
        success = client.authenticate_user("test_user", "password")

        # Assertions
        self.assertTrue(success)

        # Ensure requests.post was called with correct URL and data
        mock_post.assert_called_once_with("http://localhost:5000/authenticate",
                                          json={"username": "test_user", "password": "password"})

    @patch('requests.post')
    def test_authenticate_recovery_code(self, mock_post):
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"authenticated": True}
        mock_post.return_value = mock_response

        # Instantiate the client
        client = Client()
        client.server_url = "http://localhost:5000"

        # Test recovery code authentication
        success = client.authenticate_recovery_code("test_user", "123456")

        # Assertions
        self.assertTrue(success)

        # Ensure requests.post was called with correct URL and data
        mock_post.assert_called_once_with("http://localhost:5000/authenticate_recovery_code",
                                          json={"username": "test_user", "recovery code": "123456"})

    @patch('requests.post')
    def test_reset_password(self, mock_post):
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "recovery code": "654321"}
        mock_post.return_value = mock_response

        # Instantiate the client
        client = Client()
        client.server_url = "http://localhost:5000"

        # Test password reset
        success, recovery_code = client.reset_password("test_user", "new_password")

        # Assertions
        self.assertTrue(success)
        self.assertEqual(recovery_code, "654321")

        # Ensure requests.post was called with correct URL and data
        mock_post.assert_called_once_with("http://localhost:5000/reset_password",
                                          json={"username": "test_user", "password": "new_password"})


if __name__ == '__main__':
    unittest.main()
