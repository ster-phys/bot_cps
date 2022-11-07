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
    "Rank",
)


from enum import Enum
from typing import Callable

from typing_extensions import Self


def precompare(check_collabo: bool = True):
    """
    Decorator to enable comparisons to be made even when
    there are slight notational distortions.

    Parameters
    ----------
    check_collabo: :class:`bool`
        Sets this variable to ``True`` if returns ``False``
        when the collaboration rank is included.

    """

    def _precompare(function: Callable[..., bool]):
        def wrapper(self: function.__class__, __x: object):
            __x = Rank("s") if __x.lower() == "s1" else Rank(__x.lower())
            if check_collabo and (self.is_collabo or __x.is_collabo):
                return False
            return function(self, __x)
        return wrapper
    return _precompare

_rank_order = ("F","E","D","C","B","A","S1",)

class Rank(str, Enum):
    """Available rank of the card."""
    # rank
    S1 = "s"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"

    # others
    EX = "ex"

    # collaboration
    BL = "bl"
    BUNSUTO = "bunsuto"
    DANMACHI = "danmachi"
    DANRON = "danron"
    FATE = "fate"
    FF = "ff"
    GG = "gg"
    HAKKA = "hakka"
    KABUKI = "kabuki"
    KONOSUBA = "konosuba"
    KYOJIN = "kyojin"
    MIKU = "miku"
    NA = "na"
    NEKOMIYA = "nekomiya"
    OL = "ol"
    P5 = "p5"
    REF = "ref"
    REZERO = "rezero"
    RYZA = "ryza"
    SAO = "sao"
    SATSUTEN = "satsuten"
    SF = "sf"
    SG = "sg"
    TENSURA = "tensura"

    def __str__(self) -> str:
        return self.name

    @property
    def is_collabo(self) -> bool:
        return self.name not in _rank_order

    @precompare(check_collabo=False)
    def __eq__(self, __x: Self | str) -> bool:
        return super().__eq__(__x)

    @precompare(check_collabo=False)
    def __ne__(self, __x: Self | str) -> bool:
        return not self.__eq__(__x)

    @precompare(check_collabo=True)
    def __lt__(self, __x: Self | str) -> bool:
        return _rank_order.index(self.name) < _rank_order.index(__x.name)

    @precompare(check_collabo=True)
    def __le__(self, __x: Self | str) -> bool:
        return self.__lt__(__x) or self.__eq__(__x)

    @precompare(check_collabo=True)
    def __gt__(self, __x: Self | str) -> bool:
        return not self.__le__(__x)

    @precompare(check_collabo=True)
    def __ge__(self, __x: Self | str) -> bool:
        return not self.__lt__(__x)
