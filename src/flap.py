"""
Flappy bird is a game where the player controls a small, dumb looking bird by
tapping (all while avoiding large pipes). Each time the player passes a set of
pipes, points are awarded. Running into a pipe will result in instant death for
our poor little flappy bird, so look out!.
"""

import pygame as pg
import sys


from bird import Bird
from pipe import PipeSpawner
import ui
from utils import load_image, scale_image, StaticImage


class Game:
    wh_ratio = 9 / 16

    def __init__(self):
        pg.mixer.init()
        print()

        pg.display.set_caption('FlapPyGame')
        pg.display.set_icon(load_image('icon'))
        self.clock = pg.time.Clock()

        ratio = 288/512
        h = int(1000)
        w = int(ratio * h)

        self.screen = pg.display.set_mode((w, h))
        self.rect = self.screen.get_rect()

        self.background = StaticImage(
            scale_image(load_image('background-night'), 1, self.rect.w)
        )
        self.floor = StaticImage(
            scale_image(load_image('base'), 1, self.rect.w)
        )
        self.floor.rect.bottomleft = self.rect.bottomleft
        self.play_area = pg.Rect(
            0, 0, self.rect.w, (self.rect.h - self.floor.rect.h)
        )

        self.in_game = False
        self.pipes = PipeSpawner(self)
        self.bird = Bird(self)
        self.events = EventHandler(self)
        self.menu_ui = ui.Menu(self)
        self.in_game_ui = ui.HUD(self)

    def toggle_menu(self):
        if self.in_game:
            self.in_game = False
        elif self.bird.is_alive:
            self.in_game = True
        else:
            self.bird.revive()
            self.pipes.reset()

    def run(self):
        while True:
            dt = self.clock.tick(35) / 1000
            self.events.check_events()
            self._update(dt)
            self._draw()

    def _update(self, dt):
        self.bird.update(dt)
        if self.in_game:
            self.pipes.update(dt=dt)
        else:
            self.menu_ui.update(
                self.events.mouse_down,
                self.events.mouse_up_position,
                self.events.mouse_down_position
            )

        self.in_game_ui.update(self.bird.score)

    def _draw(self):
        self.screen.blit(self.background.image, self.background.rect)
        self.pipes.draw(self.screen)
        self.screen.blit(self.floor.image, self.floor.rect)

        self.screen.blit(self.bird.image, self.bird.rect)

        if not self.in_game:
            self.menu_ui.draw(self.screen)
        self.in_game_ui.draw(self.screen)

        pg.display.flip()

    @staticmethod
    def quit():
        sys.exit()


class EventHandler:
    def __init__(self, game):
        self.game = game

        self.mouse_down = False
        # position where mouse is currently clicking
        self.mouse_down_position = None
        # position where mouse is currently unclicking
        self.mouse_up_position = None

    def check_events(self):
        # reset mouse positions
        if self.mouse_up_position:
            self.mouse_up_position = None
        if self.mouse_down_position:
            self.mouse_down_position = None

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            elif event.type in (pg.KEYDOWN, pg.KEYUP):
                self._keyboard(event)
            elif event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
                self._mouse(event)

    def _keyboard(self, event):
        if event.type == pg.KEYDOWN:
            if self.game.in_game and event.key == pg.K_SPACE:
                self.game.bird.flap_up()
            elif event.key == pg.K_ESCAPE:
                self.game.toggle_menu()

    def _mouse(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.mouse_down = True
            self.mouse_down_position = pg.mouse.get_pos()
        elif event.type == pg.MOUSEBUTTONUP:
            self.mouse_down = False
            self.mouse_up_position = pg.mouse.get_pos()


if __name__ == '__main__':
    game = Game()
    game.run()
