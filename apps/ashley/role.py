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

from discord import Member, Message, Role, VoiceState
from discord.ext import commands, tasks
from discord.ext.commands import Bot

from ..cog import Cog
from ..config import config


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(EnjoyerRoleGrant(bot))
    await bot.add_cog(VoiceRoleGrant(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("EnjoyerRoleGrant")
    await bot.remove_cog("VoiceRoleGrant")


class EnjoyerRoleGrant(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        await self.get_object()
        self.auto_role_grant.start()
        return await super().run_once_when_ready()

    async def get_object(self) -> None:
        self.guild = await self.bot.fetch_guild(config.guilds.bot_cps)
        self.channel = await self.bot.fetch_channel(config.channels.text.profile)
        self.role = self.guild.get_role(config.roles.enjoyer)
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
        if not message.author.bot and message.channel.id == config.channels.text.profile:
            await message.author.add_roles(self.role)
        return


class VoiceRoleGrant(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        self.guild = await self.bot.fetch_guild(config.guilds.bot_cps)
        self.corr: dict[int, Role] = {
            config.channels.voice.chatting: self.guild.get_role(config.roles.chatting),
            config.channels.voice.team_blue: self.guild.get_role(config.roles.team_blue),
            config.channels.voice.team_red: self.guild.get_role(config.roles.team_red),
            config.channels.voice.team_green: self.guild.get_role(config.roles.team_green),
            config.channels.voice.team_orange: self.guild.get_role(config.roles.team_orange),
        }
        return await super().run_once_when_ready()

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):

        if before.channel is not None and before.channel.id in self.corr:
            await member.remove_roles(self.corr[before.channel.id])

        if after.channel is not None and after.channel.id in self.corr:
            await member.add_roles(self.corr[after.channel.id])

        return
