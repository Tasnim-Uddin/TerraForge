import pygame as pg
from global_constants import *
from current_events import EventManager


class Player(pg.sprite.Sprite):
    def __init__(self, block_group, position, image=pg.Surface(size=(BLOCK_SIZE, 2 * BLOCK_SIZE))):
        super().__init__()

        self.block_group = block_group
        self.image = pg.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE * 2))
        self.rect = self.image.get_rect(topleft=position)
        self.velocity = pg.math.Vector2()
        self.velocity.x = 0

    def input(self):
        for event in EventManager.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    self.velocity.x = 1
                if event.key == pg.K_a:
                    self.velocity.x = -1
            if event.type == pg.KEYUP:
                if event.key == pg.K_d or event.key == pg.K_a:
                    self.velocity.x = 0

    def horizontal_collision(self):
        collided_block = pg.sprite.spritecollideany(sprite=self, group=self.block_group)
        if collided_block is not None:
            if self.velocity.x > 0:
                self.rect.right = collided_block.rect.left
            if self.velocity.x < 0:
                self.rect.left = collided_block.rect.right

    def vertical_collision(self):
        collided_block = pg.sprite.spritecollideany(sprite=self, group=self.block_group)
        if collided_block is not None:
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.rect.bottom = collided_block.rect.top

    def movement(self):
        self.input()

        self.velocity.y += 1

        self.rect.x += self.velocity.x
        self.horizontal_collision()

        self.rect.y += self.velocity.y
        self.vertical_collision()

    def update(self):
        self.movement()
