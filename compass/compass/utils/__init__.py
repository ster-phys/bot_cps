"""
Utilities for Compass Library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2021-present ster
:license: GPL-3.0, see LICENSE for more details.

"""

__all__ = (
    "ImageType",
    "add_margin",
    "convert_to_jpg",
    "convert_to_square",
    "merge_images",
    "merge_images_horizon",
    "merge_images_vertical",
    "resize_unification",
    "Locale",
    "Tstr",
    "CONFIG",
    "similar",
    "translator",
)

from .about_image import (ImageType, add_margin, convert_to_jpg,
                          convert_to_square, merge_images,
                          merge_images_horizon, merge_images_vertical,
                          resize_unification)
from .about_str import Locale, Tstr
from .config import CONFIG
from .similar import similar, translator
