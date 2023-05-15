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

import json
import logging
from datetime import datetime
from re import split

from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog, send_tos
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tos(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Tos")


class Tos(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    @commands.hybrid_command(
        description = _("利用規約を確認する"),
    )
    async def tos(self, ctx: Context) -> None:
        await send_tos(ctx.interaction)

        epoch = self.agreed_epoch(ctx)
        content = _("<t:{0}>に同意しています").to(ctx.interaction.locale)
        await ctx.send(content=content.format(epoch), ephemeral=True)
        return

    def agreed_epoch(self, ctx: Context) -> int:
        """Obtains epoch time to have agreed Terms of Service."""
        with open(path.agreed_json, "r") as f:
            agreed_list = json.load(f)

        for agreed in agreed_list:
            if agreed["id"] == int(ctx.author.id):
                date_list = list(map(lambda el: int(el), split(r"/|:| ", agreed["date"])))
                return int(datetime(*date_list).timestamp())
