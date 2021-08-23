"""
Module to represent moving pipe obstacles that move towards the player.
"""

import pygame as pg
from pygame.sprite import Sprite, Group
import random
from collections import deque

from typing import Optional

import utils

# Typing
Image = pg.Surface


class PipeSpawner(Group):
    """class for managing pipes"""

    def __init__(self, game):
        super().__init__()
        self.game = game

        self.waiting_pipes = deque(maxlen=2)
        self.moving_pipes = deque()
        self.total_spawned = 0

        self.image_pool = utils.load_images(query='pipe')
        self.pipe_image = self._get_pipe_image()

        self.pipe_gap_height = int(self.game.rect.h * .25)
        self.pipe_spacing = int(self.game.rect.w * .35)
        self.pipe_vel_x = int(self.game.rect.w * -.33)

    def update(self, dt) -> None:
        # check if another pipe should be spawned in waiting
        while len(self.waiting_pipes) < self.waiting_pipes.maxlen:
            self._spawn_new_pipe()

        # if no pipes are moving, send one from waitlist
        if len(self.moving_pipes) == 0:
            self._move_next_pipe()

        last_pipe_right = self.moving_pipes[-1].rect.right
        next_pipe_left = self.waiting_pipes[0].rect.left

        # send new pipe when last pipe is far enough away.
        if abs(last_pipe_right - next_pipe_left) > self.pipe_spacing:
            self._move_next_pipe()

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
                image = img.copy()
                height = self.game.rect.h * 0.625
                return utils.scale_image(image, 1, height, 'h')
        else:
            raise ValueError(
                f"Could not find '{color}' in pipe image pool keys"
            )

    def _spawn_new_pipe(self):
        gap_bottom_y = random.randrange(
            start=self.pipe_gap_height,
            stop=self.game.rect.h - self.game.floor.rect.h
        )
        pipe = Pipe(self, gap_bottom_y)
        self.total_spawned += 1
        self.waiting_pipes.append(pipe)
        self.add(pipe)

    def _move_next_pipe(self):
        pipe = self.waiting_pipes.popleft()
        pipe.is_moving = True
        self.moving_pipes.append(pipe)


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
        self.is_moving = False
        self.vel_x = spawner.pipe_vel_x

        # mask collision
        self.mask = pg.mask.from_surface(self.image, 15)

        # used for scoring
        self.score_value: int = 1
        self.counted: bool = False

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
