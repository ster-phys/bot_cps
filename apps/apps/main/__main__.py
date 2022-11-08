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

import logging
import os

from discord import Intents, Locale, app_commands
from discord.app_commands import TranslationContext as _TContext
from discord.app_commands import locale_str
from discord.ext import commands

import bot_cps
from bot_cps.translator import _T

from ..google import GoogleTranslator

logger = logging.getLogger(f"{__name__}")


google_trans= GoogleTranslator()

async def translate(_Tstring: _T, locale: Locale) -> str | None:
    """|coro|

    Translates :class:`bot_cps.translator._T` string into ``locale`` strings.

    Parameters
    ----------
    _Tstring: :class:`bot_cps.translator._T`
        Original string to be translated.
    locale: :class:`discord.Locale`
        Translation Destination.

    Returns
    -------
    :class:`str` | None
        Translated string.

    """
    if str(locale) in _Tstring.extras.keys():
        retval = _Tstring.extras.get(str(locale))
    else: # translates with google translator
        retval = await google_trans.translate(_Tstring.message, locale)

    return retval


_T.translate = translate

class Translator(app_commands.Translator):
    """
    A class that handles translations for commands, parameters,
    and choices.
    """
    async def translate(self, string: _T | locale_str , locale: Locale, context: _TContext) -> str | None:
        # translates _T only
        if type(string) is not _T:
            return None
        translated = await translate(string, locale)
        return translated


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__("/", intents=Intents.default())

    async def setup_hook(self) -> None:
        await self.tree.set_translator(Translator())

        for ext in bot_cps.EXTENSIONS:
            await self.load_extension(ext)
        await self.unload_extension("bot_cps.help")

        await self.load_extension("apps.main.help")
        await self.load_extension("apps.main.tos")

        await self.tree.sync()

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}({self.user.id})")

    def run(self, token: str) -> None:
        super().run(token, root_logger=True)

if __name__ == "__main__":
    bot = Bot()
    bot.run(os.environ["DISCORD_TOKEN"])
