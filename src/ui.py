"""Module to hold code for game menu and overlays"""

import pygame as pg
from pygame.sprite import Sprite, Group

from abc import ABC, abstractmethod
from typing import Union

import utils

# Typing
Kwargs = dict


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
        self.show_title = True
        self.show_death_banner = False
        self._build()

    def _build(self):
        self.start_button = Button(
            game=self.game,
            button_name='startbutton',
            function=self.game.toggle_menu,
            scale=.25,
            center=self.game.play_area.center,
        )
        self.add(self.start_button)

        title_banner = utils.load_image('titlebanner')
        title_banner = utils.scale_image(title_banner, 0.45, self.game.rect.w, 'w')
        self.title_banner = utils.StaticImage(
            image=title_banner,
            centerx=self.start_button.rect.centerx,
            bottom=self.start_button.rect.top - 10
        )
        self.add(self.title_banner)

        lose_banner = utils.load_image('gameover')
        lose_banner = utils.scale_image(lose_banner, 0.45, self.game.rect.w, 'w')
        self.lose_banner = utils.StaticImage(
            image=lose_banner,
            centerx=self.start_button.rect.centerx,
            bottom=self.start_button.rect.top - 10
        )
        self.add(self.lose_banner)

        self.scoreboard = ScoreBoard(
            self.game,
            0.40,
            centerx=self.game.rect.centerx,
            bottom=self.game.floor.rect.top - 10
        )
        self.add(self.scoreboard)

    def update(self, *args) -> None:
        self.empty()

        self.add(self.start_button)
        self.start_button.update(*args)

        if self.game.bird.is_alive:
            self.add(self.title_banner)
        else:
            self.add(self.lose_banner)
            self.add(self.scoreboard)


class HUD(UIGroup):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self._build()

    def update(self, *args) -> None:
        if self.game.in_game:
            self.add(self.player_score)
        else:
            self.player_score.kill()

        super().update(*args)

    def _build(self):
        self.player_score = ScoreHUD(
            game=self.game,
            digit_w_scale=0.055,
            centerx=self.game.rect.centerx,
            y=self.game.rect.h * 0.01
        )
        self.add(self.player_score)


class UIElement(Sprite, ABC):
    def __init__(self, game, scale, sprite_name=None, **rect_position):
        f"""
        """
        super().__init__()
        self.game = game
        self.scale = scale
        self.sprite_name = sprite_name or ''
        self.rect_position = rect_position

    @abstractmethod
    def _build(self) -> None:
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

    # def update(self, mouse_down: bool, mouse_up_pos, mouse_down_pos) -> None:
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
        image_name = f"{self.sprite_name}-unclicked"
        self.image_unclicked = utils.scale_image(
            images[image_name],
            self.scale,
            self.game.rect.w
        )

        image_name = f"{self.sprite_name}-clicked"
        self.image_clicked = utils.scale_image(
            images[image_name],
            self.scale,
            self.game.rect.w
        )

        # default button to unclicked
        self.image = self.image_unclicked
        # positioning
        self.rect = self.image.get_rect(**self.rect_position)

    def _do_function(self):
        """Call the Button's function attribute"""
        self.function()


class ScoreHUD(UIElement):
    def __init__(self, game, digit_w_scale, **rect_position):
        super().__init__(game, digit_w_scale, **rect_position)

        self.score = 0
        self._build()
        self.update(score=self.score)

    def update(self, score) -> None:
        if self.score != score:
            self.score = score

            # load digit surfaces into list in the order they appear in score
            digits_to_print = [self.digits[n] for n in str(self.score)]

            # resize surface to fit all digits with some space between digits
            image_width = sum(image.get_width() + 2 for image in digits_to_print)
            self.image = pg.Surface((image_width, self.rect.h), pg.SRCALPHA)
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


class ScoreBoard(UIElement):
    def __init__(self, game, scale, **rect_position):
        super().__init__(game, scale, **rect_position)

        self.image = self._get_scoreboard_image()
        self.rect = self.image.get_rect(**self.rect_position)

        self._build()
        self.update_image()

    def update(self, *args, **kwargs) -> None:
        pass

    def update_image(self):
        self.image = self._get_scoreboard_image()
        self.rect = self.image.get_rect(**self.rect_position)
        self.image.blit(self.medal.image, self.medal.rect)

    def _build(self, ) -> None:
        """Initialize individual elements"""
        self.medal = self.Medal(
            self,
            scale=0.20,
            center=(0.22 * self.rect.w, .55 * self.rect.h)
        )

    def _get_scoreboard_image(self):
        return utils.scale_image(
            utils.load_image(query='scoreboard'),
            self.scale,
            self.game.rect.w
        )

    class Medal:
        def __init__(self, scoreboard, scale: Union[int, float], **blit_position):
            """
            Represents a static image of a medal that can change colors.

            Parameters-
                scoreboard: scoreboard object that the medal will be blitted to.
                scale: 0 < scale <= 1, ratio to scale medal to scoreboard width.
                **blit_position: positions kwargs for medal's rectangle.
            """
            self.parent = scoreboard

            self.images: dict[str, pg.Surface] = {}
            for medal_name, image in utils.load_images(query='medal').items():
                image = utils.scale_image(image, scale, scoreboard.rect.w, 'w')
                self.images[medal_name] = image

            self.blit_position: Kwargs = blit_position
            self.image = self.images['bronzemedal']
            self.rect = self.image.get_rect(**self.blit_position)

        def change_color(self, color: str):
            """
            Change the color of the medal

            color parameter must be one of these: ('bronze, 'silver', 'gold')
            """
            for key, img in self.images.items():
                if color.lower() in key.lower():
                    self.image = img
                    self.rect = img.get_rect(**self.blit_position)
                    self.parent.update_image()
                    break
            else:
                raise ValueError(f"Could not find color '{color}' in medal"
                                 " image pool")
