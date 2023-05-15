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
    "config",
)


class Config(object):
    class Guilds(object):
        @property
        def bot_cps(self) -> int:
            """Guild ID of the support server."""
            return 834671256367530014

    guilds = Guilds()


    class Roles(object):
        @property
        def mod(self) -> int:
            """Moderator role ID of the support server."""
            return 939507998722768948

        @property
        def contributer(self) -> int:
            """Contributors to the repository role ID of the support server."""
            return 1039156170646106153

        @property
        def supporter(self) -> int:
            """Supporter role ID of the support server."""
            return 939510038274396190

        @property
        def enjoyer(self) -> int:
            """Compass enjoyer role ID of the support server."""
            return 949894654839627808

        # temporary roles
        @property
        def chatting(self) -> int:
            """
            Role ID given to users when joining the chatting voice
            channel.
            """
            return 1043605852667527330

        @property
        def team_blue(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043572987267391530

        @property
        def team_red(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573392621699142

        @property
        def team_green(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573308530114590

        @property
        def team_orange(self) -> int:
            """Role ID given to users when joining a team channel."""
            return 1043573436598976602

    roles = Roles()


    class Channels(object):
        class Text(object):
            @property
            def profile(self) -> int:
                """ID of self-introduction channel."""
                return 939551346074452038

            @property
            def translate(self) -> int:
                """ID of the channel for which automatic translation is done."""
                return 1020627523522019379

            @property
            def access(self) -> int:
                """ID of the channel for which the access log is output."""
                return 947759021841080371

            @property
            def conversation(self) -> int:
                """ID of the channel for which the conversation log is output."""
                return 947758753539846144

            @property
            def command(self) -> int:
                """ID of the channel to output the logging of the command."""
                return 947759158927699988

            @property
            def chatting(self) -> int:
                """ID of the text channel to chat."""
                return 1043605816260956280

            @property
            def team_blue(self) -> int:
                """ID of the text channel to play game."""
                return 1043572520906932357

            @property
            def team_red(self) -> int:
                """ID of the text channel to play game."""
                return 1043572588527497216

            @property
            def team_green(self) -> int:
                """ID of the text channel to play game."""
                return 1043572627823927386

            @property
            def team_orange(self) -> int:
                """ID of the text channel to play game."""
                return 1043572662791843941

        text = Text()


        class Voice(object):
            """Class in which the voice channel IDs are written."""

            @property
            def chatting(self) -> int:
                """ID of the voice channel to chat."""
                return 939515974435090472

            @property
            def team_blue(self) -> int:
                """ID of the voice channel to play game."""
                return 1043567908409856141

            @property
            def team_red(self) -> int:
                """ID of the voice channel to play game."""
                return 1043569142155968542

            @property
            def team_green(self) -> int:
                """ID of the voice channel to play game."""
                return 1043571094973595688

            @property
            def team_orange(self) -> int:
                """ID of the voice channel to play game."""
                return 1043571669626794034

        voice = Voice()

    channels = Channels()


config = Config()
