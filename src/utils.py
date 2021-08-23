import pygame as pg
import os
from collections import deque, Counter


from typing import Iterable, Optional, Union, Container
# Typing
Filenames = Iterable[str]
Image = pg.Surface
Images = Iterable[pg.Surface]
Checkbox = Optional[bool]
Sizehint = Union[int, float]

# Globals
IMG_FOLDER_PATH = os.path.join('..', 'img')


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


def load_images(
        filenames: Optional[Filenames] = (),
        query: Optional[str] = '',
        convert_alpha: Checkbox = True,
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


def load_sprite_frames(sprite_name: str) -> deque[Image]:
    """load the images that match a query into a deque and return the deque.
    sprite_name should be the entire left half of each filename. For example, the
    query 'startbutton' would load the following filenames: 'startbutton-clicked',
    and 'startbutton-unclicked'
    """
    images: dict[str, Image] = load_images(query=sprite_name)
    return deque(
        images.values()
    )


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


def scale_image(
        image: Image, percentage: Sizehint, other_length: int, mode: str = 'w'
) -> Image:
    """
    Scale the images width to a percentage of some other width, preserves ratio.
    """
    w, h = image.get_size()
    orig_ratio = w / h  # r = w/h

    if mode == 'w':
        # scale width to other width
        w = int(percentage * other_length)
        # get height using original ratio
        h = int(w / orig_ratio)  # because r = w/h, h = w/r
    elif mode == 'h':
        # scale height to other height
        h = int(percentage * other_length)
        # get width using original ratio
        w = int(orig_ratio * h)  # because r = w/h, w = r*h

    return pg.transform.scale(image, (w, h))


def make_all_same_size(images):
    """
    Take in a container of images and make them all the same size. If no
    size argument is given, the images will take on the size and ratio which
    is most common among the given Images.
    """
    sizes = Counter(image.get_size() for image in images)
    size = sizes.most_common(1)[0][0]

    return tuple(pg.transform.scale(img, size) for img in images)


class StaticImage:
    """
    Represents a surface that has no movement/behavior used for background and
    foreground
    """
    def __init__(self, image: Image):
        self.image = image
        self.rect = self.image.get_rect()
