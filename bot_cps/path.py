"""
A program that provides bot managed by bot_cps

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
    "path",
)


import os
from os.path import abspath, dirname, exists

from discord import Locale


_ROOTPATH = dirname(abspath(__file__))

_ASSET_DIR = f"{_ROOTPATH}/asset"
_ASSET_EMOJI = f"{_ASSET_DIR}/emoji"
_ASSET_GACHA = f"{_ASSET_DIR}/gacha"
_ASSET_TEAM = f"{_ASSET_DIR}/team"
_ASSET_TOS = f"{_ASSET_DIR}/tos"

_DOCS_DIR = f"{_ROOTPATH}/docs"

class Path(object):
    """Class defining paths for the data used by the programs."""

    @property
    def localedir(self) -> str:
        """Path to locale directory."""
        return f"{_ROOTPATH}/locale"

    @property
    def emoji_json(self) -> str:
        """Path to asset file of ``emoji``."""
        return f"{_ASSET_EMOJI}/emoji.json"

    @property
    def gacha_json(self) -> str:
        """Path to asset file of ``gacha``."""
        return f"{_ASSET_GACHA}/gacha.json"

    @property
    def blue_team(self) -> str:
        """Image of the blue team portal."""
        return f"{_ASSET_TEAM}/blue.png"

    @property
    def red_team(self) -> str:
        """Image of the red team portal."""
        return f"{_ASSET_TEAM}/red.png"

    @property
    def white_team(self) -> str:
        """Image of the white team portal."""
        return f"{_ASSET_TEAM}/white.png"

    def docs_detail(self, cmd: str, locale: Locale) -> str:
        """Obtains path to command detail docs."""
        if exists(f"{_DOCS_DIR}/{locale.value}/detail/{cmd}"):
            return f"{_DOCS_DIR}/{locale.value}/detail/{cmd}"
        else:
            return f"{_DOCS_DIR}/{Locale.japanese.value}/detail/{cmd}"

    def docs_title(self, cmd: str, locale: Locale) -> str:
        """Obtains path to command title docs."""
        if exists(f"{_DOCS_DIR}/{locale.value}/title/{cmd}"):
            return f"{_DOCS_DIR}/{locale.value}/title/{cmd}"
        else:
            return f"{_DOCS_DIR}/{Locale.japanese.value}/title/{cmd}"

    @property
    def detail_dir(self) -> str:
        """Directory path to command details."""
        return f"{_DOCS_DIR}/detail"

    @property
    def title_dir(self) -> str:
        """Directory path to command title."""
        return f"{_DOCS_DIR}/title"

    @property
    def agreed_json(self) -> str:
        """Path to a file that records who has agreed to the Terms of Service."""
        path = f"{os.getcwd()}/agreed.json"
        if not exists(path):
            with open(path, "w") as f:
                f.write("[]")
        return path

    @property
    def terms_of_service(self) -> str:
        """Path of Terms of Service file."""
        return f"{_ASSET_TOS}/TERMS_OF_SERVICE.md"

path = Path()

del Path
