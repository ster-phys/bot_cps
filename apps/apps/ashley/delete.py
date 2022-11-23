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

import logging

import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import Bot, Context

from bot_cps.base import CogBase

from ..config import CONFIG

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(DeleteMessage(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("DeleteMessage")

class DeleteMessage(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.channels = [
            CONFIG.CHANNEL_IDs.TEXT.CHATTING,
            CONFIG.CHANNEL_IDs.TEXT.TEAM_BLUE,
            CONFIG.CHANNEL_IDs.TEXT.TEAM_RED,
            CONFIG.CHANNEL_IDs.TEXT.TEAM_GREEN,
            CONFIG.CHANNEL_IDs.TEXT.TEAM_ORANGE,
        ]

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> None:
        if message.channel.id not in self.channels:
            return

        # deletes after one hour
        try:
            await message.delete(delay=3600)
        except discord.NotFound:
            pass

        return

    @commands.hybrid_command()
    async def purge(self, ctx: Context):
        """Deletes all posts in the channel (for @Mod)."""
        if CONFIG.ROLE_IDs.MOD not in list(map(lambda role: role.id, ctx.author.roles)):
            await ctx.send("You are not allowed to use this command.", ephemeral=True)
            return

        if ctx.channel.id not in self.channels:
            await ctx.send("Not available in this channel.", ephemeral=True)
            return

        await ctx.defer()
        await ctx.channel.purge(limit=None, reason=f"/purge command executed by {ctx.author}.")
        await ctx.channel.send("Wow! They're so clean and shiny!", delete_after=10)
        return
