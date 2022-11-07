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
    "Attribute",
)


from enum import Enum

from typing_extensions import Self

from .utils import Locale, Tstr


class Attribute(Tstr, Enum):
    """Attributes of the card."""
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

    WATER = ("水", "water")
    FIRE = ("火", "fire")
    WOOD = ("木", "wood")

    def __str__(self) -> str:
        return self.value.__str__()

    def __lt__(self, __x: Self | str | Tstr) -> bool:
        return str(self) == "水" and str(__x) == "木" or \
               str(self) == "木" and str(__x) == "火" or \
               str(self) == "火" and str(__x) == "水"

    def __le__(self, __x: Self | str | Tstr) -> bool:
        return self.__lt__(__x) or self.__eq__(__x)

    def __gt__(self, __x: Self | str | Tstr) -> bool:
        return not self.__le__(__x)

    def __ge__(self, __x: Self | str | Tstr) -> bool:
        return not self.__lt__(__x)

    @property
    def related_terms(self) -> list[str]:
        """Returns related words.

        Returns
        -------
        List[:class:`str`]
            List of strings which element is another way of saying
            the attribute.

        """
        d = {
            "水": ["水", "青", "藍",],
            "木": ["木", "緑",],
            "火": ["火", "赤", "紅",],
        }
        return d[str(self)]

    @property
    def color(self) -> int:
        """Gets this attribute color."""
        if str(self) == "水":
            return 0x0D1BCE
        elif str(self) == "火":
            return 0xE7382A
        else: # str(self) == "木"
            return 0x59B93A
