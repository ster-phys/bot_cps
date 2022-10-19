"""
A library that provides Compass Data Structures

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

__all__ = (
    "Activation",
)


from enum import Enum

from typing_extensions import Self

from .utils import Locale, Tstr


class Activation(Tstr, Enum):
    """Activation time of the card."""
    def __new__(cls, ja_tw: str, en: str) -> Self:
        kwargs = {
            Locale.japanese.value: ja_tw,
            Locale.taiwan_chinese.value: ja_tw,
            Locale.american_english.value: en,
            Locale.british_english.value: en,
        }
        self = Tstr.__new__(cls, **kwargs)
        self._value_ = Tstr(**kwargs)
        cls._value2member_map_.update({ja_tw: self, en: self})
        return self

    LONG = ("長", "long")
    SHORT = ("短", "short")
    NONE = ("無", "none")

    def __str__(self) -> str:
        return self.value.__str__()
