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
    "Card",
)

from dataclasses import dataclass
from tempfile import mkstemp
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from typing_extensions import Self

from .activation import Activation
from .attribute import Attribute
from .collabo import Collabo
from .path import PATH
from .rank import Rank
from .rarity import Rarity
from .status import Parameter, Status
from .utils import ImageType, Locale, Tstr, merge_images_vertical


@dataclass
class Card(object):
    """Card of Compass."""
    __name: Tstr
    __rarity: Rarity
    __types: list[str]
    __cool_time: int
    __activation: Activation
    __attribute: Attribute
    __rank: Rank
    __ability: Tstr
    __status: Status
    __abbreviation: list[str]
    __collabo: Collabo
    __filename: str
    __path: str = ""

    def __post_init__(self) -> None:
        self.__path = PATH.CARDIMG + "/" + self.__filename + ".jpg"

    def __str__(self) -> str:
        return "【" + "・".join(self.types) + "】" + self.name

    @property
    def image(self) -> ImageType:
        """Gets ``PIL`` image."""
        return Image.open(self.path)

    @property
    def name(self) -> Tstr:
        """Name of the card."""
        return self.__name

    @property
    def rarity(self) -> Rarity:
        """Rarity of the card."""
        return self.__rarity

    @property
    def types(self) -> list[str]:
        """List of the card types."""
        return self.__types

    @property
    def cool_time(self) -> int:
        """Cool time of the card."""
        return self.__cool_time

    @property
    def activation(self) -> Activation:
        """Activation time of the card."""
        return self.__activation

    @property
    def attribute(self) -> Attribute:
        """Attribute of the card."""
        return self.__attribute

    @property
    def rank(self) -> Rank:
        """Rank of the card available."""
        return self.__rank

    @property
    def ability(self) -> str:
        """The card's ability and detail."""
        return self.__ability

    @property
    def path(self) -> str:
        """Path of the card image file."""
        return self.__path

    @property
    def status(self) -> Status:
        """Status of the card."""
        return self.__status

    @property
    def abbreviation(self) -> list[str]:
        """The card's abbreviations."""
        if (not self.is_collabo) and (self.rarity == Rarity.UR):
            return self.__abbreviation + self.__name.values() + \
                   list(map(lambda wd: wd + "".join(self.types), self.attribute.related_terms))
        return self.__abbreviation + self.__name.values()

    @property
    def collabo(self) -> Collabo:
        """Collaboration of the card."""
        return self.__collabo

    @property
    def is_collabo(self) -> bool:
        """Whether or not it is a collaboration card."""
        return not (self.__collabo == Collabo.NONE or self.__collabo == Collabo.EX)

    @classmethod
    def read_json(cls, json: dict[str, Any], **kwargs: str) -> Self:
        """Class method to construct :class:`card` from :class:`dict`.

        Parameters
        ----------
        json: Dict[:class:`str`, :class:`Any`]
            Element of :file:`compass/data/card.json.fernet`, that has the following
            fourteen keys;
                name, rarity, activation, attribute, ability, rank, filename, collabo: :class:`str`
                types, abbreviation: List[:class:`str`]
                cool_time: :class:`int`
                atk, def, phs: Dict[:class:`str`, :class:`float`].
        **kwargs: :class:`str`
            Optional keyword arguments, that is used to supply multiple languages.
            This parameter may have the following four keys;
                en_name, en_ability, tw_name, tw_ability: :class:`str`.

        """
        en_name = kwargs.get("en_name", json["name"])
        en_ability = kwargs.get("en_ability", json["ability"])
        tw_name = kwargs.get("tw_name", json["name"])
        tw_ability = kwargs.get("tw_ability", json["ability"])

        en_name = en_name if en_name else json["name"]
        en_ability = en_ability if en_ability else json["ability"]
        tw_name = tw_name if tw_name else json["name"]
        tw_ability = tw_ability if tw_ability else json["ability"]

        d = {}
        d["_Card__name"] = Tstr(**{
            Locale.japanese.value: json["name"],
            Locale.taiwan_chinese.value: tw_name,
            Locale.american_english.value: en_name,
            Locale.british_english.value: en_name,
        })
        d["_Card__rarity"] = Rarity(json["rarity"].lower())
        d["_Card__types"] = json["types"]
        d["_Card__cool_time"] = json["cool_time"]
        d["_Card__activation"] = Activation(json["activation"])
        d["_Card__attribute"] = Attribute(json["attribute"])
        d["_Card__rank"] = Rank(json["rank"].lower())
        d["_Card__ability"] = Tstr(**{
            Locale.japanese.value: json["ability"],
            Locale.taiwan_chinese.value: tw_ability,
            Locale.american_english.value: en_ability,
            Locale.british_english.value: en_ability,
        })
        d["_Card__filename"] = json["filename"]
        d["_Card__status"] = Status(**{"atk":json["atk"],"def":json["def"],"phs":json["phs"]})
        d["_Card__collabo"] = Collabo(json["collabo"])
        d["_Card__abbreviation"] = json["abbreviation"]
        return cls(**d)

    def generate_image(self, path: str | None = None, level: int = 50,
                       locale: Locale = Locale.japanese) -> str:
        """Generates image with processing applied.

        Generates an image with embedded details such as card effects
        and cool time.

        Parameters
        ----------
        path: Optinal[:class:`str`]
            Destination to save the image to.
            If `None`, the image is saved in :file:`tmp` directory.
        level: :class:`int`
            Level of the card to be displayed.
        locale: :class:`Locale`
            If a corresponding image is available, it is used.

        Returns
        -------
        :class:`str`
            Destination to save the image to.

        """

        if path is None:
            _, path = mkstemp(".png")

        locale = Locale(locale)

        if locale == Locale.taiwan_chinese:
            font = ImageFont.truetype(PATH.TW_FONT, 26)
        else:
            font = ImageFont.truetype(PATH.JP_FONT, 26)

        img_above = Image.open(PATH.DETAIL.frame("above", locale))
        img_above.paste(Image.open(PATH.DETAIL.rarity(self.rarity)), (46, 30))

        draw = ImageDraw.Draw(img_above)
        draw.text((125,24), self.name.replace("∗","＊"), (255,255,255), font=font)
        img_above.paste(Image.open(PATH.DETAIL.level(level)), (78,35))

        img_below = Image.open(PATH.DETAIL.frame("below", locale))

        status: Parameter = self.status.get(str(level))

        atk_width = int(status.attack *2 /3)
        def_width = int(status.defense *17 /12)
        phs_width = int(status.physical *11 /140)

        atk_width = 336 if atk_width > 336 else atk_width
        def_width = 336 if def_width > 336 else def_width
        phs_width = 336 if phs_width > 336 else phs_width

        draw = ImageDraw.Draw(img_below)
        draw.rectangle((150, 87,150+atk_width,118), fill=(196,216,106))
        draw.rectangle((150,143,150+def_width,174), fill=(196,216,106))
        draw.rectangle((150,199,150+phs_width,230), fill=(196,216,106))

        img_below_alpha = Image.new("RGBA", img_below.size, (255,255,255,0))

        def fill_b(status: float, number: int) -> str:
            return ("b"*number + str(int(status)))[-number:]

        for i in range(4):
            img_below_alpha.paste(Image.open(PATH.DETAIL.status(fill_b(status.attack, 4)[i])),(419+16*i,97))
            img_below_alpha.paste(Image.open(PATH.DETAIL.status(fill_b(status.defense, 4)[i])),(419+16*i,153))
            img_below_alpha.paste(Image.open(PATH.DETAIL.status(fill_b(status.physical, 4)[i])),(419+16*i,209))

        img_below = Image.alpha_composite(img_below, img_below_alpha)
        img_below.paste(Image.open(PATH.DETAIL.activation(self.activation)),(624, 15))

        cool = f"bb{self.cool_time}"[-3:]
        for i in range(3):
            img_below.paste(Image.open(PATH.DETAIL.cool_time(cool[i])), (268+19*i,21))
        img_below.paste(Image.open(PATH.DETAIL.cool_time("sec")), (332,15))

        ability = self.ability.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))
        ability = [ability[i*19: (i+1)*19] for i in range(len(ability)//19 + 1)]
        ability = ability[:-1] if ability[-1] == "" else ability
        spacing = 5 - len(ability)

        img_middle = Image.open(PATH.DETAIL.frame("middle", locale))
        pilimg_list = [img_middle for _ in range(len(ability) - 1)]
        pilimg_list = [img_above] + pilimg_list + [img_below]
        ability = "\n".join(ability)
        img = merge_images_vertical(*pilimg_list, color=0xECEDED)
        draw = ImageDraw.Draw(img)
        draw.text((261,66), ability, (160,160,160), font=font, spacing=spacing)

        img.save(path)

        return path
