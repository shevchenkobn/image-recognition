from glob import glob
from PIL import Image, ImageDraw
import os

allowed_extensions = Image.registered_extensions().keys()


def get_filenames_from_dir(dirpath, sort=True):
    dirpath = os.path.join(os.path.abspath(dirpath), '')
    image_names = []
    for ext in allowed_extensions:
        image_names += glob(dirpath + '*' + ext)
    if sort:
        image_names.sort()
    return image_names


def draw_rectangle(image, coords, stroke, color):
    draw = ImageDraw.Draw(image)

    draw.rectangle(
        coords,
        outline=color,
        width=stroke
    )
