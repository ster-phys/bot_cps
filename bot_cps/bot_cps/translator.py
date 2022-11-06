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
    "_T",
    "Translator",
)

from discord import Locale, app_commands
from discord.app_commands import TranslationContext as _TContext
from discord.app_commands import locale_str


class _T(locale_str):
    """Class to use when displaying a different string for each locale."""
    def __init__(self, localed_str: dict[Locale, str], /) -> None:
        """Constructs an object of this class.

        Parameters
        ----------
        localed_str: Dict[:class:`discord.Locale`, :class:`str`]
            Text to be displayed in that locale. This must always
            include text written in ``en-US``.

        """
        kwargs: dict[str, str] = {}

        for k, v in localed_str.items():
            kwargs[str(k)] = v

        message = kwargs[str(Locale.american_english)]

        # If only en-US is available, substitute en-GB.
        if str(Locale.british_english) not in kwargs.keys():
            kwargs[str(Locale.british_english)] = kwargs[str(Locale.american_english)]

        super().__init__(message, **kwargs)

        # just for typing
        self.extras: dict[str, str]

    async def translate(self, locale: Locale) -> str:
        """|coro|

        Obtains the translated string from the string to be translated.

        locale: :class:`discord.Locale`
            Target locale for translation. If the ``locale`` key dose not exist,
            ``message`` (in ``en-US``) is used.

        """
        return self.extras.get(str(locale), self.message)


class Translator(app_commands.Translator):
    """
    A class that handles translations for commands, parameters,
    and choices.
    """
    async def translate(self, string: _T, locale: Locale, context: _TContext) -> str | None:
        if str(locale) in string.extras.keys():
            return string.extras[str(locale)]
        return None
