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

import json
import logging
from datetime import datetime
from re import split

from discord import Locale
from discord.ext import commands
from discord.ext.commands import Bot, Context

from bot_cps.base import CogBase
from bot_cps.translator import _T

from ..config import PATH
from .base import send_tos

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tos(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Tos")

class Tos(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Checks the Terms of Service.",
            Locale.british_english: "Checks the Terms of Service.",
            Locale.japanese: "利用規約を確認する",
            Locale.taiwan_chinese: "確認使用條款",
        })
    )
    async def tos(self, ctx: Context) -> None:
        await send_tos(ctx.interaction)

        epoch = self.agreed_epoch(ctx)
        content = await _T({
            Locale.american_english: f"You have agreed on <t:{epoch}>.",
            Locale.british_english: f"You have agreed on <t:{epoch}>.",
            Locale.japanese: f"<t:{epoch}>に同意しています",
            Locale.taiwan_chinese: f"於<t:{epoch}>同意",
        }).translate(ctx.interaction.locale)
        await ctx.send(content=content, ephemeral=True)
        return

    def agreed_epoch(self, ctx: Context) -> int:
        """Obtains epoch time to have agreed Terms of Service."""
        with open(PATH.AGREED_JSON, "r") as f:
            agreed_list = json.load(f)

        for agreed in agreed_list:
            if agreed["id"] == int(ctx.author.id):
                date_list = list(map(lambda el: int(el), split(r"/|:| ", agreed["date"])))
                return int(datetime(*date_list).timestamp())
