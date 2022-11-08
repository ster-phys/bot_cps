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
from datetime import datetime, timezone

from discord import Embed, Member, RawMemberRemoveEvent, TextChannel
from discord.ext import commands
from discord.ext.commands import Bot

from bot_cps.base import CogBase

from ..config import CONFIG

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(AccessLogging(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("AccessLogging")

class AccessLogging(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        self.channel: TextChannel = await self.bot.fetch_channel(CONFIG.CHANNEL_IDs.ACCESS)
        return await super().run_once_when_ready()

    def now(self) -> int:
        dt = datetime.now(tz=timezone.utc)
        return int(dt.timestamp())

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: Member) -> None:
        name = f"{member.display_name} ({member.id})"
        description = f"{member.mention} joined at <t:{self.now()}>"

        embed = Embed(color=0xf3981d, description=description)
        embed.set_author(name=name, icon_url=None if member.avatar is None else member.avatar.url)
        await self.channel.send(embed=embed)
        return

    @commands.Cog.listener("on_raw_member_remove")
    async def on_raw_member_remove(self, payload: RawMemberRemoveEvent) -> None:
        name = f"{payload.user.display_name} ({payload.user.id})"
        description = f"{payload.user.mention} left at <t:{self.now()}>"

        embed = Embed(color=0x414fa3, description=description)
        embed.set_author(name=name, icon_url=None if payload.user.avatar is None else payload.user.avatar.url)
        await self.channel.send(embed=embed)
        return
