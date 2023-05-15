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
import zoneinfo

from discord import Embed, Locale, Message
from discord.ext import commands
from discord.ext.commands import Bot


from ..cog import Cog
from ..config import config
from ..google import GoogleTranslator


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Translate(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Translate")


class Translate(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.google_trans= GoogleTranslator()
        self.icon_url = "https://cdn-icons-png.flaticon.com/512/5968/5968494.png"

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> None:
        if message.author.bot or message.channel.id != config.channels.text.translate:
            return

        text = message.content

        ja = await self.google_trans.translate(text, Locale.japanese)
        zh_TW = await self.google_trans.translate(text, Locale.taiwan_chinese)

        created_at = message.created_at
        jst = created_at.astimezone(zoneinfo.ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")
        name = f"{message.author} wrote on {jst} (JST)."

        embed = Embed(color=message.author.color)
        embed.set_author(name=name, icon_url=None if message.author.avatar is None else message.author.avatar.url)
        embed.add_field(name="Original", value=text+"\nㅤ", inline=False)
        embed.add_field(name="日本語", value=ja+"\nㅤ", inline=False)
        embed.add_field(name="台灣語", value=zh_TW, inline=False)
        embed.set_footer(text="Powered by Google Apps Script", icon_url=self.icon_url)

        await message.delete(delay=5)
        await message.channel.send(embed=embed)
        return
