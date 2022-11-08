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

from discord import Message
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from bot_cps.base import CogBase

from ..config import CONFIG

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(AutoRoleGrant(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("AutoRoleGrant")

class AutoRoleGrant(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        await self.get_object()
        self.auto_role_grant.start()
        return await super().run_once_when_ready()

    async def get_object(self) -> None:
        self.guild = await self.bot.fetch_guild(CONFIG.GUILD_ID)
        self.channel = await self.bot.fetch_channel(CONFIG.CHANNEL_IDs.PROFILE)
        self.role = self.guild.get_role(CONFIG.ROLE_IDs.ENJOYER)
        return

    @tasks.loop(minutes=10)
    async def auto_role_grant(self) -> None:
        members = []
        async for message in self.channel.history():
            members.append(message.author)

        async for member in self.guild.fetch_members():
            if member in members:
                await member.add_roles(self.role)
            else:
                await member.remove_roles(self.role)

        return

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> None:
        if not message.author.bot and message.channel.id == CONFIG.CHANNEL_IDs.PROFILE:
            await message.author.add_roles(self.role)
        return
