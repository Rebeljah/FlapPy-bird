"""
This module contains code for a flappy bird. The bird is always falling towards
the ground. The player controls the bird by tapping, each tap will cause the
bird to 'jump' in mid-air.
"""

import pygame as pg
from pygame.sprite import Sprite

from collections import deque
from typing import Union

from pipe import Pipe
import utils

# Typing
Image = pg.Surface
Degrees = Union[float, int]


class Bird(Sprite):
    def __init__(self, game, sprite_name: str = 'bluebird'):
        super().__init__()
        self.game = game

        self.sprite_name = sprite_name
        self.is_alive = True
        self.score = 0
        self.collision = BirdCollider(self)

        # Images and rectangle
        self.animation_frames = deque(
            utils.scale_image(img, 0.118, self.game.rect.w, 'w')
            for img in utils.load_sprite_frames(
                sprite_name=self.sprite_name
            )
        )

        self.image = self.animation_frames[0].copy()
        self.rect = self.image.get_rect()

        # position / velocity
        self.x = game.rect.w // 5
        self.y = (game.rect.h - game.floor.rect.h) // 2
        self.rect.topleft = self.x, self.y
        self.vel_y = 0  # pps

        # movement settings
        self.accel = 5.903 * self.game.rect.w  #
        self.flap_vel_y = -1.389 * self.game.rect.w  # pps
        self.max_vel_y = 1.91 * self.game.rect.w  #
        self.angle = 0  # default to no rotation
        self.max_angle = 45

        self.update(dt=0)

    def update(self, dt):
        """
        Update the bird's velocity, position, and rotation, check collision
        """
        # update velocity
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.accel * dt

        # update position
        self.y += self.vel_y * dt
        self.rect.center = (self.x, self.y)

        self.collision.check_collision()

        # render next frame and rotate image
        self._update_image()

    def flap_up(self) -> None:
        self.vel_y = self.flap_vel_y

    def die(self) -> None:
        self.is_alive = False
        self.angle = -90
        self.game.toggle_menu()

    def _update_image(self):
        """
        Copies the next animation frame for flappy and updates it's rotation.
        The angle of rotation of the Bird depends on its current velocity.
        """

        frame: Image = self.animation_frames[0].copy()
        self.animation_frames.rotate()

        if self.is_alive:
            self.angle: Degrees = self.vel_y * -.11
            if abs(self.angle) > self.max_angle:
                self.angle = \
                    self.max_angle if self.angle > 0 else -self.max_angle
        else:
            self.angle = -90

        self.image = pg.transform.rotate(frame, self.angle)


class BirdCollider:
    def __init__(self, bird):
        self.bird = bird
        self.game = bird.game

    def check_collision(self):
        self._check_floor_collision()
        self._check_pipe_collision()
        self._update_score()

    def _check_floor_collision(self):
        """
        """
        # check ground collision
        if self.bird.rect.bottom > self.game.floor.rect.top:
            self.bird.die()

    def _check_pipe_collision(self) -> None:
        """
        """
        pipe: Pipe
        for pipe in self.game.pipes:
            if (
                    pipe.is_moving
                    # bird has not passed pipe
                    and self.game.rect.left < pipe.rect.right
                    # bird is in or near pipe
                    and pipe.rect.left - self.game.rect.right < 50
                    # bird pixels are overlapping pipe pixels
                    and pg.sprite.collide_mask(self.bird, pipe)
            ):
                self.bird.die()

    def _update_score(self) -> None:
        """
        """
        pipe: Pipe
        for pipe in self.game.pipes:
            if (
                    not pipe.counted
                    and self.bird.rect.left > pipe.rect.right
            ):
                pipe.counted = True
                self.bird.score += pipe.score_value
                print(self.bird.score)
