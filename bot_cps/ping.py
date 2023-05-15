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

import logging

from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Ping(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Ping")


class Ping(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    @commands.hybrid_command(
        description=_("ping値を返す"),
    )
    async def ping(self, ctx: Context) -> None:
        await ctx.defer()
        latency = round(ctx.bot.latency * 1000)
        await ctx.send(f"Pong!! (`{latency}ms`)")
        return
