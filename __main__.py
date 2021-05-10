import argparse
import os
import sys
from PIL import Image

from util import change_filename_dir, ensure_dir
from image.util import get_filenames_from_dir
from util.argparse import PathType, RangedFloatType
import image

if sys.version_info < (3, 6):
    sys.stdout.write("Requires Python 3.6 at minimum (pillow constraint, tested on 3.8)\n")
    sys.exit(1)

__version__ = '1.0.0'


def main(args):
    filenames = get_filenames_from_dir(args.input_dir)
    if args.transformed_dir:
        ensure_dir(args.transformed_dir)
    if args.recognized_dir:
        ensure_dir(args.recognized_dir)
    for filename in filenames:
        print(f'Transforming file {filename}')
        src_img = Image.open(filename)
        img = image.transform_image(src_img, args.transform_k)
        if args.transformed_dir and not args.recognized_dir:
            img.save(
                change_filename_dir(filename, args.transformed_dir)
            )
        if args.recognized_dir:
            print(f'Recognizing file {filename}')
            rect = image.recognize(img, rect_size=12, step_percent=0.475)
            if args.transformed_dir:
                image.util.draw_rectangle(img, rect, stroke=2, color=(0, 255, 0))
                img.save(
                    change_filename_dir(filename, args.transformed_dir)
                )
            image.util.draw_rectangle(src_img, rect, stroke=2, color=(0, 255, 0))
            src_img.save(
                change_filename_dir(filename, args.recognized_dir)
            )
    print('Finished ' + ('recognition' if args.recognized_dir else 'transformation'))


def get_args():
    parser = argparse.ArgumentParser(
        description='Utility for finding blood cells in image. '
                    'Specify at least one of output directories.'
    )
    parser.add_argument(
        '--input-dir', '-i',
        action='store',
        nargs='?',
        default='./input_images',
        type=PathType(
            exists=True,
            arg_type='dir',
            dash_ok=False,
            permission=os.R_OK
        ),
        # required=True,
        help='The directory to read files from',
        dest='input_dir'
    )
    parser.add_argument(
        '--transformed-out', '-t',
        action='store',
        nargs='?',
        type=PathType(
            arg_type='dir',
            dash_ok=False,
            permission=os.W_OK
        ),
        required=False,
        help='The output directory to write black-white files to.',
        dest='transformed_dir'
    )
    parser.add_argument(
        '--recognised-out', '-r',
        action='store',
        nargs='?',
        type=PathType(
            arg_type='dir',
            dash_ok=False,
            permission=os.W_OK
        ),
        required=False,
        help='The output directory to write recognized files to.',
        dest='recognized_dir'
    )
    parser.add_argument(
        '--transform-k', '-k',
        action='store',
        nargs='?',
        type=RangedFloatType(image.TRANSFORM_K_RANGE),
        required=True,
        help='The k parameter for transformation. In range [%r, %r]' % image.TRANSFORM_K_RANGE,
        dest='transform_k'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'v{__version__}',
        help='Print version of the package',
    )
    args = parser.parse_args()

    if not args.recognized_dir and not args.transformed_dir:
        parser.error('either output directory or both must be specified')
    return args


main(get_args())
