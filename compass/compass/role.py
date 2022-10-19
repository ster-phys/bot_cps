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
    "Role",
)


from enum import Enum

from typing_extensions import Self

from .utils import Locale, Tstr


class Role(Tstr, Enum):
    """Role of the Hero."""
    def __new__(cls, val: str, ja: str, tw: str, en: str) -> Self:
        kwargs = {
            Locale.japanese.value: ja,
            Locale.taiwan_chinese.value: tw,
            Locale.american_english.value: en,
            Locale.british_english.value: en,
        }
        self = Tstr.__new__(cls, val, **kwargs)
        self._value_ = Tstr(val, **kwargs)
        cls._value2member_map_.update({val: self, ja: self, tw: self, en: self})
        return self

    ATTACKER = ("atk", "アタッカー", "戰士", "attacker")
    SPRINTER = ("spr", "スプリンター", "快跑手", "sprinter")
    GUNNER = ("gun", "ガンナー", "狙擊手", "gunner")
    TANK = ("tnk", "タンク", "坦克", "tank")

    def __str__(self) -> str:
        return self.value.__str__()
