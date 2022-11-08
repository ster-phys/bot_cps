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
from datetime import timedelta

from discord import Embed, Message, TextChannel
from discord.ext import commands
from discord.ext.commands import Bot

from bot_cps.base import CogBase

from ..config import CONFIG

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(MessageLogging(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("MessageLogging")

class MessageLogging(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        self.channel: TextChannel = await self.bot.fetch_channel(CONFIG.CHANNEL_IDs.CONVERSATION)
        return await super().run_once_when_ready()

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.channel.id == CONFIG.CHANNEL_IDs.CONVERSATION:
            return

        date = (message.created_at + timedelta(hours=9)).strftime("%s")
        description = f"Date: <t:{date}>\n"
        description += f"Name: `{message.author}`\n"
        description += f"Channel: {message.channel.mention} (`{message.channel.id}`)\n"
        description += f"URL: {message.jump_url}\n"
        description += f"Content: `{message.content}`\n"

        embed = Embed(color=message.author.color, description=description)
        name = f"{message.author.display_name}（{message.author.id}）"
        embed.set_author(name=name, icon_url=message.author.avatar.url)
        await self.channel.send(embed=embed)

        return
