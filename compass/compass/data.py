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
    "CardData",
    "HeroData",
    "StageData",
)


import json
import os
from collections import UserList
from math import ceil, sqrt
from random import choice
from tempfile import mkstemp
from typing import Any, overload

from cryptography.fernet import Fernet
from PIL import Image, ImageDraw
from typing_extensions import Self

from .attribute import Attribute
from .card import Card
from .collabo import Collabo
from .hero import Hero
from .path import PATH
from .rank import Rank, _rank_order
from .rarity import Rarity
from .role import Role
from .stage import Stage
from .status import Parameter
from .utils import (Locale, Tstr, add_margin, merge_images,
                    merge_images_horizon, merge_images_vertical, similar)


class CardData(UserList[Card]):
    """Data of Compass card.

    To use this data, ``TOKEN`` to decrypt a json file is required.
    ``TOKEN`` must be set in an environment variable as ``BOT_CPS_TOKEN``.

    """

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, data: Self) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, tw: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str], tw: dict[str, str]) -> None:
        ...

    def __init__(self, *args: Card, **kwargs: dict[str, str]) -> None:
        super().__init__()

        if len(args) == 0:
            with open(PATH.EN_CARDJSON, "r") as f:
                en = kwargs.get("en", json.load(f))

            with open(PATH.TW_CARDJSON, "r") as f:
                tw = kwargs.get("tw", json.load(f))

            with open(PATH.CARDJSON, "rb") as f:
                fernet = Fernet(os.environ["BOT_CPS_TOKEN"])
                cards: list[dict[str, Any]] = json.loads(fernet.decrypt(f.read()))

            for card in cards:
                d = {
                    "en_name": en[card["name"]]["name"],
                    "en_ability": en[card["name"]]["ability"],
                    "tw_name": tw[card["name"]]["name"],
                    "tw_ability": tw[card["name"]]["ability"],
                }
                self.data.append(Card.read_json(card, **d))
        else:
            self.data = list(*args)

    def __str__(self) -> str:
        return f"{len(self)} Cards' Data"

    @overload
    def __getitem__(self, index: int) -> Card:
        ...

    @overload
    def __getitem__(self, key: str) -> Card:
        ...

    @overload
    def __getitem__(self, *keys: str) -> Card:
        ...

    @overload
    def __getitem__(self, slice: slice) -> Self:
        ...

    def __getitem__(self, *args) -> Self | Card:
        if isinstance(args[0], str):
            if args[0].isdigit():
                return super().__getitem__(int(args[0]))
            else:
                return self._guess_card(args[0])
        elif isinstance(*args, tuple) and list(map(type, *args)) == [str] * len(*args):
            retval = self.__class__([])
            for arg in list(*args):
                retval.append(self._guess_card(arg))
            return retval
        else:
            return super().__getitem__(*args)

    def _guess_card(self, key: str) -> Card:
        """Guesses :class:`compass.Card` from the input.

        Parameters
        ----------
        key: :class:`str`
            String similar to card name or abbreviation.

        Returns
        -------
        :class:`compass.Card`
            ``Card`` judged to be most similar to the input string.

        """

        return similar(key, self.data, lambda el: el.abbreviation)

    def divide(self) -> dict[str, Self]:
        """
        Divides into the following four types: ``offensive``, ``defensive``,
        ``supportive``, and ``recovery``.

        Returns
        -------
        Dict[:class:`str`, :class:`CardData`]
            The value returned is :class:`dict` and its keys are the following four.
            ``off`` for offensive cards, ``sup`` for support cards,
            ``def`` for defensive cards and ``rec`` for recovery cards.

        """
        type_dict = {"rec": ["癒",],
                     "sup": ["奪","止","閃","毒","害","人","除","押","黙","爆","弱","罠",],
                     "def": ["返","防","強",],
                     "off": ["近","周","遠","連",]}
        card_dict = {"off": self.__class__([]),
                     "def": self.__class__([]),
                     "sup": self.__class__([]),
                     "rec": self.__class__([]),}
        kind_list = ["rec", "sup", "def", "off"]

        def list_in_list(list1: list[Any], list2: list[Any]) -> bool:
            for el in list1:
                if el in list2:
                    return True
            return False

        for card in self:
            flag = False
            for kind in kind_list:
                if list_in_list(card.types, type_dict[kind]):
                    flag = True
                    card_dict[kind].append(card)
            if not flag:
                card_dict["sup"].append(card)

        return card_dict

    def get_card(self, *args: str | Attribute | Collabo | Rarity,
                  season: bool = False, normal: bool = True, collabo: bool = True) -> Card:
        """Returns data for card that satisfied the condition.

        Parameters
        ----------
        *args: :class:`str` | :class:`compass.Attribute` | :class:`compass.Collabo` | :class:`compass.Rarity`
            Specifies the condition for returns.
        season: :class:`bool`
            Whether or not to include season cards.
        normal: :class:`bool`
            Whether or not to include normal cards.
        collabo: :class:`bool`
            Whether or not to include collaboration cards.

        Returns
        -------
        :class:`compass.Card`
            Returns a card that satisfies the conditions at random.

        """
        cards = self.get_cards(*args, season=season, normal=normal, collabo=collabo)
        return choice(cards)

    def get_cards(self, *args: str | Attribute | Collabo | Rarity,
                  season: bool = False, normal: bool = True, collabo: bool = True) -> Self:
        """Returns data for cards that satisfied the condition.

        Parameters
        ----------
        *args: :class:`str` | :class:`compass.Attribute` | :class:`compass.Collabo` | :class:`compass.Rarity`
            Specifies the condition for returns.
        season: :class:`bool`
            Whether or not to include season cards.
        normal: :class:`bool`
            Whether or not to include normal cards.
        collabo: :class:`bool`
            Whether or not to include collaboration cards.

        Returns
        -------
        :class:`CardData`
            Returns all cards that satisfy the condition.

        """

        attributes, rarities, collabos = [], [], []
        _attributes, _rarities, _collabos = list(Attribute), list(Rarity), list(Collabo)

        for arg in args:
            if arg in _attributes:
                attributes.append(Attribute(arg.lower()))
            elif arg in _rarities:
                rarities.append(Rarity(arg.lower()))
            elif arg in _collabos:
                collabos.append(Collabo(arg))
            else:
                raise ValueError("No object matches the string.")

        if attributes == []:
            attributes = _attributes
        if rarities == []:
            rarities = _rarities
        if collabos == []:
            collabos = _collabos

        retval = self.__class__([])
        if season:
            retval.extend(self.get_season_cards(attributes, rarities))
        if normal:
            retval.extend(self.get_normal_cards(attributes, rarities))
        if collabo:
            retval.extend(self.get_collabo_cards(attributes, rarities, collabos))
        return retval

    def get_season_cards(self, attributes: list[Attribute] = list(Attribute),
                         rarities: list[Rarity] = list(Rarity)) -> Self:
        """Returns data for season cards.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_cards``
        function. In fact, this function is called within the ``get_cards``
        function.

        Parameters
        ----------
        attributes: List[:class:`compass.Attribute`]
            Conditions relating to the attributes of cards.
        rarities: List[:class:`compass.Rarity`]
            Conditions relating to the rarities of cards.

        Returns
        -------
        :class:`CardData`
            Returns all **season** cards that satisfy the conditions given.

        """
        retval = self.__class__([])
        for card in self:
            if (card.rank == Rank.EX) and (card.rarity in rarities) and \
               (card.attribute in attributes):
                retval.append(card)
        return retval

    def get_normal_cards(self, attributes: list[Attribute] = list(Attribute),
                         rarities: list[Rarity] = list(Rarity)) -> Self:
        """Returns data for normal cards.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_cards``
        function. In fact, this function is called within the ``get_cards``
        function.

        Parameters
        ----------
        attributes: List[:class:`compass.Attribute`]
            Conditions relating to the attributes of cards.
        rarities: List[:class:`compass.Rarity`]
            Conditions relating to the rarities of cards.

        Returns
        -------
        :class:`CardData`
            Returns all **normal** cards that satisfy the conditions given.

        """
        retval = self.__class__([])
        for card in self:
            if (card.rank != Rank.EX) and (card.rank in _rank_order) and \
               (card.rarity in rarities) and (card.attribute in attributes):
                retval.append(card)
        return retval

    def get_collabo_cards(self, attributes: list[Attribute] = list(Attribute),
                         rarities: list[Rarity] = list(Rarity),
                         collabos: list[Collabo] = list(Collabo)) -> Self:
        """Returns data for collaboration cards.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_cards``
        function. In fact, this function is called within the ``get_cards``
        function.

        Parameters
        ----------
        attributes: List[:class:`compass.Attribute`]
            Conditions relating to the attributes of cards.
        rarities: List[:class:`compass.Rarity`]
            Conditions relating to the rarities of cards.
        collabos: List[:class:`compass.Collabo`]
            Conditions relating to the collaborations of cards.

        Returns
        -------
        :class:`CardData`
            Returns all **collaboration** cards that satisfy the conditions given.

        """
        retval = self.__class__([])
        for card in self:
            if (card.rank != Rank.EX) and (card.rank not in _rank_order) and \
               (card.collabo != Collabo.NONE) and (card.collabo in collabos) and \
               (card.rarity in rarities) and (card.attribute in attributes):
                retval.append(card)
        return retval

    def generate_image(self, path: str | None = None, levels: list[int] | None = [50]*4,
                       locale: Locale = Locale.japanese) -> str:
        """Generates an image with processing applied.

        The behaviour depends on the number of cards.
        If the number of cards is one, an image with embedded card details
        is generated.
        When the number of cards is between two and four, an image of a deck
        with those cards is generated.
        If the number of cards is greater than these, an image of a list of
        cards is generated.

        Parameters
        ----------
        path: Optinal[:class:`str`]
            Destination to save the image to.
            If `None`, the image is saved in :file:`tmp` directory.
        levels: Optional[List[int]]
            Cards' level.
        locale: :class:`Locale`
            If a corresponding image is available, it is used.

        Returns
        -------
        :class:`str`
            Destination to save the image to.

        Raises
        ------
        RuntimeError
            The number of cards must be at least one. If there are zero cards,
            this error is raised.

        """

        if path is None:
            _, path = mkstemp(".png")

        locale = Locale(locale)

        if len(self) == 0:
            raise RuntimeError("Invalid length of data.")
        elif len(self) == 1:
            retval = self[0].generate_image(path=path, level=levels[0], locale=locale)
        elif 2 <= len(self) <= 4:
            retval = self.generate_deck(path=path, levels=levels, locale=locale)
        else:
            retval = self.generate_large_image(path=path)
        return retval

    def generate_deck(self, path: str | None = None, levels: list[int] | None = [50]*4,
                      locale: Locale = Locale.japanese) -> str:
        """Generates deck image with processing applied.

        Parameters
        ----------
        path: Optinal[:class:`str`]
            Destination to save the image to.
            If `None`, the image is saved in :file:`tmp` directory.
        levels: Optional[List[int]]
            Cards' level.
        locale: :class:`Locale`
            If a corresponding image is available, it is used.

        Returns
        -------
        :class:`str`
            Destination to save the image to.

        Raises
        ------
        RuntimeError
            The number of cards must be between one and four.
            If they do not belong to this range, raises error.

        """

        if not (1 <= len(self) <= 4):
            raise RuntimeError("Length of data must be between 1 and 4.")

        while(len(self) > len(levels)):
            levels.extend([50])

        if path is None:
            _, path = mkstemp(".png")

        locale = Locale(locale)

        pilimages = [card.image for card in self]

        for _ in range(4 - len(self)):
            pilimages.append(Image.open(PATH.DECK.blank()))

        imgprocs = []
        imgprocs.append(add_margin(pilimages[0], top=10, right=10, bottom=10, left=80, color=0xECEDED))
        imgprocs.append(add_margin(pilimages[1], top=10, right=10, bottom=10, left=10, color=0xECEDED))
        imgprocs.append(add_margin(pilimages[2], top=10, right=10, bottom=10, left=10, color=0xECEDED))
        imgprocs.append(add_margin(pilimages[3], top=10, right=80, bottom=10, left=10, color=0xECEDED))

        img_deck = merge_images_horizon(*imgprocs, color=0xECEDED)
        img_deck = img_deck.resize((795, (img_deck.height*795)//img_deck.width))

        img_above = Image.open(PATH.DECK.frame("above", locale))
        img_below = Image.open(PATH.DECK.frame("below", locale))

        img_deck_main = Image.new("RGBA", img_deck.size, (255,255,255,0))
        img_deck_alpha = Image.new("RGBA", img_deck.size, (255,255,255,0))

        img_deck_main.paste(img_deck,(0,0))
        for i in range(len(levels)):
            img_deck_alpha.paste(Image.open(PATH.DECK.level(str(levels[i]))).resize(size=(40,23)),(75+170*i,65))

        img_deck = Image.alpha_composite(img_deck_main,img_deck_alpha)

        img = merge_images_vertical(*[img_above, img_deck, img_below], color=0xECEDED)

        status = Parameter(0, 0, 0)
        for i in range(len(self)):
            status += self[i].status[str(levels[i])]

        atk_width = int(status.attack * (142/480))
        def_width = int(status.defense * (56/95))
        phs_width = int(status.physical * (77/2331))

        atk_width = 590 if atk_width > 590 else atk_width
        def_width = 590 if def_width > 590 else def_width
        phs_width = 590 if phs_width > 590 else phs_width

        draw = ImageDraw.Draw(img)
        draw.rectangle((157,394,157+atk_width,425), fill=(196,216,106))
        draw.rectangle((157,440,157+def_width,471), fill=(196,216,106))
        draw.rectangle((157,486,157+phs_width,517), fill=(196,216,106))

        img_alpha = Image.new("RGBA", img.size, (255,255,255,0))

        def fill_b(status: float, number: int) -> str:
            return ("b"*number + str(int(status)))[-number:]

        for i in range(5):
            img_alpha.paste(Image.open(PATH.DECK.status(fill_b(status.attack, 5)[i])),(660+16*i,400))
            img_alpha.paste(Image.open(PATH.DECK.status(fill_b(status.defense, 5)[i])),(660+16*i,446))
            img_alpha.paste(Image.open(PATH.DECK.status(fill_b(status.physical, 5)[i])),(660+16*i,492))

        Image.alpha_composite(img, img_alpha).save(path)

        return path

    def generate_large_image(self, path: str | None = None) -> str:
        """Generates large image with processing applied.

        Parameters
        ----------
        path: Optinal[:class:`str`]
            Destination to save the image to.
            If `None`, the image is saved in :file:`tmp` directory.

        Returns
        -------
        :class:`str`
            Destination to save the image to.

        Raises
        ------
        RuntimeError
            The number of cards must be at least one. If there are zero cards,
            this error is raised.

        """

        if len(self) == 0:
            raise RuntimeError("Invalid length of data.")

        if path is None:
            _, path = mkstemp(".png")

        if len(self) == 1:
            self[0].image.save(path)
        else:
            imgs = [card.image for card in self]
            number = int(ceil(sqrt(len(self))))
            merge_images(*imgs, number=number).save(path)
        return path

class HeroData(UserList[Hero]):
    """Data of Compass hero.

    To use this data, ``TOKEN`` to decrypt a json file is required.
    ``TOKEN`` must be set in an environment variable as ``BOT_CPS_TOKEN``.

    """

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, data: Self) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, tw: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str], tw: dict[str, str]) -> None:
        ...

    def __init__(self, *args: tuple[Hero], **kwargs: dict[str, str]) -> None:
        super().__init__()

        if len(args) == 0:
            with open(PATH.EN_HEROJSON, "r") as f:
                en = kwargs.get("en", json.load(f))

            with open(PATH.TW_HEROJSON, "r") as f:
                tw = kwargs.get("tw", json.load(f))

            with open(PATH.HEROJSON, "rb") as f:
                fernet = Fernet(os.environ["BOT_CPS_TOKEN"])
                heroes: list[dict[str, Any]] = json.loads(fernet.decrypt(f.read()))

            for hero in heroes:
                d = {
                    "en_name": en[hero["name"]]["name"],
                    "en_ultname": en[hero["name"]]["ultname"],
                    "en_haname": en[hero["name"]]["haname"],
                    "tw_name": tw[hero["name"]]["name"],
                    "tw_ultname": tw[hero["name"]]["ultname"],
                    "tw_haname": tw[hero["name"]]["haname"],
                }
                self.data.append(Hero.read_json(hero, **d))
        else:
            self.data = list(*args)

    def __str__(self) -> str:
        return f"{len(self)} Heroes' Data"

    @overload
    def __getitem__(self, index: int) -> Hero:
        ...

    @overload
    def __getitem__(self, key: str) -> Hero:
        ...

    @overload
    def __getitem__(self, slice: slice) -> Self:
        ...

    def __getitem__(self, *args) -> Self | Hero:
        if isinstance(args[0], str):
            if args[0].isdigit():
                return super().__getitem__(int(args[0]))
            else:
                return self._guess_hero(args[0])
        else:
            return super().__getitem__(*args)

    def _guess_hero(self, key: str) -> Hero:
        """Guesses :class:`compass.Hero` from the input.

        Parameters
        ----------
        key: :class:`str`
            String similar to hero name.

        Returns
        -------
        :class:`compass.Hero`
            ``Hero`` judged to be most similar to the input string.

        """

        return similar(key, self.data, lambda el: el.name.values() + [str(el)])

    def get_hero(self, *args: str | Role, original: bool = True,
                   collabo: bool = True, exclusion: bool = True) -> Hero:
        """Returns data for hero that satisfied the condition.

        Parameters
        ----------
        *args: :class:`str` | :class:`compass.Role`
            Specifies the condition for returns.
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`compass.Hero`
            Returns a hero that satisfies the conditions at random.

        """
        heroes = self.get_heroes(*args, original=original, collabo=collabo, exclusion=exclusion)
        return choice(heroes)

    def get_heroes(self, *args: str | Role, original: bool = True,
                   collabo: bool = True, exclusion: bool = True) -> Self:
        """Returns data for heroes that satisfied the condition.

        Parameters
        ----------
        *args: :class:`str` | :class:`compass.Role`
            Specifies the condition for returns.
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`HeroData`
            Returns all heroes that satisfy the condition.

        """
        args = list(map(lambda arg: arg.lower(), args))
        if args == []:
            args = list(Role)

        retval = self.__class__([])
        if Role.ATTACKER in args:
            retval.extend(self.get_attacker_heroes(original, collabo, exclusion))
        if Role.GUNNER in args:
            retval.extend(self.get_gunner_heroes(original, collabo, exclusion))
        if Role.SPRINTER in args:
            retval.extend(self.get_sprinter_heroes(original, collabo, exclusion))
        if Role.TANK in args:
            retval.extend(self.get_tank_heroes(original, collabo, exclusion))

        return retval

    def get_attacker_heroes(self, original: bool = True, collabo: bool = True,
                            exclusion: bool = True) -> Self:
        """Returns data for attacker heroes.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_heroes``
        function. In fact, this function is called within the ``get_heroes``
        function.

        Parameters
        ----------
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`HeroData`
            Returns all **attacker** heroes that satisfy the condition.

        """
        exclusion_list = (
            "マルコス'55(1凸)",
            "マルコス'55(2凸)",
            "マルコス'55(3凸)",
            "サーティーン(atk)",
        )

        retval = self.__class__([])
        for hero in self:
            if hero.role == Role.ATTACKER and \
               ((not exclusion) or (exclusion and hero.name not in exclusion_list)) and \
               ((not hero.is_collabo and original) or (hero.is_collabo and collabo)):
                retval.append(hero)

        return retval

    def get_gunner_heroes(self, original: bool = True, collabo: bool = True,
                            exclusion: bool = True) -> Self:
        """Returns data for gunner heroes.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_heroes``
        function. In fact, this function is called within the ``get_heroes``
        function.

        Parameters
        ----------
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`HeroData`
            Returns all **gunner** heroes that satisfy the condition.

        """
        exclusion_list = (
            "猫宮ひなた(SG)",
        )

        retval = self.__class__([])
        for hero in self:
            if hero.role == Role.GUNNER and \
               ((not exclusion) or (exclusion and hero.name not in exclusion_list)) and \
               ((not hero.is_collabo and original) or (hero.is_collabo and collabo)):
                retval.append(hero)

        if exclusion:
            for val in retval:
                # 13
                if val.name == "サーティーン(gun)":
                    d = {}
                    for locale in Locale:
                        d[locale.value] = val.name(locale.value).replace("(gun)","")
                    val.name = Tstr(**d)
                # nekomiya
                if val.name == "猫宮ひなた(AR)":
                    d = {}
                    for locale in Locale:
                        d[locale.value] = val.name(locale.value).replace("(AR)","")
                    val.name = Tstr(**d)

        return retval

    def get_sprinter_heroes(self, original: bool = True, collabo: bool = True,
                            exclusion: bool = True) -> Self:
        """Returns data for sprinter.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_heroes``
        function. In fact, this function is called within the ``get_heroes``
        function.

        Parameters
        ----------
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`HeroData`
            Returns all **sprinter** heroes that satisfy the condition.

        """
        exclusion_list = (
            "ピエール77世(HS)",
        )

        retval = self.__class__([])
        for hero in self:
            if hero.role == Role.SPRINTER and \
               ((not exclusion) or (exclusion and hero.name not in exclusion_list)) and \
               ((not hero.is_collabo and original) or (hero.is_collabo and collabo)):
                retval.append(hero)

        return retval

    def get_tank_heroes(self, original: bool = True, collabo: bool = True,
                            exclusion: bool = True) -> Self:
        """Returns data for tank.

        This function is intended for use inside the library, since it is
        possible to simulate the same behaviour with the ``get_heroes``
        function. In fact, this function is called within the ``get_heroes``
        function.

        Parameters
        ----------
        original: :class:`bool`
            Whether or not to include original heroes.
        collabo: :class:`bool`
            Whether or not to include collabo heroes.
        exclusion: :class:`bool`
            Whether or not to apply exclusion filters.

        Returns
        -------
        :class:`HeroData`
            Returns all **tank** heroes that satisfy the condition.

        """
        exclusion_list = ()

        retval = self.__class__([])
        for hero in self:
            if hero.role == Role.TANK and \
               ((not exclusion) or (exclusion and hero.name not in exclusion_list)) and \
               ((not hero.is_collabo and original) or (hero.is_collabo and collabo)):
                retval.append(hero)

        return retval

class StageData(UserList[Stage]):
    """Data of Compass stage.

    To use this data, ``TOKEN`` to decrypt a json file is required.
    ``TOKEN`` must be set in an environment variable as ``BOT_CPS_TOKEN``.

    """

    @overload
    def __init__(self) -> None:
        ...

    @overload
    def __init__(self, data: Self) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, tw: dict[str, str]) -> None:
        ...

    @overload
    def __init__(self, *, en: dict[str, str], tw: dict[str, str]) -> None:
        ...

    def __init__(self, *args: Stage, **kwargs: dict[str, str]) -> None:
        super().__init__()

        if len(args) == 0:
            with open(PATH.EN_STAGEJSON, "r") as f:
                en = kwargs.get("en", json.load(f))

            with open(PATH.TW_STAGEJSON, "r") as f:
                tw = kwargs.get("tw", json.load(f))

            with open(PATH.STAGEJSON, "rb") as f:
                fernet = Fernet(os.environ["BOT_CPS_TOKEN"])
                stages: list[dict[str, Any]] = json.loads(fernet.decrypt(f.read()))

            for stage in stages:
                d = {
                    "en_name": en[stage["name"]]["name"],
                    "en_filename": en[stage["name"]]["filename"],
                    "tw_name": tw[stage["name"]]["name"],
                    "tw_filename": tw[stage["name"]]["filename"],
                }
                self.data.append(Stage.read_json(stage, **d))
        else:
            self.data = list(*args)

    def __str__(self) -> str:
        return f"{len(self)} Stages' Data"

    @overload
    def __getitem__(self, index: int) -> Stage:
        ...

    @overload
    def __getitem__(self, key: str) -> Stage:
        ...

    @overload
    def __getitem__(self, slice: slice) -> Self:
        ...

    def __getitem__(self, *args) -> Self | Stage:
        if isinstance(args[0], str):
            if args[0].isdigit():
                return super().__getitem__(int(args[0]))
            else:
                return self._guess_stage(args[0])
        else:
            return super().__getitem__(*args)

    def _guess_stage(self, key: str) -> Stage:
        """Guesses :class:`compass.Stage` from the input.

        Parameters
        ----------
        key: :class:`str`
            String similar to stage name.

        Returns
        -------
        :class:`compass.Stage`
            ``Stage`` judged to be most similar to the input string.

        """

        return similar(key, self.data, lambda el: el.name.values())

    def get_stage(self, number: int = 3) -> Stage:
        """Returns data for stage that satisfied the condition.

        Parameters
        ----------
        number: :class:`int`
            Number of people per team.

        Returns
        -------
        :class:`compass.Stage`
            Returns a stage that satisfies the condition at random.

        """
        stages = self.get_stages(number)
        return choice(stages)

    def get_stages(self, number: int = 3) -> Self:
        """Returns data for stages that satisfied the condition.

        Parameters
        ----------
        number: :class:`int`
            Number of people per team.

        Returns
        -------
        :class:`StageData`
            Returns all stages that satisfies the condition.

        """
        retval = self.__class__([])
        for stage in self:
            if stage.number == number and stage.is_official:
                retval.append(stage)

        return retval
