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

from __future__ import annotations

__all__ = (
    "Locale",
    "Tstr",
)


from enum import Enum
from typing import Any

from typing_extensions import Self


def __new__(cls: Self, value: Any | None = None):
    if type(value) is cls:
        return value
    if value in cls._value2member_map_:
        return cls._value2member_map_[value]
    else:
        return cls._value2member_map_[str(Locale.japanese)]

Enum.__new__ = __new__

class Locale(str, Enum):
    """
    Locale representation corresponding to :attr:`discord.Locale`
    in ``discord.py``.
    """
    def __new__(cls, locale: str) -> Self:
        self = str.__new__(cls, locale)
        self._value_ = str(locale)
        cls._value2member_map_.update({locale: self})
        return self

    american_english = "en-US"
    british_english = "en-GB"
    taiwan_chinese = "zh-TW"
    japanese = "ja"

    def __str__(self) -> str:
        return self.value

class Tstr(str):
    """Extension class for :class:`str` for multilingualisation."""
    def __new__(cls, *args: str, **kwargs: str) -> Self:
        if len(args) == 0:
            if type(kwargs[Locale.japanese.value]) is not str:
                raise ValueError("kwargs[Locale.japanese.value] must be str.")
            self = super().__new__(cls, kwargs[Locale.japanese.value])
            default = kwargs[Locale.japanese.value]
        else:
            if type(*args) is not str:
                raise ValueError("*arg must be str.")
            self = super().__new__(cls, *args)
            default = args[0]

        self._locale_str: dict[Locale, str] = {}
        for locale in list(Locale):
            self._locale_str[locale] = kwargs.get(locale.value, default)

        return self

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self._locale_str[Locale.japanese]

    def __call__(self, locale: Locale | None = None) -> str:
        if locale in list(Locale):
            return self._locale_str[Locale(locale)]
        else:
            return self._locale_str[Locale.japanese]

    def __eq__(self, __x: object) -> bool:
        if super().__eq__(__x):
            return True
        return __x in list(self._locale_str.values())

    def values(self) -> list[str]:
        """Gets all locale string as List[:class:`str`].

        Returns
        -------
        List[:class:`str`]
            List with each locale string as an element.

        """
        return list(self._locale_str.values())
