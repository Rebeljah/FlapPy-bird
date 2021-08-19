"""
Flappy bird is a game where the player controls a small, dumb looking bird by
tapping (all while avoiding large pipes). Each time the player passes a set of
pipes, points are awarded. Running into a pipe will result in instant death for
our poor little flappy bird, so look out!.
"""

import pygame as pg
import sys
import random


from bird import Bird
from pipe import PipeSpawner, Pipe
from utils import load_image, StaticImage


class Game:
    wh_ratio = 9 / 16

    def __init__(self):
        pg.display.set_caption('FlapPyGame')
        pg.display.set_icon(load_image('icon'))
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((288, 512))
        self.rect = self.screen.get_rect()

        self.background = StaticImage(load_image('background'))
        self.foreground = StaticImage(load_image('base'))
        self.foreground.rect.bottomleft = self.rect.bottomleft
        self.bird = Bird(self)
        self.pipes = PipeSpawner(self)

    def run(self):
        while True:
            dt = self.clock.tick(40) / 1000
            self._check_events()
            self._update(dt)
            self._draw()

    def _check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.bird.flap_up()

    def _update(self, dt):
        self.bird.update(dt)
        self.pipes.update(dt=dt)
        self._check_collision()

    def _draw(self):
        self.screen.blit(self.background.image, self.background.rect)
        self.pipes.draw(self.screen)
        self.screen.blit(self.foreground.image, self.foreground.rect)
        self.screen.blit(self.bird.image, self.bird.rect)

        pg.display.flip()

    def _check_collision(self) -> None:
        pipe: Pipe

        # check ground collision
        if self.bird.rect.bottom > self.foreground.rect.top:
            self.bird.die(cause='floor')
            return None

        # only check collision if a pipe is less than 100 pixels away
        for pipe in self.pipes:
            if (
                    pipe.is_moving
                    and abs(self.bird.rect.right - pipe.rect.left) < 100
                    and pg.sprite.collide_mask(self.bird, pipe)
            ):
                self.bird.die(cause='pipe')

    @staticmethod
    def _quit():
        sys.exit()


if __name__ == '__main__':
    game = Game()
    game.run()
