import Engine, Classes, random, math, json
from perlin_noise import *

world_data = {}

tiles = []

tile_rects = []

CHUNK_SIZE = 8

#get patterns of structures
with open('C:\JustGoUp\Resources\Settings\patterns.json', 'r') as file:
    patterns = json.load(file)


seed = random.randint(-1000000, 1000000)

biomes = ['plains', 'hills', 'superflat']

depth = 2

amplifier = 1

#add depth to the world via multiple noises combined
noises = [PerlinNoise(octaves=(x+1)*7, seed = seed) for x in range(depth)]

treenoise = PerlinNoise(octaves=20, seed = seed)

cavenoise = PerlinNoise(octaves=10, seed = seed)

def generate_chunk(x, y):
    global seed, noise1, noise2, noise3, noise4
    chunk_data = []

    random.seed(seed)
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos
            target_y = y * CHUNK_SIZE + y_pos

            noise_val = 0

            for i, noise in enumerate(noises):
                noise_val += noise([target_x/100 * amplifier]) * 1/(i+1)

            tree_val = treenoise([target_x/23])
            cave_val = cavenoise([target_x/(50+target_y/5), target_y/(50+target_y/5)])

            height = int(noise_val * 20)

            tile_type = ''  
            if target_y > 8 - height and target_y < 12 - height:
                tile_type = 'dirt'
            if target_y >= 12 - height:
                tile_type = 'stone'
            if target_y == 8 - height:
                tile_type = 'grass'
            if target_y == 7 - height:
                if tree_val > 0.15:
                    pending_structures.append([[target_x, target_y], 'tree', chunk_data])
                elif tree_val > 0.1 and tree_val < 0.15:
                    tile_type = 'rock'
                elif tree_val < -0.2:
                    tile_type = 'berrybush'
                elif tree_val > 0 and tree_val < 0.1:
                    tile_type = 'bush'

            if cave_val > 0.1 and target_y > 10:
                tile_type = ''

            if target_y == 256:
                tile_type = 'bedrock'

            if target_y > 256:
                tile_type = ''
            if tile_type:
                chunk_data.append([[target_x, target_y], tile_type])

            # for y in range(5):
            #     for x in range(7):
            #         # target_x, target_y = the "location" of the chunk, x, y = position of block
            #         target_x = x - 1 + int(round(-scroll[0] / (CHUNK_SIZE * 50)))
            #         target_y = y - 1 + int(round(-scroll[1] / (CHUNK_SIZE * 50)))
            #         target_chunk = str(target_x) + ';' + str(target_y)
            #
            #         if not target_chunk in world_data:
            #             world_data[target_chunk] = generate_chunk(target_x, target_y)
            #
            #         for tile in world_data[target_chunk][:]:
            #             window.blit(Engine.images[f'{tile[1]}'],
            #                         (tile[0][0] * 50 + scroll[0], tile[0][1] * 50 + scroll[1]))
            
    return chunk_data

def spawn_patterns(x, y, pattern, chunk_data):
    #x, y = the pattern's origin
    for block in patterns[pattern]:
        chunk_data.append([[block[0]+x, block[1]+y], block[2]])

def spawn_water(x, y, pattern, chunk_data):
    #x, y = the pattern's origin
    for block in patterns[pattern]:
        chunk_data.append([[block[0]+x, block[1]+y], block[2]])

pending_structures = []