import pygame

from global_constants import *


class QuadTree:
    def __init__(self, capacity=4):
        boundary = CHUNK_WIDTH * CHUNK_HEIGHT * BLOCK_SIZE
        self.root = QuadTreeNode(boundary, capacity)

    def insert(self, entity):
        return self.root.insert(entity)

    def query(self, rect):
        found_entities = []
        self.root.query(rect, found_entities)
        return found_entities

    def update(self, entity):
        # Remove entity from the tree and insert it again to update its position
        # This could be optimized by updating the tree directly
        self.remove(entity)
        self.insert(entity)

    def remove(self, entity):
        self.root.entities.remove(entity)


class QuadTreeNode:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # Rectangle representing the node's boundary
        self.capacity = capacity  # Maximum number of entities in a node
        self.entities = []  # List of entities in this node
        self.children = None  # Children nodes

    def insert(self, entity):
        if not self.boundary.colliderect(entity.rect):
            return False  # Entity is outside the node's boundary

        if len(self.entities) < self.capacity:
            self.entities.append(entity)
            return True

        if self.children is None:
            self.subdivide()

        for child in self.children:
            if child.insert(entity):
                return True

        # If the entity cannot fit into any child node, it stays in this node
        self.entities.append(entity)
        return True

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.w // 2
        h = self.boundary.h // 2

        nw_boundary = pygame.Rect(x, y, w, h)
        ne_boundary = pygame.Rect(x + w, y, w, h)
        sw_boundary = pygame.Rect(x, y + h, w, h)
        se_boundary = pygame.Rect(x + w, y + h, w, h)

        self.children = [
            QuadTreeNode(nw_boundary, self.capacity),
            QuadTreeNode(ne_boundary, self.capacity),
            QuadTreeNode(sw_boundary, self.capacity),
            QuadTreeNode(se_boundary, self.capacity)
        ]

    def query(self, rect, found_entities):
        if not self.boundary.colliderect(rect):
            return

        for entity in self.entities:
            if entity.rect.colliderect(rect):
                found_entities.append(entity)

        if self.children is not None:
            for child in self.children:
                child.query(rect, found_entities)
