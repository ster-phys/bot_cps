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
    "GoogleTranslator",
)

import logging
import urllib.parse
from random import randint

import aiohttp
from discord import Locale

logger = logging.getLogger(__name__)


class GoogleTranslator(object):
    DEPLOY_IDs = (
        "AKfycbwRQkPkQ6SqAnINwwoMBaUIZQatqEEFNczIsDuJbgKFJOxspwc",
        "AKfycbxt0fGnL5f5MRoGIsyZ9JXZPs6qLUGC7FPo2vGYB8O7f__cvfdygenpofk90QGjOu0j",
        "AKfycby5o6tuGKoYPcFXnL3wZ8nkI5RCdnBRLnvs3Ku-2HVjs0lqylJtn8R_9C7YymhSzW3l",
        "AKfycbwGOEUnIjZ8ihKpGGY8eJzSFehpHliURXZcIZvqg5ptqdBdEVCYhz6LEDJug0JbyGsx",
        "AKfycbxvcBspzIRwSHjdilxhKUYg-E4qRGcmtxotns9-rxPSR4iAaLot67_yUKwoE2RkvTCm",
    )

    URL = "https://script.google.com/macros/s/{id}/exec?text={text}&lang={locale}"

    LOOKUP = {
        Locale.american_english: "en",
        Locale.british_english: "en",
        Locale.bulgarian: "bg",
        Locale.chinese: "zh-CN",
        Locale.taiwan_chinese: "zh-TW",
        Locale.croatian: "hr",
        Locale.czech: "cs",
        Locale.danish: "da",
        Locale.dutch: "nl",
        Locale.finnish: "fi",
        Locale.french: "fr",
        Locale.german: "de",
        Locale.greek: "el",
        Locale.hindi: "hi",
        Locale.hungarian: "hu",
        Locale.italian: "it",
        Locale.japanese: "ja",
        Locale.korean: "ko",
        Locale.lithuanian: "lt",
        Locale.norwegian: "no",
        Locale.polish: "pl",
        Locale.brazil_portuguese: "pt",
        Locale.romanian: "ro",
        Locale.russian: "ru",
        Locale.spain_spanish: "es",
        Locale.swedish: "es",
        Locale.thai: "th",
        Locale.turkish: "tr",
        Locale.ukrainian: "uk",
        Locale.vietnamese: "vi",
    }

    def __init__(self) -> None:
        """Constructor of this class."""
        pass

    def convert_locale(self, locale: Locale) -> str:
        """Converts discord locale to google locale.

        Parameters
        ----------
        locale: :class:`discord.Locale`
            Locale of discord.

        Returns
        -------
        :class:`str`
            Locale of google.

        """

        return self.LOOKUP.get(locale, self.LOOKUP[Locale.american_english])

    async def get_url(self, text: str, locale: str) -> str:
        """Obtains the URL of the translator."""
        id = randint(0, len(self.DEPLOY_IDs)-1)
        return self.URL.format(id=self.DEPLOY_IDs[id], text=text, locale=locale)

    async def translate(self, text: str, locale: Locale) -> str | None:
        """|coro|

        Translates strings using google's translation API.

        Parameters
        ----------
        text: :class:`str`
            Source string (in English) of the translation.
        locale: :class:`discord.Locale`
            Target locale for translation.

        Returns
        -------
        :class:`str` | None
            Translated strings.

        """
        g_locale = self.convert_locale(locale)

        if g_locale == self.LOOKUP[Locale.american_english]:
            return None

        url = await self.get_url(text=urllib.parse.quote(text), locale=g_locale)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                js = await r.json()

        logger.info("\"%s\" has translated to \"%s\".", text, js["text"])
        return js["text"]
