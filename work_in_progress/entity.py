import pygame
from global_constants import *


class Entity:
    def __init__(self, block, position):
        self.block = block
        self.position = position
