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
    "Translator",
    "locale_str",
)


import gettext
from glob import glob
from os.path import basename
from typing import Callable

from discord import Locale, app_commands
from discord.app_commands.translator import TranslationContextTypes

from .path import path


def _get_translator(locale: Locale = Locale.japanese) -> Callable[[str], str]:
    """Defines ``_`` to translate.

    Parameters
    ----------
    locale: :class:`discord.Locale`
        Target language location for translation.

    Returns
    -------
    Callable[[:class:`str`], :class:`str`]
        Obtains translator that translates to specific language.

    Usage
    -----

    ```python
    _ = _get_translator()
    print(_("Target string to be translated."))
    ```

    """

    files = glob(path.localedir + "/*.pot")
    domains = list(map(lambda file: basename(file)[:-4], files))

    fallbacks = [
        gettext.translation(
            domain=domain,
            localedir=path.localedir,
            languages=(locale.value,),
            fallback=True,
        )
        for domain in domains
    ]

    translation = fallbacks[0]
    for fallback in fallbacks[1:]:
        translation.add_fallback(fallback)

    return translation.gettext


class locale_str(app_commands.locale_str):

    def to(self, locale: Locale) -> str:
        """Translates immediately to ``locale`` string."""
        _ = _get_translator(locale)
        return _(self.message)


# override locale_str class
app_commands.translator.locale_str = locale_str


class Translator(app_commands.Translator):
    """
    A class that handles translations for commands, parameters,
    and choices.
    """

    async def translate(self, string: locale_str, locale: Locale,
                        context: TranslationContextTypes) -> str | None:
        _ = _get_translator(locale)
        return _(string.message)
