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
    "get_emojis",
)

from re import match
from typing import Literal

from discord import Client, Emoji
from discord.ext.commands import Bot

from .config import CONFIG
from .exception import EmojiNotFound


def get_emojis(
    client: Client | Bot,
    category: Literal["hero", "role", "attr"]
) -> list[Emoji]:
    """Gets emojis that match ``category``.

    To use this function, the appropriate ``CONFIG.GUILD_ID`` must be set.
    This means that the guild represented by the ``CONFIG.GUILD_ID`` must
    have emojis added that match the ``categories`` in the source code.

    Parameters
    ----------
    client: :class:`discord.Client` | :class:`discord.ext.commands.Bot`
        Represents a client connenction that connects to ``Discord``.
        This class is used to interact with the Discord WebSocket and API.
    category: :class:`str`
        Category of emojis to get.

    """

    categories = {
        "hero": r"\d+_.*",
        "role": r"role_.*",
        "attr": r"attr_.*",
    }

    if category not in categories:
        return []

    emojis = []
    pattern = categories[category]

    for emoji in sorted(client.get_guild(CONFIG.GUILD_ID).emojis,
                        key=lambda el: el.name):
        if match(pattern, emoji.name):
            emojis.append(emoji)

    if emojis == []:
        raise EmojiNotFound(f"{category} emojis are not found.")

    return emojis
