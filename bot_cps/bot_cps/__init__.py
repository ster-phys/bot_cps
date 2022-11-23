"""
Cogs for Compass Bot
~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2021-present ster
:license: GPL-3.0, see LICENSE for more details.

"""

__title__ = "bot_cps"
__author__ = "ster"
__license__ = "GPL-3.0"
__copyright__ = "Copyright 2021-present ster"
__version__ = "1.0.1"

__all__ = (
    "EXTENSIONS",
    "Bot",
    "Translator",
)

EXTENSIONS = (
    f"{__title__}.card",
    f"{__title__}.deck",
    f"{__title__}.emoji",
    f"{__title__}.gacha",
    f"{__title__}.help",
    f"{__title__}.listener",
    f"{__title__}.ping",
    f"{__title__}.roulette",
    f"{__title__}.stage",
    f"{__title__}.team",
)

import logging

from discord.ext import commands

from .translator import Translator

logger = logging.getLogger(f"{__title__}.{__name__}")

class Bot(commands.Bot):
    """
    To use the ``Cog`` provided by this library,
    the ``Translator`` must be set as follows.
    """
    async def setup_hook(self) -> None:
        # sets translator
        await self.tree.set_translator(Translator())
        return await super().setup_hook()

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}({self.user.id})")

    def run(self, token: str) -> None:
        super().run(token, root_logger=True)
