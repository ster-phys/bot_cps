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
    "Rarity",
)


from enum import Enum

from typing_extensions import Self

_rarity_order = ("UR","SR","R","N",)

class Rarity(str, Enum):
    """Rarity of the card."""
    def __new__(cls, value: str) -> Self:
        self = str.__new__(cls, value)
        self._value_ = str(value)
        cls._value2member_map_.update({value.upper(): self})
        return self

    UR = ("ur",)
    SR = ("sr",)
    R = ("r",)
    N = ("n",)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, __x: Self | str) -> bool:
        return super().__eq__(__x.lower())

    def __ne__(self, __x: Self | str) -> bool:
        return not self.__eq__(__x)

    def __lt__(self, __x: Self | str) -> bool:
        __x = self.__class__(__x.lower())
        return _rarity_order.index(self.name) < _rarity_order.index(__x.name)

    def __le__(self, __x: Self | str) -> bool:
        return self.__lt__(__x) or self.__eq__(__x)

    def __gt__(self, __x: Self | str) -> bool:
        return not self.__le__(__x)

    def __ge__(self, __x: Self | str) -> bool:
        return not self.__lt__(__x)
