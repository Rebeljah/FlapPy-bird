"""Module to hold code for game menu and overlays"""

import pygame as pg
from pygame.sprite import Sprite, Group
import os
from abc import ABC, abstractmethod

from typing import Iterable, Optional, Union

import utils


class UIGroup(Group, ABC):
    """
    Class to represent a group of sprites that make up a certain UI view.
    UIGroups can be treated like a pygame Group object. To build a new UI Group,
    create a new class and override the _build method. the _build method
    is ued for initializing and configuring UI elements before adding them to
    the UIGroup
    """
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _build(self):
        """Configure and place individual Sprites into this UIGroup"""
        pass


class Menu(UIGroup):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self._build()

    def _build(self):
        start_button = Button(
            game=self.game,
            button_name='startbutton',
            function=self.game.toggle_menu,
            scale=.25,
            center=self.game.play_area.center,
        )
        self.add(start_button)


class Overlays(UIGroup):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self._build()

    def _build(self):
        player_score = ScoreDisplay(
            game=self.game,
            digit_w_scale=0.055,
            centerx=self.game.rect.centerx,
            y=self.game.rect.h * 0.01
        )
        self.add(player_score)


class UIElement(Sprite, ABC):
    def __init__(self, game, scale, sprite_name='', **rect_position):
        f"""
        """
        super().__init__()
        self.game = game
        self.scale = scale
        if sprite_name:
            self.sprite_name = sprite_name
        self.rect_position = rect_position

    @abstractmethod
    def _build(self) -> None:
        """"""
        pass


class Button(UIElement):
    def __init__(
            self,
            game,
            button_name: str,
            function,
            scale: float,
            **rect_position
    ):
        f"""
        Represents a button that can be clicked and execute a function.
        
        button image file should be stored in the ../img folder and be named like:
        (button_name)button-(specific) 
        (e.g. 
        -full filename: startbutton-clicked.png
        --- button_name = 'startbutton'
        AND
        -full filename: leaderboardbutton-unclicked.png
        --- button_name = 'leaderboardbutton'
        """
        super().__init__(game, scale, button_name, **rect_position)

        self.function = function
        self._build()

    def update(self, mouse_down: bool, mouse_up_pos, mouse_down_pos) -> None:
        """
        Check if the button is being clicked and execute function on button
        release
        """
        # is button being clicked
        if mouse_down:
            if mouse_down_pos and self.rect.collidepoint(*mouse_down_pos):
                self.image = self.image_clicked

        else:
            # check for mouse_up on button
            if mouse_up_pos and self.rect.collidepoint(*mouse_up_pos):
                self._do_function()

            self.image = self.image_unclicked

    def _build(self) -> None:
        # load all button images that match the given button name
        # append button to name before querying files to ensure proper images
        # are loaded.

        images: dict[str, pg.Surface] = utils.load_images(
            query=self.sprite_name
        )

        # Scale button width to a percentage of window width, ratio is preserved.
        self.image_unclicked = utils.scale_image(
            images[f"{self.sprite_name}-unclicked"],
            self.scale, self.game.rect.w
        )

        self.image_clicked = utils.scale_image(
            images[f"{self.sprite_name}-clicked"],
            self.scale, self.game.rect.w
        )

        # default button to unclicked
        self.image = self.image_unclicked
        # positioning
        self.rect = self.image.get_rect(**self.rect_position)

    def _do_function(self):
        self.function()


class ScoreDisplay(UIElement):
    def __init__(self, game, digit_w_scale, **rect_position):
        super().__init__(game, digit_w_scale, **rect_position)

        self.score: int = 0
        self._build()

    def update(self) -> None:
        bird_score: int = self.game.bird.score

        if self.score != bird_score:
            self.score = bird_score

            # load digit surfaces into list in the order they appear in score
            digits_to_print = [self.digits[n] for n in str(self.score)]

            # resize surface to fit all digits with some space between digits
            new_width = sum(image.get_width() + 2 for image in digits_to_print)
            self.image = pg.Surface((new_width, self.rect.h), pg.SRCALPHA)
            self.rect = self.image.get_rect(center=self.rect.center)

            # blit digits to self using their order to space them.
            digit_width = digits_to_print[0].get_width()
            for i, digit in enumerate(digits_to_print):
                rect = digit.get_rect(left=digit_width * i)
                if rect.left > 0:
                    rect.left += 1  # add buffer between letters
                self.image.blit(digit, rect)

    def _build(self) -> None:
        digit_filenames = [f"{n}.png" for n in range(10)]
        digits: dict = utils.load_images(digit_filenames)

        digit_images = utils.make_all_same_size(digits.values())
        digit_images = [
            utils.scale_image(digit, self.scale, self.game.rect.w)
            for digit in digit_images
        ]
        self.digits = {
            k: v for k, v in zip(digits.keys(), digit_images)
        }

        self.image = self.digits['0']
        self.rect = self.image.get_rect(**self.rect_position)
        self.update()
