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
        self.on_ground = False
        self.score = 0
        self.game_awareness = BirdAwareness(self)  # collision and scoring
        self.sounds: dict = utils.load_sounds(
            sound_names=['hit', 'die', 'point', 'wing']
        )

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
        self.y = (game.rect.h - game.floor.rect.h) // 2
        self.rect.y = self.y
        self.rect.x = 0.10 * self.game.rect.w
        self.vel_y = 0  # pps

        # movement settings
        self.accel = 5.85 * self.game.rect.w  #
        self.flap_vel_y = -1.4 * self.game.rect.w  # pps
        self.max_vel_y = 1.91 * self.game.rect.w  #
        self.angle = 0  # default to no rotation
        self.max_angle = 45

        self.update(dt=0)
        self.state_memory = BirdStateMemory(self)  # for resetting

    def update(self, dt):
        """
        Update the bird's velocity, position, and rotation, check collision
        """
        in_game: bool = self.game.in_game

        # update velocity
        if in_game and self.vel_y < self.max_vel_y:
            self.vel_y += self.accel * dt

        # update position if above ground, (stop moving after hitting ground)
        if in_game and not self.on_ground:
            self.y += self.vel_y * dt
            self.rect.centery = self.y

        if not self.on_ground:
            self.game_awareness.check_floor_collision()

        if self.is_alive:
            self.game_awareness.check_pipe_collision()
            self.game_awareness.update_score()

        # render next frame and rotate image
        if not self.on_ground:
            self._update_image()

    def flap_up(self) -> None:
        if self.is_alive:
            self.vel_y = self.flap_vel_y
            self.sounds['wing'].play()

    def increment_score(self, amount: int = 1):
        if self.is_alive:
            self.score += amount
            self.sounds['point'].play()

    def die(self) -> None:
        self.angle = -90
        self.is_alive = not self.is_alive

    def revive(self):
        if not self.is_alive:
            self.state_memory.reset_bird()
            self.state_memory = BirdStateMemory(self)
        else:
            print(f"{__name__} WARNING: The bird can't revive, it's still alive")

    def _update_image(self):
        """
        Copies the next animation frame for flappy and updates it's rotation.
        The angle of rotation of the Bird depends on its current velocity.
        """
        frame: Image = self.animation_frames[0].copy()
        self.animation_frames.rotate()

        if self.game.in_game:
            self.angle: Degrees = self.vel_y * -.11
            if abs(self.angle) > self.max_angle:
                self.angle = \
                    self.max_angle if self.angle > 0 else -self.max_angle

        self.image = pg.transform.rotate(frame, self.angle)


class BirdAwareness:
    def __init__(self, bird):
        self.bird = bird
        self.game = bird.game

    def check_floor_collision(self):
        if self.bird.rect.bottom > self.game.floor.rect.top:
            self.bird.on_ground = True

            self.bird.sounds['hit'].play()

            if self.bird.is_alive:
                self.bird.die()

            if self.game.in_game:
                self.game.toggle_menu()
        else:
            self.bird.on_ground = False

    def check_pipe_collision(self) -> None:
        pipe: Pipe
        for pipe in self.game.pipes.moving_pipes:
            if (
                    pipe.is_moving
                    # bird has not passed pipe
                    and self.game.rect.left < pipe.rect.right
                     # bird is in or near pipe
                    and pipe.rect.left - self.bird.rect.right < 5
                    # bird pixels are overlapping pipe pixels
                    and pg.sprite.collide_mask(self.bird, pipe)
            ):
                self.bird.sounds['hit'].play()
                self.bird.sounds['die'].play()
                self.bird.max_angle = 90
                self.bird.die()

    def update_score(self) -> None:
        pipe: Pipe
        for pipe in self.game.pipes.moving_pipes:
            if (
                    not pipe.counted
                    and self.bird.rect.left > pipe.rect.right
            ):
                self.bird.increment_score(1)
                pipe.counted = True


class BirdStateMemory:
    """
    Class to represent state data about the bird at init (for resetting after
    death)
    """
    def __init__(self, bird: Bird):
        self.bird = bird

        attrs = [
            'is_alive', 'on_ground', 'score', 'image', 'rect', 'y', 'vel_y',
            'angle', 'max_angle'
        ]

        for attr_name in attrs:
            bird_attr = bird.__dict__[attr_name]

            if isinstance(bird_attr, (pg.Surface, pg.Rect)):
                bird_attr = bird_attr.copy()

            self.__dict__[attr_name] = bird_attr

    def reset_bird(self) -> None:
        self.bird.__dict__.update(self.__dict__)
