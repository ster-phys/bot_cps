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

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from .base import Cog


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Listener(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Listener")


class Listener(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.server: int = 0

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        if not self.presence.is_running():
            await self.presence.start()
        return

    @tasks.loop(seconds=1)
    async def presence(self) -> None:
        server = len(self.bot.guilds)
        if self.server != server:
            self.server = server
            activity = discord.Activity(name=f"{server:,} servers", type=discord.ActivityType.playing)
            await self.bot.change_presence(activity=activity)
            self.logger.info(f"Activity changed to {server:,} servers.")
        return

    @presence.before_loop
    async def before_presence(self) -> None:
        await self.bot.wait_until_ready()
        return
