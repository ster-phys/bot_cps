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
    "Parameter",
    "Status",
)


from copy import copy
from dataclasses import dataclass

from typing_extensions import Self


@dataclass
class Parameter(object):
    """Parameters of the compass data."""
    attack: float
    defense: float
    physical: float

    def __iadd__(self, __x: Self) -> Self:
        self.attack += __x.attack
        self.defense += __x.defense
        self.physical += __x.physical
        return self

    def __add__(self, __x: Self) -> Self:
        tmp = copy(self)
        tmp.__iadd__(__x)
        return tmp

    def __isub__(self, __x: Self) -> Self:
        self.attack -= __x.attack
        self.defense -= __x.defense
        self.physical -= __x.physical
        return self

    def __sub__(self, __x: Self) -> Self:
        tmp = copy(self)
        tmp.__isub__(__x)
        return tmp

    def __imul__(self, __x: Self) -> Self:
        self.attack *= __x.attack
        self.defense *= __x.defense
        self.physical *= __x.physical
        return self

    def __mul__(self, __x: Self) -> Self:
        tmp = copy(self)
        tmp.__imul__(__x)
        return tmp

    def __itruediv__(self, __x: Self) -> Self:
        self.attack /= __x.attack
        self.defense /= __x.defense
        self.physical /= __x.physical
        return self

    def __truediv__(self, __x: Self) -> Self:
        tmp = copy(self)
        tmp.__itruediv__(__x)
        return tmp

_level_list = [1, 20, 30, 40, 50, 60]

class Status(dict):
    """Status of the card."""
    def __init__(self, **data: dict[str, float]) -> None:
        super().__init__()
        atks, defs, phss = data["atk"], data["def"], data["phs"]
        for v in _level_list:
            param = Parameter(atks[str(v)], defs[str(v)], phss[str(v)])
            self.update({str(v): param})

    def __getitem__(self, __key):
        __key = str(__key) if type(__key) is int else __key
        return super().__getitem__(__key)
