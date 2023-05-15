"""
A program that provides bot managed by bot_cps

The GNU General Public License v3.0 (GPL-3.0)

Copyright (C) 2021-present ster <ster.physics@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

__title__ = "bot_cps"
__author__ = "ster"
__license__ = "GPL-3.0"
__copyright__ = "Copyright 2021-present ster"
__version__ = "1.1.0a"


__all__ = (
    "extensions",
)


extensions = (
    f"{__title__}.card",
    f"{__title__}.deck",
    f"{__title__}.emoji",
    f"{__title__}.gacha",
    f"{__title__}.help",
    f"{__title__}.listener",
    f"{__title__}.ping",
    f"{__title__}.roulette",
    f"{__title__}.stage",
    f"{__title__}.team",
    f"{__title__}.tos",
)
