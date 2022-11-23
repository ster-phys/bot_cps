"""
A library that provides Bot Launcher Managed by bot_cps

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
    "PATH",
)

import json
from os.path import abspath, dirname, exists

from bot_cps.config import CONFIG as BOT_CPS_CONFIG


class _Config(object):
    """Class in which the configuration is written."""

    @property
    def GUILD_ID(self) -> int:
        """ID of the guild to be added emoji etc. used by the bot."""
        return 834671256367530014

    class _RoleIDs(object):
        """Class in which the role IDs are written."""

        @property
        def MOD(self) -> int:
            """Moderator role ID of the support server."""
            return 939507998722768948

        @property
        def CONTRIBUTER(self) -> int:
            """Contributors to the repository role ID of the support server."""
            return 1039156170646106153

        @property
        def SUPPORTER(self) -> int:
            """Supporter role ID of the support server."""
            return 939510038274396190

        @property
        def ENJOYER(self) -> int:
            """Compass enjoyer role ID of the support server."""
            return 949894654839627808

        # temporary roles
        @property
        def CHATTING(self) -> int:
            """
            Role ID given to users when joining the chatting voice
            channel.
            """
            return 1043605852667527330

        @property
        def TEAM_BLUE(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043572987267391530

        @property
        def TEAM_RED(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573392621699142

        @property
        def TEAM_GREEN(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573308530114590

        @property
        def TEAM_ORANGE(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573436598976602

    ROLE_IDs = _RoleIDs()

    class _ChannelIDs(object):
        """Class in which the channel IDs are written."""

        @property
        def PROFILE(self) -> int:
            """ID of self-introduction channel."""
            return 939551346074452038

        @property
        def TRANSLATE(self) -> int:
            """ID of the channel for which automatic translation is done."""
            return 1020627523522019379

        @property
        def ACCESS(self) -> int:
            """ID of the channel for which the access log is output."""
            return 947759021841080371

        @property
        def CONVERSATION(self) -> int:
            """ID of the channel for which the conversation log is output."""
            return 947758753539846144

        @property
        def COMMAND(self) -> int:
            """ID of the channel to output the logging of the command."""
            return 947759158927699988

        class _Voice(object):
            """Class in which the voice channel IDs are written."""

            @property
            def CHATTING(self) -> int:
                """ID of the voice channel to chat."""
                return 939515974435090472

            @property
            def TEAM_BLUE(self) -> int:
                """ID of the voice channel to play game."""
                return 1043567908409856141

            @property
            def TEAM_RED(self) -> int:
                """ID of the voice channel to play game."""
                return 1043569142155968542

            @property
            def TEAM_GREEN(self) -> int:
                """ID of the voice channel to play game."""
                return 1043571094973595688

            @property
            def TEAM_ORANGE(self) -> int:
                """ID of the voice channel to play game."""
                return 1043571669626794034

        VOICE = _Voice()

        class _Text(object):
            """
            Class in which the text channel IDs related to the voice
            channels are written.
            """

            @property
            def CHATTING(self) -> int:
                """ID of the text channel to chat."""
                return 1043605816260956280

            @property
            def TEAM_BLUE(self) -> int:
                """ID of the text channel to play game."""
                return 1043572520906932357

            @property
            def TEAM_RED(self) -> int:
                """ID of the text channel to play game."""
                return 1043572588527497216

            @property
            def TEAM_GREEN(self) -> int:
                """ID of the text channel to play game."""
                return 1043572627823927386

            @property
            def TEAM_ORANGE(self) -> int:
                """ID of the text channel to play game."""
                return 1043572662791843941

        TEXT = _Text()

    CHANNEL_IDs = _ChannelIDs()

    @property
    def COLOR(self) -> int:
        """Main color of the bot."""
        return BOT_CPS_CONFIG.COLOR

CONFIG = _Config()


class _Path(object):
    """Class defining paths for the data used by these bot."""

    @property
    def ROOTPATH(self) -> str:
        """
        Root of the directory in which the programs that run the bots
        are stored.
        """
        return dirname(abspath(__file__))

    @property
    def TERMS_OF_SERVICE(self) -> str:
        """Path of Terms of Service file."""
        return abspath(f"{self.ROOTPATH}/../TERMS_OF_SERVICE.md")

    @property
    def AGREED_JSON(self) -> str:
        """Path to a file that records who has agreed to the Terms of Service."""
        path = abspath(f"{self.ROOTPATH}/../../../agreed.json")
        if not exists(path):
            with open(path, "w") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        return path

    @property
    def LOG_FILE(self) -> str:
        """Path to the file to log the commands."""
        return abspath(f"{self.ROOTPATH}/../../../bot_cps.log")

    @property
    def DOCS(self) -> str:
        """Path to docs directory."""
        return f"{self.ROOTPATH}/main/docs"

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

PATH = _Path()
