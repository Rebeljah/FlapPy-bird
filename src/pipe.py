"""
Module to represent moving pipe obstacles that move towards the player.
"""

import pygame as pg
from pygame.sprite import Sprite, Group
import random
from typing import Optional

import utils

# Typing
Image = pg.Surface


class PipeSpawner(Group):
    """class for managing pipes"""
    def __init__(self, game):
        super().__init__()

        self.game = game

        self.image_pool = utils.load_images(query='pipe')
        self.pipe_image = self._get_pipe_image()

        self.pipe_gap_height = self.game.rect.h // 4.5
        self.pipe_vel_x = -100

    def update(self, dt) -> None:
        pipe: Pipe

        if len(self.sprites()) == 0:
            self._spawn_pipe()

        super().update(dt)

    def _get_pipe_image(self, color: Optional[str] = '') -> Image:
        """
        Returns the pipe image that matches the given color. Raises ValueError
        when color is not found. If no color arg is passed, a random color
        is chosen.
        """
        if not color:
            color = random.choice(('red', 'green'))

        for name, img in self.image_pool.items():
            if color in name:
                return img.copy()
        else:
            raise ValueError(
                f"Could not find '{color}' in pipe image pool keys"
            )

    def _spawn_pipe(self):
        gap_bottom_y = random.randrange(
            start=self.pipe_gap_height,
            stop=self.game.rect.h - self.game.foreground.rect.h
        )
        pipe = Pipe(self, gap_bottom_y)
        self.add(pipe)


class Pipe(Sprite):
    def __init__(self, spawner: PipeSpawner, gap_bottom_y):
        """
        A Pipe represents the upper and lower portion of a pipe obstacle.

        """
        super().__init__()
        self.spawner = spawner

        self.rect = self._create_rect()
        self.image = self._render_image()

        # position
        self.rect.bottom = gap_bottom_y + spawner.pipe_image.get_rect().h
        self.rect.x = spawner.game.rect.right
        self.x, self.y = self.rect.topleft

        # movement
        self.is_moving = True
        self.vel_x = spawner.pipe_vel_x

        # mask collision
        self.mask = pg.mask.from_surface(self.image, 15)

    def update(self, dt: float) -> None:
        if self.is_moving:
            self.x += self.vel_x * dt
            self.rect.x = self.x

        # delete pipe that has gone off-screen
        if self.rect.right < self.spawner.game.rect.left:
            self.kill()  # bye bye pipy

    def _create_rect(self) -> pg.Rect:
        """
        create a rectangle that will fit the pipe obstacle
        """
        rect = self.spawner.pipe_image.get_rect()
        rect.h *= 2
        rect.h += self.spawner.pipe_gap_height

        return rect

    def _render_image(self) -> Image:
        """
        render pipe obstacle surface
        """
        # creating image
        image = pg.Surface(self.rect.size, pg.SRCALPHA)

        pipe_image = self.spawner.pipe_image
        pipe_btm_img = pipe_image
        pipe_top_img = pg.transform.rotate(pipe_image, 180)

        image.blits([
            (pipe_btm_img, pipe_image.get_rect(bottomleft=self.rect.bottomleft)),
            (pipe_top_img, pipe_image.get_rect(topleft=self.rect.topleft))
            ])
        return image
