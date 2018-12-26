#!/usr/bin/env python
import logging
from datetime import datetime
from logging import FileHandler, Formatter, getLogger
from pathlib import Path
from typing import Dict, Generator, List, Tuple

import click
import cv2
import numpy as np
import yaml
from tqdm import tqdm

logger = getLogger(__name__)
logger.setLevel(logging.INFO)

log_format = Formatter('%(asctime)s (%(name)s) [%(levelname)s] %(message)s')
now_date = datetime.now()
log_file_name = now_date.strftime('./logs/%Y-%m-%d_%H-%M-%S-%f.log')
file_handler = FileHandler(filename=log_file_name)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

logger.info('script start')


def load_config(config_path: str) -> Dict[str, str]:
    """load_config

    Load configuration yaml file

    Parameters
    ----------
    config_path : str
        path to config file

    Returns
    -------
    Dict[str, str]
        loaded configuration
    """
    with open(config_path, 'rb') as f:
        config = yaml.load(f)

    logger.info(f'config file {config_path} were loaded')
    return config[0]


def create_image_list(target_path: str, ext: str = 'jpg') -> List[Path]:
    """create_image_list

    Create a list of image paths

    Parameters
    ----------
    target_path : str
        search directory
    ext : str, optional
        file extention (the default is 'jpg')

    Returns
    -------
    List[Path]
        list of Path objects
    """
    image_paths = sorted(list(Path(target_path).glob(f'*.{ext}')))
    logger.info(f'{len(image_paths)} {ext} images were found in {target_path}')
    return image_paths


def image_generator(target_list: List[Path]) -> Generator[np.ndarray, None, None]:
    """image_generator

    Generator that yields images one by one

    Parameters
    ----------
    target_list : List[Path]
        list of image path

    Returns
    -------
    Generator[np.ndarray, None, None]
        Loaded images (OpenCV style)
    """
    for p in target_list:
        yield cv2.imread(str(p), cv2.IMREAD_COLOR)


def crop(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """crop_image

    Cropping image

    Parameters
    ----------
    image : np.ndarray
        (H, W, C) or (N, H, W, C)
    bbox : Tuple[int, int, int, int]
        xmin, ymin, xmax, ymax

    Returns
    -------
    np.ndarray
        Cropped image
    """
    ndim = image.ndim
    if ndim not in (3, 4):
        raise ValueError('ndim accepts only 3 or 4')

    xmin, ymin, xmax, ymax = bbox
    if ndim == 3:
        cropped_image = image[ymin:ymax, xmin:xmax, :]
    else:
        cropped_image = image[:, ymin:ymax, xmin:xmax, :]

    return cropped_image


@click.command()
@click.option(
    '-c',
    '--config',
    default='./crop_config.yml',
    type=str
)
def crop_image(config: str) -> None:
    # dump CLI options for debug
    logger.debug(f'-c {config}')

    crop_conf = load_config(config)

    bbox = crop_conf['bbox'][0]  # TODO: 複数個所同時切り出し
    image_list = create_image_list(crop_conf['target_path'], ext=crop_conf['ext'])

    for i, im in tqdm(enumerate(image_generator(image_list)), total=len(image_list)):
        try:
            cropped_img = crop(im, bbox)
            fname = Path(crop_conf['output_path']) / f'{crop_conf["output_header"]}_{image_list[i].stem}.png'
            cv2.imwrite(str(fname), cropped_img)
            tqdm.write(f'image saved to {fname}')
            logger.info(f'image saved to {fname}')
        except Exception as ex:
            # 途中で読めない画像があっても続行する
            logger.exception(ex)
            tqdm.write(f'error ocurred while processing {image_list[i]}')
            logger.error(f'error ocurred while processing {image_list[i]}')


if __name__ == "__main__":
    crop_image()
