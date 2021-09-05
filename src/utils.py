import pygame as pg

import os
from collections import Counter


from typing import Iterable, Optional, Union
# Typing
Filenames = Iterable[str]
Image = pg.Surface
Images = Iterable[pg.Surface]
Checkbox = Optional[bool]
Sizehint = Union[int, float]
Sound = pg.mixer.Sound
KwargName = str
Position = Iterable[Union[int, float]]
KwargValue = Union[int, float, Position]
RectPositionKwargs = dict[KwargName, KwargValue]
Size = tuple[int, int]

# Globals
IMG_FOLDER_PATH = os.path.join('..', 'img')
AUDIO_FOLDER_PATH = os.path.join('..', 'audio')


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

            print(f"{__name__} load image {file_path}")

            return convert_image(img, convert_alpha)
    else:
        raise FileNotFoundError(
            f"Could not find image filename containing '{query}'"
        )


def load_images(
        filenames: Optional[Filenames] = (),
        query: Optional[str] = '',
        convert_alpha: Checkbox = True,
        ) -> dict[str, Image]:
    """
        Loads images into a dictionary explicitly and/or using a query.
        {'img_name': Image, ...}
        You must specify filenames and / or provide a query. If no matches
        are found, raises FileNotFoundError. You can optionally call
        convert_alpha on all images with the convert_alpha flag. If called
        with convert_alpha=False, images will will be converted using .convert()
        rather than .convert_alpha()
    """
    folder_path = IMG_FOLDER_PATH
    images = {}

    if filenames:
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

    print(f"{__name__} load images {', '.join(k for k in images.keys())}")

    if images:
        return images
    else:
        raise FileNotFoundError(f"Could not load any images."
                                f"Could not locate filenames:\n"
                                f"{filenames}\n"
                                f"No results for query: {query}")


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
    except pg.error:
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


def make_all_same_size(images: Images) -> Images:
    """
    Take in a container of images and make them all the same size. The Images
    will take on the size which is most common among the given Images.
    """
    # get most common size
    sizes = Counter(image.get_size() for image in images)
    w, h = sizes.most_common()[0][0]

    return tuple(pg.transform.scale(surf, (w, h)) for surf in images)


def load_sounds(sound_names: Iterable[str]) -> dict[str, Sound]:
    """
        Loads sounds into a dictionary. You must specify sound names.
        (no need to specify filename. If no matches are found, an empty dict
        is returned.
    """
    folder_path = AUDIO_FOLDER_PATH
    extension = '.wav'

    sounds = {}
    for sound_name in sound_names:
        file_path = os.path.join(folder_path, sound_name + extension)
        sounds[sound_name] = pg.mixer.Sound(file_path)

    print(f"{__name__} load sounds: {', '.join(sound_names)}")

    return sounds


class StaticImage(pg.sprite.Sprite):
    """
    Represents a surface that has no movement/behavior used for background and
    foreground
    """
    def __init__(self,
                 image: Image,
                 **rect_position
        ):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(**rect_position)
