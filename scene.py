import opensimplex
from all_texture_data import block_texture_data
from player import Player
from block import Block
from camera import *


class Scene:
    def __init__(self, game):
        self.game = game

        self.block_textures = self.load_block_sprites()

        self.player = Player()

        self.precise_camera_scroll = [0, 0]
        self.camera_scroll = [0, 0]

        self.camera = Camera(player=self.player)
        self.follow = Follow(camera=self.camera, player=self.player)
        self.border = Border(camera=self.camera, player=self.player)
        self.camera.setmethod(method=self.follow)

        self.all_world_blocks = {
            # "x;y" : Block(), Block(), ...
            # "x;y" represents the block position as a row and column
        }

        self.chunks = {
            # "x;y" : Block(), Block(), ...
            # "x;y" represents the chunk number as a row and column
        }

        # self.generate_world()
        # self.divide_to_chunks()

    @staticmethod
    def load_block_sprites():
        textures = {}
        atlas = pygame.transform.scale(pygame.image.load(file="assets/blocks_atlas.png").convert_alpha(),
                                       size=(BLOCK_SIZE * BLOCKS_IN_ATLAS_X, BLOCK_SIZE * BLOCKS_IN_ATLAS_Y))

        for block_type, information in block_texture_data.items():
            textures[block_type] = pygame.Surface.subsurface(atlas,
                                                             pygame.Rect(information["position"][0] * BLOCK_SIZE,
                                                                         information["position"][1] * BLOCK_SIZE,
                                                                         information["size"][0],
                                                                         information["size"][1]))
        return textures

    def generate_world(self):
        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                if y == 10:  # more than 10  blocks
                    self.all_world_blocks[f"{str(x * BLOCK_SIZE)};{str(y * BLOCK_SIZE)}"] = Block(
                        image=self.block_textures["grass"], position=(x * BLOCK_SIZE, y * BLOCK_SIZE))
                elif y > 10:
                    self.all_world_blocks[f"{str(x * BLOCK_SIZE)};{str(y * BLOCK_SIZE)}"] = Block(
                        image=self.block_textures["dirt"], position=(x * BLOCK_SIZE, y * BLOCK_SIZE))
        # for x in range(WORLD_WIDTH):
        #     y = int((opensimplex.noise2(x=x * 0.1, y=0)) * 10)
        #     print(y)
        #     self.all_world_blocks[f"{str(x * BLOCK_SIZE)};{str(y * BLOCK_SIZE)}"] = Block(
        #         image=self.block_textures["grass"], position=(x * BLOCK_SIZE, y * BLOCK_SIZE))
        #     while y < WORLD_HEIGHT:
        #         self.all_world_blocks[f"{str(x * BLOCK_SIZE)};{str(y * BLOCK_SIZE + BLOCK_SIZE)}"] = Block(
        #             image=self.block_textures["grass"], position=(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE))
        #         y += BLOCK_SIZE

    def divide_to_chunks(self):
        for position in self.all_world_blocks:
            x = self.all_world_blocks[position].rect.x // (CHUNK_WIDTH * BLOCK_SIZE)
            y = self.all_world_blocks[position].rect.y // (CHUNK_HEIGHT * BLOCK_SIZE)
            if f"{str(x)};{str(y)}" not in self.chunks:
                self.chunks[f"{str(x)};{str(y)}"] = set()
            self.chunks[f"{str(x)};{str(y)}"].add(self.all_world_blocks[position])

    def generate_chunk(self, offset):
        current_chunk_blocks = []
        for x in range(CHUNK_WIDTH):
            for y in range(CHUNK_HEIGHT):
                real_x = (offset[0] + x) * BLOCK_SIZE
                real_y = (offset[1] + y) * BLOCK_SIZE
                print(real_x, real_y)
                if real_y == 64:
                    current_chunk_blocks.append(Block(image=self.block_textures["grass"], position=(real_x, real_y)))
                elif real_y > 50:
                    current_chunk_blocks.append(Block(image=self.block_textures["dirt"], position=(real_x, real_y)))
        return current_chunk_blocks

    # def find_player_chunk(self):
    #     player_chunk_pos = [
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 2),  # topleft
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 2),  # top
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 2),  # topright
    #
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # left
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # mid
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # right
    #
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # bottomleft
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # bottom
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # bottomright
    #     ]
    #
    #     keys = [f"{offset[0]};{offset[1]}" for offset in player_chunk_pos]
    #
    #     chunks = [self.chunks.get(key, []) for key in keys]
    #
    #     return chunks

    # def generate_chunk(self, offset):
    #     chunk_offset = [0, 0]
    #     chunk_offset[0] = int(offset[0]) * CHUNK_WIDTH * BLOCK_SIZE
    #     chunk_offset[1] = int(offset[1]) * CHUNK_HEIGHT * BLOCK_SIZE
    #
    #     blocks = []
    #     for x in range(CHUNK_WIDTH + 1):
    #         for y in range(CHUNK_HEIGHT + 1):
    #             blocks.append(
    #                 Block(image=self.block_textures["grass"], position=(x + chunk_offset[0], y + chunk_offset[1])))
    #     return blocks

    # def find_player_chunk(self):
    #     surrounding_chunks = [
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # topleft
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # topright
    #
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # left
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # mid
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # right
    #
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottomleft
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom
    #         (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
    #          self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottomright
    #     ]
    #
    #     chunks = {}
    #     for offset in surrounding_chunks:
    #         if f"{offset[0]};{offset[1]}" not in chunks.keys():
    #             chunks[f"{offset[0]};{offset[1]}"] = self.generate_chunk(offset=offset)
    #
    #     return chunks

    # def render(self):
    #     self.precise_camera_scroll[0] = self.player.rect.x - WINDOW_WIDTH / 2 + self.player.rect.width / 2
    #     self.precise_camera_scroll[1] = self.player.rect.y - WINDOW_HEIGHT / 2 + self.player.rect.height / 2
    #
    #     if self.player.rect.centerx <= WINDOW_WIDTH / 2:
    #         self.precise_camera_scroll[0] = 0
    #
    #     self.camera_scroll[0] = int(self.precise_camera_scroll[0])
    #     self.camera_scroll[1] = int(self.precise_camera_scroll[1])
    #
    #     self.game.screen.fill("lightblue")
    #
    #     chunks = self.find_player_chunk()
    #     for chunk in chunks:
    #         self.game.screen.fblits([(block.image, (
    #             int(block.position[0] * BLOCK_SIZE) - self.camera_scroll[0], int(block.position[1] * BLOCK_SIZE) - self.camera_scroll[1])) for block in chunks[chunk]])
    #
    #     self.player.movement(chunks=chunks)
    #     self.player.render(screen=self.game.screen, offset=self.camera_scroll)

    def render(self):
        self.precise_camera_scroll[0] = self.player.rect.x - WINDOW_WIDTH / 2 + self.player.rect.width / 2
        self.precise_camera_scroll[1] = self.player.rect.y - WINDOW_HEIGHT / 2 + self.player.rect.height / 2

        if self.player.rect.centerx <= WINDOW_WIDTH / 2:  # checking for border on left side - #TODO check for right side
            self.precise_camera_scroll[0] = 0

        self.camera_scroll[0] = int(self.precise_camera_scroll[0])
        self.camera_scroll[1] = int(self.precise_camera_scroll[1])

        self.game.screen.fill("lightblue")

        # self.find_player_chunk()
        # for chunk in self.find_player_chunk():
        #     self.game.screen.fblits(
        #         [(block.image,
        #           (int(block.position[0]) - self.camera_scroll[0], int(block.position[1]) - self.camera_scroll[1]))
        #          for block in chunk])

        # chunks = self.find_player_chunk()
        # for chunk_position in chunks:
        #     for block in chunks[chunk_position]:
        #         self.game.screen.blit(block.image, (block.position[0] - self.camera_scroll[0], block.position[1] - self.camera_scroll[1]))

        neighbour_chunk_offsets = [
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # topleft
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # top
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) + 1),  # topright

            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # left
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # mid
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE)),  # right

            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) - 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottomleft
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE),
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottom
            (self.player.position[0] // (CHUNK_WIDTH * BLOCK_SIZE) + 1,
             self.player.position[1] // (CHUNK_HEIGHT * BLOCK_SIZE) - 1),  # bottomright
        ]

        collision_chunks = {}
        for offset in neighbour_chunk_offsets:
            print(offset)
            if f"{offset[0]};{offset[1]}" not in self.chunks:
                self.chunks[f"{offset[0]};{offset[1]}"] = self.generate_chunk(offset)
            self.game.screen.fblits(
                [(block.image, (block.position[0] - self.camera_scroll[0], block.position[1] - self.camera_scroll[1]))
                 for block in self.chunks[f"{offset[0]};{offset[1]}"]])
            collision_chunks[f"{offset[0]};{offset[1]}"] = (self.chunks.get(f"{offset[0]};{offset[1]}", []))

        self.player.movement(chunks=collision_chunks)
        self.player.render(screen=self.game.screen, offset=self.camera_scroll)
