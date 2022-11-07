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
    "Hero",
)


from dataclasses import dataclass
from typing import Any

from PIL import Image
from typing_extensions import Self

from .path import PATH
from .role import Role
from .status import Parameter
from .utils import ImageType, Locale, Tstr


@dataclass
class Hero(object):
    """Hero of Compass."""
    __num: int
    __name: Tstr
    __setname: str
    __parameter: Parameter
    __speed: float
    __role: Role
    __ultname: Tstr
    __ultinvincible: str
    __haname: Tstr
    __is_collabo: bool
    __icon_name: str
    __icon_color: int
    __image_name: str
    __image_color: int

    __icon_path: str = ""
    __image_path: str = ""

    def __post_init__(self) -> None:
        self.__icon_path = f"{PATH.ICONIMG}/{self.__icon_name}.jpg"
        self.__image_path = f"{PATH.HEROIMG}/{self.__image_name}.jpg"

    def __str__(self) -> str:
        return f"{self.num:03}_{self.__setname}"

    @property
    def num(self) -> int:
        """Number of the hero."""
        return self.__num

    @property
    def name(self) -> Tstr:
        """Name of the hero."""
        return self.__name

    @name.setter
    def name(self, value: Tstr) -> None:
        """Setter of the hero name."""
        if type(value) is not Tstr:
            raise ValueError("Value mast be Tstr.")
        self.__name = value
        return

    @property
    def parameter(self) -> Parameter:
        """Parameter of the hero."""
        return self.__parameter

    @property
    def speed(self) -> float:
        """Speed of the hero."""
        return self.__speed

    @property
    def role(self) -> Role:
        """Role of the hero."""
        return self.__role

    @property
    def ultname(self) -> Tstr:
        """Hero skill name of the hero."""
        return self.__ultname

    @property
    def ultinvincible(self) -> str:
        """Iinvincibility time of the hero skill."""
        return self.__ultinvincible

    @property
    def haname(self) -> Tstr:
        """Ability name of the hero."""
        return self.__haname

    @property
    def is_collabo(self) -> bool:
        """wWhether or not the collaboration hero."""
        return self.__is_collabo

    @property
    def icon_path(self) -> str:
        """Path of the hero's icon."""
        return self.__icon_path

    @property
    def icon_color(self) -> int:
        """Icon color of the hero."""
        return self.__icon_color

    @property
    def image_path(self) -> str:
        """Path of the hero's image."""
        return self.__image_path

    @property
    def image_color(self) -> int:
        """Image color of the hero."""
        return self.__image_color

    @property
    def icon(self) -> ImageType:
        """Gets icon as ``PIL`` image."""
        return Image.open(self.icon_path)

    @property
    def image(self) -> ImageType:
        """Gets hero as ``PIL`` image."""
        return Image.open(self.image_path)

    @classmethod
    def read_json(cls, json: dict[str, Any], **kwargs: str) -> Self:
        """Class method to construct :class:`Hero` from :class:`dict`.

        Parameters
        ----------
        json: Dict[:class:`str`, :class:`Any`]
            Element of :file:`compass/data/hero.json.fernet`, that has the following
            sixteen keys;
                num, icon_color, image_color: :class:`int`
                name, setname, role, ultname, ultinvincible, haname, icon_name, image_name: :class:`str`
                attack, defense, physical, speed: :class:`float`
                is_collabo: :class:`bool`.
        **kwargs: :class:`str`
            Optional keyword arguments, that is used to supply multiple languages.
            This parameter may have the following six keys;
                en_name, en_ultname, en_haname, tw_name, tw_ultname, tw_haname: :class:`str`.

        """
        en_name = kwargs.get("en_name", json["name"])
        en_ultname = kwargs.get("en_ultname", json["ultname"])
        en_haname = kwargs.get("en_haname", json["haname"])
        tw_name = kwargs.get("tw_name", json["ultname"])
        tw_ultname = kwargs.get("tw_ultname", json["name"])
        tw_haname = kwargs.get("tw_haname", json["haname"])

        en_name = en_name if en_name else json["name"]
        en_ultname = en_ultname if en_ultname else json["ultname"]
        en_haname = en_haname if en_haname else json["haname"]
        tw_name = tw_name if tw_name else json["name"]
        tw_ultname = tw_ultname if tw_ultname else json["ultname"]
        tw_haname = tw_haname if tw_haname else json["haname"]

        d = {}
        d["_Hero__num"] = json["num"]
        d["_Hero__name"] = Tstr(**{
            Locale.japanese.value: json["name"],
            Locale.taiwan_chinese.value: tw_name,
            Locale.american_english.value: en_name,
            Locale.british_english.value: en_name,
        })
        d["_Hero__setname"] = json["setname"]
        d["_Hero__parameter"] = Parameter(json["attack"], json["defense"], json["physical"])
        d["_Hero__speed"] = json["speed"]
        d["_Hero__role"] = Role(json["role"])
        d["_Hero__ultname"] = Tstr(**{
            Locale.japanese.value: json["ultname"],
            Locale.taiwan_chinese.value: tw_ultname,
            Locale.american_english.value: en_ultname,
            Locale.british_english.value: en_ultname,
        })
        d["_Hero__ultinvincible"] = json["ultinvincible"]
        d["_Hero__haname"] = Tstr(**{
            Locale.japanese.value: json["name"],
            Locale.taiwan_chinese.value: tw_haname,
            Locale.american_english.value: en_haname,
            Locale.british_english.value: en_haname,
        })
        d["_Hero__is_collabo"] = json["is_collabo"]
        d["_Hero__icon_name"] = json["icon_name"]
        d["_Hero__icon_color"] = json["icon_color"]
        d["_Hero__image_name"] = json["image_name"]
        d["_Hero__image_color"] = json["image_color"]
        return cls(**d)
