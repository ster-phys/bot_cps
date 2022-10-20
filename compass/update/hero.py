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


import json
from copy import deepcopy

import cv2
from compass.path import PATH
from cryptography.fernet import Fernet
from sklearn.cluster import KMeans

from utils import generate_diff_html, request


class MainColor(object):
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.rgb: tuple[int, int, int] = ()
        self.color: int = self.get_main_color()

    def __int__(self) -> int:
        return self.color

    def __str__(self) -> str:
        return f"\033[38;2;{self.rgb[0]};{self.rgb[1]};{self.rgb[2]}m ■ \033[0m"

    def get_main_color(self) -> int:
        """Caluculate main color."""
        cv2img = cv2.imread(self.path)
        cv2img = cv2.cvtColor(cv2img, cv2.COLOR_BGR2RGB)
        cv2img = cv2img.reshape((cv2img.shape[0] * cv2img.shape[1], 3))

        cluster = KMeans(n_clusters=5)
        cluster.fit(X=cv2img)
        cluster_centers_arr = cluster.cluster_centers_.astype(int, copy=False)

        self.rgb = tuple(cluster_centers_arr[0])
        colorHexStr = "0x%02x%02x%02x" % tuple(cluster_centers_arr[0])

        return int(colorHexStr,0)


async def __main__(yagi_url: str, fernet_key: str) -> None:
    """|coro|

    Main function to update compass hero data.

    Parameters
    ----------
    yagi_url: :class:`str`
        ``URL`` of Yagi Simulator.
    fernet_key: :class:`str`
        A URL-safe base64-encoded 32-byte key.

    """

    # get data from yagisimu (yagi_url)
    soup = await request(yagi_url)
    yagis: list[dict] = json.loads(soup.find("p").text)
    logger.info(f"Gets {len(yagis)} cards data from Yagi Simulator.")

    # read hero json data
    fernet = Fernet(fernet_key)
    with open(PATH.HEROJSON, "rb") as f:
        heroes = json.loads(fernet.decrypt(f.read()))

    # keeps old version
    heroes_old = deepcopy(heroes)

    # update data from yagisimu
    for index in range(len(list(zip(yagis, heroes)))):
        for key in ["attack", "defense", "physical", "speed", "ultname",
                    "ultinvincible", "haname",]:
            heroes[index][key] = yagis[index][key]

    # caluculate main color of hero icon and image
    for index in range(len(heroes)):
        icon = MainColor(f"{PATH.ICONIMG}/{heroes[index]['icon_name']}.jpg")
        heroes[index]["icon_color"] = int(icon)
        image = MainColor(f"{PATH.HEROIMG}/{heroes[index]['image_name']}.jpg")
        heroes[index]["image_color"] = int(image)
        logger.info(f"{heroes[index]['name']} {icon} {image}")

    # keeps old version
    heroes_new = deepcopy(heroes)

    # dumps data to json file
    with open(PATH.HEROJSON, "wb") as f:
        bytes_str = json.dumps(heroes, ensure_ascii=False, indent=4).encode()
        f.write(fernet.encrypt(bytes_str))

    # checks diffs between the old and the new
    html = generate_diff_html(heroes_old, heroes_new)
    print(html)

    logger.info("All steps have been completed.")
