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
    "Stage",
)


from dataclasses import dataclass
from typing import Any

from PIL import Image
from typing_extensions import Self

from .path import PATH
from .utils import ImageType, Locale, Tstr


@dataclass
class Stage(object):
    """Stage of Compass."""
    __name: Tstr
    __number: int
    __portal: int
    __filename: Tstr
    __is_official: bool

    __path: Tstr = Tstr("")

    def __post_init__(self) -> None:
        d = {}
        for locale in Locale:
            d[locale.value] = f"{PATH.STAGEIMG}/{self.__filename(locale)}.png"
        self.__path = Tstr(**d)

    def __str__(self) -> str:
        return f"【{self.number}on{self.number}】{self.name}"

    def image(self, locale: Locale = Locale.japanese) -> ImageType:
        """Gets ``PIL`` image.

        Parameters
        ----------
        locale: :class:`Locale`
            If a locale-supported image is available, it is returned.

        Returns
        -------
        :class:`ImageType`
            ``PIL`` image of the stage.

        """
        return Image.open(self.path(locale))

    @property
    def name(self) -> Tstr:
        """Name of the stage."""
        return self.__name

    @property
    def number(self) -> int:
        """Number of people per team on the stage."""
        return self.__number

    @property
    def portal(self) -> int:
        """Number of portals on the stage."""
        return self.__portal

    @property
    def path(self) -> Tstr:
        """Path of the image file."""
        return self.__path

    @property
    def is_official(self) -> bool:
        """Whether the stage is official or not."""
        return self.__is_official

    @classmethod
    def read_json(cls, json: dict[str, Any], **kwargs: str) -> Self:
        """Class method to construct :class:`Stage` from :class:`dict`.

        Parameters
        ----------
        json: Dict[:class:`str`, :class:`Any`]
            Element of :file:`compass/data/stage.json.fernet`, that has
            the following five keys;
                name, filename: :class:`str`
                number, portal: :class:`int`
                is_official: :class:`bool`.
        **kwargs: Dict[:class:`str`, :class:`str`]
            Optional keyword arguments, that is used to supply multiple languages.
            This parameter may have the following four keys;
                en_name, en_filename, tw_name, tw_filename: :class:`str`.

        """
        en_name = kwargs.get("en_name", json["name"])
        en_filename = kwargs.get("en_filename", json["filename"])
        tw_name = kwargs.get("tw_name", json["name"])
        tw_filename = kwargs.get("tw_filename", json["filename"])

        d = {}
        d["_Stage__name"] = Tstr(**{
            Locale.japanese.value: json["name"],
            Locale.taiwan_chinese.value: tw_name,
            Locale.american_english.value: en_name,
            Locale.british_english.value: en_name,
        })
        d["_Stage__number"] = json["number"]
        d["_Stage__portal"] = json["portal"]
        d["_Stage__filename"] = Tstr(**{
            Locale.japanese.value: json["filename"],
            Locale.taiwan_chinese.value: tw_filename,
            Locale.american_english.value: en_filename,
            Locale.british_english.value: en_filename,
        })
        d["_Stage__is_official"] = json["is_official"]
        return cls(**d)
