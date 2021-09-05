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

        self.image_pool = utils.load_images(query='pipe')
        self.pipe_image = self._get_pipe_image()

        self.pipe_gap_height = int(self.game.rect.h * .22)
        self.pipe_spacing = int(self.game.rect.w * .42)
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

        # UPDATE ALL PIPES
        super().update(dt)

    def reset(self):
        self.empty()
        self.waiting_pipes.clear()
        self.moving_pipes.clear()

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
                height = self.game.rect.h
                return utils.scale_image(image, 0.625, height, 'h')
        else:
            raise ValueError(
                f"Could not find '{color}' in pipe image pool keys"
            )

    def _spawn_new_pipe(self):
        gap_bottom_y = random.randrange(
            start=self.pipe_gap_height,
            stop=self.game.floor.rect.top
        )
        pipe = Pipe(self, gap_bottom_y)
        self.waiting_pipes.append(pipe)
        self.add(pipe)

    def _move_next_pipe(self):
        self.moving_pipes.append(self.waiting_pipes.popleft())
        self.moving_pipes[-1].is_moving = True


class Pipe(Sprite):
    def __init__(self, spawner: PipeSpawner, gap_bottom_y, point_value: int = 1):
        """
        A Pipe represents the upper and lower portion of a pipe obstacle.

        """
        # sprite init
        super().__init__()

        # parent reference
        self.spawner = spawner

        # used for scoring
        self.point_value: int = point_value
        self.counted: bool = False

        # position
        self.rect = self._create_rect()
        self.rect.bottom = gap_bottom_y + spawner.pipe_image.get_rect().h
        self.rect.x = spawner.game.rect.right
        self.x, self.y = self.rect.topleft

        # movement
        self.is_moving = False
        self.vel_x = spawner.pipe_vel_x

        # image
        self.image = self._render_image()

        # mask collision
        self.mask = pg.mask.from_surface(self.image, 15)

    def update(self, dt: float) -> None:
        if self.is_moving:
            self.x += self.vel_x * dt
            self.rect.x = self.x

        # delete pipe that has gone off-screen
        if self.rect.right < 0:
            self.kill()  # bye bye pipey

    def _create_rect(self) -> pg.Rect:
        """
        create a rectangle that will fit the pipe obstacle
        """
        rect = self.spawner.pipe_image.get_rect()
        rect.h *= 2  # double height to fit 2 pipes
        rect.h += self.spawner.pipe_gap_height  # increase height to fit gap

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
            (pipe_top_img, pipe_image.get_rect(topleft=(0, 0))),
            (pipe_btm_img, pipe_image.get_rect(bottom=self.rect.h))
        ])
        return image
