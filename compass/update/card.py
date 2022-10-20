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

import logging

logger = logging.getLogger(__name__)


import asyncio
import hashlib
import io
import json
from copy import deepcopy
from re import compile

import aiohttp
import Levenshtein
from compass import Rarity, translator
from compass.path import PATH
from compass.utils import convert_to_jpg, resize_unification
from cryptography.fernet import Fernet
from PIL import Image

from utils import generate_diff_html, request

GAMERCH_URL = "https://gamerch.com/compass/entry/{0}"
RARITY_ENTRY_NUM = {str(key): value for key, value in zip(Rarity, range(454738, 454734, -1))}


async def get_cards_info(rarity: Rarity) -> list[dict[str, Rarity | int]]:
    """|coro|

    Gets specific rarity cards infomation from ``Gamerch``.

    Parameters
    ----------
    rarity: :class:`compass.Rarity`
        Specifies rarity in order to get cards.

    Returns
    -------
    List[Dict[:class:`str`, :class:`compass.Rarity` | :class:`int`]]
        Rarity and entry number list.

    """

    url = GAMERCH_URL.format(RARITY_ENTRY_NUM[str(rarity)])
    soup = await request(url)

    mu_wikidb_list = soup.find_all("div", class_="mu__wikidb-list")
    mu_table = []
    for mu_wikidb in mu_wikidb_list:
        mu_table.extend(
            mu_wikidb.find_all("tr", class_=compile(r"mu__table--row([2-9]|[1-9][0-9]+)"))
        )
    rarity_href = list(map(lambda el: {"rarity": rarity,
                                       "href": int(el.find("a")["href"].replace(GAMERCH_URL.format(""), ""))},
                           mu_table))

    logger.info(f"Gets {len(rarity_href)} cards info from {url}.")

    return rarity_href


async def download_image(url: str, dirname: str) -> str:
    """|coro|

    Downloads image from url and saves it to dirname as hashed name.

    Parameters
    ----------
    url: :class:`str`
        The URL at which the image exists.
    dirname: :class:`str`
        Directory name which the image save to.

    Returns
    -------
    :class:`str`
        The image name (filename) that is hashed it.

    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                logger.error(f"Access to {url} was terminated with status code {r.status}")
                exit(1)

            bytes_img = await r.read()

    filename = hashlib.md5(bytes_img).hexdigest()
    img = Image.open(io.BytesIO(bytes_img))
    img = convert_to_jpg(resize_unification(img))
    img.save(f"{dirname}/{filename}.jpg")

    return filename


async def get_card_info(rarity: Rarity, href: int) -> dict[str, str | list[str] | int | dict[str, float]]:
    """|coro|

    Gets a card information from ``Gamerch``.

    Parameters
    ----------
    rarity: :class:`compass.Rarity`
        Card's rarity.
    href: :class:`str`
        Gamerch entry number, using as ``GAMERCH_URL.format(href)``.

    Returns
    -------
    Dict[:class:`str`, :class:`str` | List[:class:`str`] | :class:`int` | Dict[:class:`str`, :class:`float`]]
        Card's data; name, types, cool_time, ..., and so on.

    """

    soup = await request(GAMERCH_URL.format(href))

    markup = soup.find("div", class_="markup mu")

    card = {"name": None, "rarity": str(rarity).lower(), "types": [], "cool_time": 9999,
            "activation": None, "attribute": None, "rank": None, "ability": None,
            "filename": None, "atk": {}, "def": {}, "phs": {},
            "collabo": "", "abbreviation": []}

    for lv in [1, 20, 30, 40, 50, 60]:
        card["atk"][str(lv)], card["def"][str(lv)], card["phs"][str(lv)] = 0., 0., 0.

    card["name"] = markup.find("h2", class_="mu__h-large").text.replace("の基本データ", "") \
                         .replace("／","/").replace("［HF］"," [HF]")

    legacy_top = markup.find("div", class_="legacy-db-tpl_top")
    legacy_middle = markup.find("div", class_="legacy-db-tpl_middle")
    legacy_bottom = markup.find("div", class_="legacy-db-tpl_bottom")

    type1 = legacy_top.find("tr", class_="mu__table--row2").find("td", class_="mu__table--col2").text
    type2 = legacy_top.find("tr", class_="mu__table--row3").find("td", class_="mu__table--col2").text

    card["types"].append(type1)

    if "/" in type2:
        card["types"].extend(type2.split("/"))
    elif type2 != "-":
        card["types"].append(type2)

    card["cool_time"] = int(legacy_top.find("tr", class_="mu__table--row4") \
                                      .find("td", class_="mu__table--col2").text)

    card["activation"] = legacy_top.find("tr", class_="mu__table--row5") \
                                   .find("td", class_="mu__table--col2").text

    card["attribute"] = legacy_top.find("tr", class_="mu__table--row6") \
                                  .find("td", class_="mu__table--col2").text

    card["rank"] = legacy_top.find("tr", class_="mu__table--row7") \
                             .find("td", class_="mu__table--col2").text.lower()
    if card["rank"] == "シーズン報酬":
        card["rank"] = "ex"
    elif card["rank"] == "s1":
        card["rank"] = "s"

    value = legacy_middle.find("tr", class_="mu__table--row2") \
                         .find("td", class_="mu__table--col1").string
    card["atk"]["1"] = int(value) if value.isdecimal() else 0.

    value = legacy_middle.find("tr", class_="mu__table--row2") \
                         .find("td", class_="mu__table--col2").string
    card["def"]["1"] = int(value) if value.isdecimal() else 0.

    value = legacy_middle.find("tr", class_="mu__table--row4") \
                         .find("td", class_="mu__table--col1").string
    card["phs"]["1"] = int(value) if value.isdecimal() else 0.

    trans = str.maketrans("１２３４５６７８９０()％+&", "1234567890（）%＋＆")
    card["ability"] = legacy_bottom.find_all("div", "mu__table")[1] \
                                   .find("tr", class_="mu__table--row2") \
                                   .find("td", class_="mu__table--col1") \
                                   .text.translate(trans).replace("\n", " ")
    img_url = markup.find("span", class_="mu__img").find("picture") \
                    .find("source").find("img")["data-original"]

    card["filename"] = await download_image(img_url, PATH.CARDIMG)

    return card


def closest_index(cards: list[dict], name: str) -> int:
    """Gets closest index from cards and name.

    Parameters
    ----------
    cards: List[:class:`dict`]
        Cards data list.
    name: :class:`dict`
        The name of the card to look for.

    Returns
    -------
    :class:`int`
        Closest index.

    """

    for card in cards:
        if translator(card["name"]) == translator(name):
            return cards.index(card)

    logger.info(f"\"{name}\" is not == judged.")

    for card in cards:
        if translator(card["name"]) in translator(name):
            logger.info("The closest card name is %s." % card["name"])
            return cards.index(card)

    for card in cards:
        if translator(name) in translator(card["name"]):
            logger.info("The closest card name is %s." % card["name"])
            return cards.index(card)

    jaro_list = []
    for card in cards:
        jaro_dist = Levenshtein.jaro_winkler(translator(name), translator(card["name"]))
        jaro_list.append(jaro_dist)

    index = jaro_list.index(max(jaro_list))
    logger.info("The closest card name is %s." % cards[index]["name"])
    return index


def data_overwrites(cards: list[dict], yagis: list[dict]) -> None:
    """Overwrites cards data using yagi data.

    Parameters
    ----------
    cards: List[:class:`dict`]
        Cards data which get from `Gamerch`.
    yagis: List[:class:`dict`]
        Yagi Simulator data.

    """

    for yagi in yagis:
        # special process for card, "ラム（SR）"
        if yagi["name"] == "ラム":
            index = closest_index(cards, yagi["name"] + "（SR）")
        else:
            index = closest_index(cards, yagi["name"])
        cards[index]["name"] = yagi["name"]
        if not yagi["ability"] == "-":
            cards[index]["ability"] = yagi["ability"]
        for status in ["atk", "def", "phs"]:
            for lv in range(20, 70, 10):
                cards[index][status][str(lv)] = yagi[status + str(lv)]
        cards[index]["rank"] = yagi["rank"]
        cards[index]["collabo"] = yagi["collabo"]
    return


async def get_abbreviations() -> list[dict[str, str]]:
    """|coro|

    Gets card abbreviations from ``Gamerch``.

    Returns
    -------
    List[Dict[:class:`str`, :class:`str`]]
        List of card name and abbreviation.

    """

    soup = await request(GAMERCH_URL.format(454698))

    abbs: list[dict[str, str]] = []

    li_list = []
    for closebox in soup.find_all("div", class_="mu__closebox--wrap")[11:15]:
        li_list.extend(closebox.find_all("li", class_="mu__list--1"))

    abbs = list(map(lambda li: {"name": li.find("a").text,
                                "abbreviation": li.find("span", class_="mu__text-bolder").text},
                    li_list))

    return abbs


async def set_abbreviation(cards: list[dict], name: str, abbreviation: str) -> None:
    """|coro|

    Sets the abbreviation to cards data.

    Parameters
    ----------
    cards: List[:class:`dict`]
        Cards data which get from ``Gamerch`` and Yagi Simu.
    name: :class:`str`
        Card name.
    abbreviation: :class:`str`
        Abbreviation of the card corresponding to the name.

    """

    index = closest_index(cards, name)
    cards[index]["abbreviation"].append(abbreviation)
    return


async def __main__(yagi_url: str, fernet_key: str) -> None:
    """|coro|

    Main function to update compass card data.

    Parameters
    ----------
    yagi_url: :class:`str`
        ``URL`` of Yagi Simulator.
    fernet_key: :class:`str`
        A URL-safe base64-encoded 32-byte key.

    """

    # gets data from Gamerch
    cards_info: list[dict[str, Rarity | str]] = []

    for rarity in Rarity:
        cards_info.extend(await get_cards_info(rarity))

    cards_info.sort(key=lambda el: el["href"])

    cards = await asyncio.gather(*[get_card_info(**info) for info in cards_info])
    logger.info(f"Gets {len(cards)} cards data.")

    # gets data from yagisimu (yagi_url)
    soup = await request(yagi_url)
    yagis: list[dict] = json.loads(soup.find("p").text)
    logger.info(f"Gets {len(yagis)} cards data from Yagi Simulator.")
    data_overwrites(cards, yagis)

    # updates abbreviation
    abbs_data = await get_abbreviations()
    logger.info(f"Gets {len(abbs_data)} abbreviations.")
    for abb_data in abbs_data:
        await set_abbreviation(cards, **abb_data)

    # keep old and new version data
    fernet = Fernet(fernet_key)
    with open(PATH.CARDJSON, "rb") as f:
        cards_old = json.loads(fernet.decrypt(f.read()))

    cards_new = deepcopy(cards)

    # dumps card data to json file
    with open(PATH.CARDJSON, "wb") as f:
        bytes_str = json.dumps(cards, ensure_ascii=False, indent=4).encode()
        f.write(fernet.encrypt(bytes_str))

    # checks diffs between the old and the new
    html = generate_diff_html(cards_old, cards_new)
    print(html)

    logger.info("All steps have been completed.")
