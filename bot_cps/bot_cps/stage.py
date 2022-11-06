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
# See the <compass.README.md> file for the meaning of environment variables.

import logging
from typing import Literal

from discord import File, Locale, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from compass import StageData

from .base import CogBase
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Stage(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Stage")

class Stage(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        try:
            self.data = StageData()
        except:
            self.logger.warning("The client cannot use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Stage gacha.",
            Locale.british_english: "Stage gacha.",
            Locale.japanese: "ステージガチャ",
            Locale.taiwan_chinese: "隨機場地",
        })
    )
    @app_commands.describe(
        number = _T({
            Locale.american_english: "Specifies the number of people per team.",
            Locale.british_english: "Specifies the number of people per team.",
            Locale.japanese: "１チームあたりの人数を選んでね！",
            Locale.taiwan_chinese: "請選擇各隊人數",
        })
    )
    async def stage(self, ctx: Context, number: Literal[2, 3] = 3) -> None:
        ret_stage = self.data.get_stage(number=number)
        file = ret_stage.path(str(ctx.interaction.locale))
        await ctx.send(file=File(file, filename=f"{ctx.author.id}.png"))
        return
