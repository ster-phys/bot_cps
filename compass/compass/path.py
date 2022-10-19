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
    "PATH",
)


import os

from .activation import Activation
from .rarity import Rarity
from .utils import Locale


class _Path(object):
    """Class defining paths for the data used by this library."""

    _ROOTPATH = os.path.dirname(os.path.abspath(__file__))
    _IMGS = f"{_ROOTPATH}/images"
    _DATA = f"{_ROOTPATH}/data"
    _TRANS = f"{_ROOTPATH}/trans"
    _FONTS = f"{_ROOTPATH}/fonts"

    CARDIMG = f"{_IMGS}/card"
    ICONIMG = f"{_IMGS}/icon"
    HEROIMG = f"{_IMGS}/hero"
    STAGEIMG = f"{_IMGS}/stage"

    CARDJSON = f"{_DATA}/card.json.fernet"
    HEROJSON = f"{_DATA}/hero.json.fernet"
    STAGEJSON = f"{_DATA}/stage.json.fernet"

    _EN_TRANS = f"{_TRANS}/en"
    _TW_TRANS = f"{_TRANS}/zh-TW"

    EN_CARDJSON = f"{_EN_TRANS}/card.json"
    EN_HEROJSON = f"{_EN_TRANS}/hero.json"
    EN_STAGEJSON = f"{_EN_TRANS}/stage.json"

    TW_CARDJSON = f"{_TW_TRANS}/card.json"
    TW_HEROJSON = f"{_TW_TRANS}/hero.json"
    TW_STAGEJSON = f"{_TW_TRANS}/stage.json"

    JP_FONT = f"{_FONTS}/NotoSansJP-Bold.otf"
    TW_FONT = f"{_FONTS}/NotoSansTC-Bold.otf"

    class _Deck(object):
        """Path of images for generating deck image."""

        def __init__(self, _IMGS: str) -> None:
            self.DECKIMG = f"{_IMGS}/deck"

        def frame(self, position: str, locale: Locale = Locale.japanese) -> str:
            locale = Locale(locale)
            add = ".tw" if locale == Locale.taiwan_chinese else ""
            return f"{self.DECKIMG}/frame/{position}{add}.png"

        def level(self, number: str | int) -> str:
            return f"{self.DECKIMG}/level/{number}.png"

        def status(self, number: str | int) -> str:
            return f"{self.DECKIMG}/status/{number}.png"

        def blank(self) -> str:
            return f"{self.DECKIMG}/blank.jpg"

    DECK = _Deck(_IMGS)

    class _Detail(object):
        """Path of images for generating detail image."""

        def __init__(self, _IMGS: str) -> None:
            self.DETAILIMG = f"{_IMGS}/detail"

        def activation(self, act: str | Activation) -> str:
            return f"{self.DETAILIMG}/activation/{Activation(act).name.lower()}.png"

        def cool_time(self, number: str | int) -> str:
            return f"{self.DETAILIMG}/cool_time/{number}.png"

        def frame(self, place: str, locale: Locale = Locale.japanese) -> str:
            locale = Locale(locale)
            add = ".tw" if locale == Locale.taiwan_chinese else ""
            return f"{self.DETAILIMG}/frame/{place}{add}.png"

        def level(self, number: str | int) -> str:
            return f"{self.DETAILIMG}/level/{number}.png"

        def rarity(self, rarity_: str | Rarity) -> str:
            rarity_ = Rarity(rarity_)
            return f"{self.DETAILIMG}/rarity/{rarity_.name}.png"

        def status(self, number: str | int) -> str:
            return f"{self.DETAILIMG}/status/{number}.png"

    DETAIL = _Detail(_IMGS)

PATH = _Path()
