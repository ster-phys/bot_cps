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


import difflib
import json

import aiohttp
from bs4 import BeautifulSoup


async def request(url: str) -> BeautifulSoup | None:
    """|coro|

    Sends a ``GET`` request.

    Parameters
    ----------
    url: :class:`str`
        URL for the new :class:`aiohttp.ClientSession` object.

    Returns
    -------
    Optional[:class:`BeautifulSoup`]
        :class:`BeautifulSoup` object corresponding to url.

    """

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                logger.error(f"Access to {url} was terminated with status code {r.status}")
                exit(1)
            html = await r.text(encoding="utf-8")
            soup = BeautifulSoup(html, "lxml")

    return soup


def generate_diff_html(json1: dict | list[dict], json2: dict | list[dict]) -> str:
    """Checks diffs between two objects.

    Parameters
    ----------
    json1: :class:`dict` | List[:class:`dict`]
        An object that can be ``json.dumps`` to which to compare
        the differences.

    json2: :class:`dict` | List[:class:`dict`]
        An object that can be ``json.dumps`` to which to compare
        the differences.

    Returns
    -------
    :class:`str`
        Differences written in html.

    """

    diff = difflib.HtmlDiff(tabsize=4)
    old_str = json.dumps(json1, ensure_ascii=False, indent=4)
    new_str = json.dumps(json2, ensure_ascii=False, indent=4)
    return diff.make_table(old_str.splitlines(), new_str.splitlines(),
                           context=True, numlines=0)
