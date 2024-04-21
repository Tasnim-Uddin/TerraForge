import pygame

PLAYER_SAVE_FOLDER = "local_player_save_files"
WORLD_SAVE_FOLDER = "local_world_save_files"

pygame.init()
WINDOW_WIDTH = pygame.display.Info().current_w #* 0 + 1280
WINDOW_HEIGHT = pygame.display.Info().current_h #* 0 + 720

FRAMES_PER_SECOND = 60


HORIZONTAL_SCROLL_DELAY_FACTOR = 10
VERTICAL_SCROLL_DELAY_FACTOR = 10


BLOCK_SIZE = 32

# Number of blocks per chunk
CHUNK_WIDTH = 32
CHUNK_HEIGHT = 32

# Number of blocks in the world
WORLD_WIDTH = 100000
WORLD_HEIGHT = 1000

# Player related
PLAYER_HORIZONTAL_SPEED = 10
GRAVITY = 0.5
PLAYER_JUMP_HEIGHT = 11
PLAYER_ATTACK_INTERVAL = 0.1

REACH = 5  # 5 blocks

# Inventory
COLUMN_SLOTS = 9
ROW_SLOTS = 3


# SlimeEnemy related
ENEMY_HORIZONTAL_SPEED = 2
ENEMY_JUMP_HEIGHT = 15
SLIME_ATTACK_INTERVAL = 10


MAX_HEALTH = 100

# World levels in terms of blocks
DIRT_LEVEL = 0
CAVE_LEVEL = 10
DEEP_CAVE_LEVEL = 350

# Ore levels in terms of blocks
COAL_LEVEL = 20
IRON_LEVEL = 80
GOLD_LEVEL = 150
EMERALD_LEVEL = 200
DIAMOND_LEVEL = 270

# Ore spawn rates
COAL_SPAWN_RATE = 0.05
IRON_SPAWN_RATE = 0.03
GOLD_SPAWN_RATE = 0.02
EMERALD_SPAWN_RATE = 0.0001
DIAMOND_SPAWN_RATE = 0.01

