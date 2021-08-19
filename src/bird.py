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
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image_pool = utils.load_images(query='bird')

        self.is_alive = True
        self.color = 'blue'
        self.animation_frames = self._get_animation_frames()
        self.image = self._next_frame()
        self.rect = self.image.get_rect()

        # position / velocity
        self.x = game.rect.w // 5
        self.y = game.rect.h // 2
        self.vel_y = 0  # pps

        # movement settings
        self.accel = 1800  #
        self.flap_vel_y = -400  # pps
        self.max_vel_y = 550  #
        self.max_angle_deg = 45

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

        # render next frame and rotate image
        self._update_image()

    def flap_up(self) -> None:
        self.vel_y = self.flap_vel_y

    def change_color(self, color: str) -> None:
        self.color = color
        self.animation_frames = self._get_animation_frames()
        self.image = self._next_frame()
        self.rect = self.image.get_rect(center=self.rect.center)

    def die(self, cause: str) -> None:
        if cause == 'pipe':
            print('hit a pipe')
        else:
            print('hit the floor')

    def _get_animation_frames(self) -> deque[Image]:
        """load bird images that match the color into a deque"""
        frames = deque(
            img for name, img in self.image_pool.items() if self.color in name
        )
        return frames

    def _next_frame(self) -> Image:
        """Gets the next frame from the frames deque and rotates the deque"""
        self.animation_frames: deque

        frame: Image = self.animation_frames[0].copy()
        self.animation_frames.rotate(1)
        return frame

    def _update_image(self):
        """
        update / rotate image
        """
        frame: Image = self._next_frame()

        angle: Degrees = self.vel_y * -.2  # degrees
        if abs(angle) < self.max_angle_deg:
            self.image = pg.transform.rotate(frame, angle)
        else:
            angle = self.max_angle_deg if angle > 0 else -self.max_angle_deg
            self.image = pg.transform.rotate(frame, angle)
