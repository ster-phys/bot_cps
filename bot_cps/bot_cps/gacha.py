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

# To use the Cog defined in this file, the environment variables
# listed below must be set.
#
# - BOT_CPS_TOKEN
#
# See the <./config.py> file for the meaning of environment variables.


import json
import logging
from os import remove
from os.path import basename
from random import choices, shuffle

from discord import File, Locale, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from compass import CardData

from .base import CogBase
from .config import PATH
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Gacha(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Gacha")


# prepares choices for name argument
with open(PATH.GACHA_JSON, "r") as f:
    GACHA_DATA = json.load(f)

GACHA_LIST = [app_commands.Choice(name=data["name"], value=idx)
              for idx, data in enumerate(GACHA_DATA)]


class Gacha(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        try:
            self.data = CardData()
        except:
            self.logger.warning("The client cannot use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Gacha Simulator.",
            Locale.british_english: "Gacha Simulator.",
            Locale.japanese: "ガチャシミュレーター",
            Locale.taiwan_chinese: "抽卡模擬器",
        })
    )
    @app_commands.describe(
        name = _T({
            Locale.american_english: "Specifies the gacha name to simulate.",
            Locale.british_english: "Specifies the gacha name to simulate.",
            Locale.japanese: "シミュレートするガチャの名前を指定してね！",
            Locale.taiwan_chinese: "請決定模擬的卡池！",
        })
    )
    @app_commands.choices(name=GACHA_LIST)
    async def gacha(self, ctx: Context, name: int) -> None:
        data = GACHA_DATA[name]
        cards = CardData([])

        rarities = choices([*data["weight"]], [*data["weight"].values()], k=data["k"])

        for rarity in [*data["weight"]]:
            population = CardData([])
            weights = []
            k = sum(el==rarity for el in rarities)
            for condition in data[rarity]:
                tmp = self.data.get_cards(*condition["args"], **condition["kwargs"])
                population.extend(tmp)
                weights.extend([condition["weight"]]*len(tmp))
            cards.extend(choices(population, weights, k=k))

        shuffle(cards)

        filepath = cards.generate_large_image()
        filename = basename(filepath)

        await ctx.send(file=File(filepath, filename=filename))

        remove(filepath)
