"""
A library that provides Cogs for Compass Bot

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
    "CONFIG",
    "ENVKEY",
    "PATH",
)

import os


class _EnvKey(object):
    """
    Class that records the environment variables used
    by ``bot_cps`` library.
    """

    _PREFIX = "BOT_CPS_" # prefix of environment variable

    @property
    def GUILD_ID(self) -> str:
        """
        Name of environment variable in which the guild ID
        is stored. The guild must have emojis used by the bot.
        """
        return f"{self._PREFIX}GUILD_ID"

ENVKEY = _EnvKey()


class _Config(object):
    """Class in which the configuration is written."""

    @property
    def GUILD_ID(self) -> int | None:
        """ID of the guild to be added emoji etc. used by the bot."""
        try:
            return int(os.environ[ENVKEY.GUILD_ID])
        except KeyError:
            None

    @property
    def COLOR(self) -> int:
        """Main color of the bot."""
        return 0xB33E5C


CONFIG = _Config()


class _Path(object):
    """Class defining paths for the data used by this cogs."""

    ROOTPATH = os.path.dirname(os.path.abspath(__file__))
    ASSETS = f"{ROOTPATH}/assets"

    # docs for help command
    DOCS = f"{ROOTPATH}/docs"

    @property
    def DOCS_DETAIL(self) -> str:
        """
        Path to the directory where the file describing the
        details of the command is located.
        """
        return f"{self.DOCS}/detail"

    @property
    def DOCS_TITLE(self) -> str:
        """
        Path to a directory where the file describing the
        brief description of the command is located.
        """
        return f"{self.DOCS}/title"

    # for team command
    TEAM = f"{ASSETS}/team"

    @property
    def TEAM_BLUE(self) -> str:
        """Path to the blue portal image."""
        return f"{self.TEAM}/blue.png"

    @property
    def TEAM_RED(self) -> str:
        """Path to the red portal image."""
        return f"{self.TEAM}/red.png"

    @property
    def TEAM_WHITE(self) -> str:
        """Path to the white portal image."""
        return f"{self.TEAM}/white.png"

    # for gacha command
    GACHA = f"{ASSETS}/gacha"

    @property
    def GACHA_JSON(self) -> str:
        """Gacha configuration file."""
        return f"{self.GACHA}/gacha.json"

PATH = _Path()
