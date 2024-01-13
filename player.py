import pygame as pg
from global_constants import *
from current_events import EventManager


class Player(pg.sprite.Sprite):
    def __init__(self, block_group, position, image=pg.Surface(size=(BLOCK_SIZE, 2 * BLOCK_SIZE))):
        super().__init__()

        self.block_group = block_group
        self.image = pg.transform.scale(surface=image, size=(BLOCK_SIZE, BLOCK_SIZE * 2))
        self.rect = self.image.get_rect(topleft=position)
        self.camera_scroll = pg.math.Vector2()
        self.velocity = pg.math.Vector2()
        self.on_ground = False

    def input(self):
        for event in EventManager.events:  # noqa
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    self.velocity.x = HORIZONTAL_SPEED
                if event.key == pg.K_a:
                    self.velocity.x = -HORIZONTAL_SPEED
                if event.key == pg.K_SPACE:
                    if self.on_ground:  # jumping allowed only when the player is on the ground
                        self.on_ground = False
                        self.velocity.y -= JUMP_HEIGHT
            if event.type == pg.KEYUP:
                if event.key == pg.K_d or event.key == pg.K_a:
                    self.velocity.x = 0

    def horizontal_collision(self):
        collided_block = pg.sprite.spritecollideany(sprite=self, group=self.block_group)  # noqa
        if collided_block is not None:
            if self.velocity.x > 0:
                self.rect.right = collided_block.rect.left
            if self.velocity.x < 0:
                self.rect.left = collided_block.rect.right

    def vertical_collision(self):
        collided_block = pg.sprite.spritecollideany(sprite=self, group=self.block_group)  # noqa
        if collided_block is not None:
            if self.velocity.y > 0:
                self.velocity.y = 0
                self.rect.bottom = collided_block.rect.top
                self.on_ground = True

    def movement(self):
        self.input()

        if self.velocity.y <= TERMINAL_VELOCITY:
            self.velocity.y += 1

        self.rect.x += self.velocity.x
        self.horizontal_collision()

        self.rect.y += self.velocity.y
        self.vertical_collision()

        self.get_camera_scroll()

    def get_camera_scroll(self):
        self.camera_scroll.x = self.rect.x - WINDOW_WIDTH/2 + self.rect.width/2
        self.camera_scroll.y = self.rect.y - WINDOW_HEIGHT/2 + self.rect.height/2
        return self.camera_scroll

    def update(self):
        self.movement()
