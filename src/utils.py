import pygame as pg
import os
from typing import Iterable, Optional


# Typing
Filenames = Iterable[str]
Image = pg.Surface
Checkbox = Optional[bool]

# Globals
IMG_FOLDER_PATH = os.path.join('..', 'img')


def convert_image(image: Image, convert_alpha: Checkbox = True
                  ) -> Image:
    """Image is converted to using .convert_alpha() by default but if called
        with convert_alpha=False, images will will be converted using .convert()
        rather than .convert_alpha()"""
    try:
        if convert_alpha:
            return image.convert_alpha()
        else:
            return image.convert()
    except pg.error as e:
        print(f"WARNING in src/{__name__}.py convert_image()\n"
              f"Could not convert {image}"
              )
        return image


def load_images(
        filenames: Optional[Filenames] = (), query: Optional[str] = '',
        convert_alpha: Checkbox = True
        ) -> dict[str, Image]:
    """
        Loads images into a dictionary explicitly and/or using a query.
        {'img_name': Image, ...}
        You must specify filenames and / or provide a query. If no matches
        are found, an empty dict is returned. You can optionally call
        convert_alpha on all images with the convert_alpha flag. If called
        with convert_alpha=False, images will will be converted using .convert()
        rather than .convert_alpha()
    """

    folder_path = IMG_FOLDER_PATH
    images = {}

    for fn in filenames:
        file_path = os.path.join(folder_path, fn)
        img = pg.image.load(file_path)
        img_name = fn.split('.')[0]
        images[img_name] = convert_image(img, convert_alpha)

    if query:
        for fn in os.listdir(folder_path):
            if query in fn:
                file_path = os.path.join(folder_path, fn)
                img = pg.image.load(file_path)
                img_name = fn.split('.')[0]
                images[img_name] = convert_image(img, convert_alpha)

    return images


def load_image(query: str, convert_alpha: Checkbox = True
               ) -> Image:
    """
    Queries the img directory and returns the first image whose
    filename contains the query as a sub-string.
    """
    folder_path = IMG_FOLDER_PATH

    for fn in os.listdir(folder_path):
        if query in fn:
            file_path = os.path.join(folder_path, fn)
            img = pg.image.load(file_path)
            img_name = fn.split('.')[0]

            return convert_image(img, convert_alpha)


class StaticImage:
    """
    Represents a surface that has no movement/behavior used for background and
    foreground
    """
    def __init__(self, image: Image):
        self.image = image
        self.rect = self.image.get_rect()
