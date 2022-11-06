"""
A library that provides Cogs for Compass Bot

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
from glob import glob
from os.path import basename, exists

from discord import Embed, Locale, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import CogBase
from .config import CONFIG, PATH
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Help(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Help")

CMD_LIST: list[str] = sorted(list(map(lambda path: basename(path), glob(f"{PATH.DOCS_TITLE}/en-US/*"))))

class Help(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.titles: dict[str, _T] = {}
        self.details: dict[str, _T] = {}
        self.generate_docs()

    def generate_docs(self) -> None:
        """Generates docs dict."""
        for cmd in CMD_LIST:
            title_arg, detail_arg = {}, {}
            for locale in Locale:
                if exists(f"{PATH.DOCS_TITLE}/{locale}/{cmd}"):
                    with open(f"{PATH.DOCS_TITLE}/{locale}/{cmd}", "r") as f:
                        title_arg.update({locale: f.read()})
                if exists(f"{PATH.DOCS_DETAIL}/{locale}/{cmd}"):
                    with open(f"{PATH.DOCS_DETAIL}/{locale}/{cmd}", "r") as f:
                        detail_arg.update({locale: f.read()})
            self.titles[cmd] = _T(title_arg)
            self.details[cmd] = _T(detail_arg)

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Checks for commands.",
            Locale.british_english: "Checks for commands.",
            Locale.japanese: "コマンドについて調べる",
            Locale.taiwan_chinese: "查詢bot的指令",
        })
    )
    @app_commands.describe(
        command = _T({
            Locale.american_english: "the name of the command (displays command list if not specified)",
            Locale.british_english: "the name of the command (displays command list if not specified)",
            Locale.japanese: "コマンドの名前（指定しない場合，コマンド一覧が表示される）",
            Locale.taiwan_chinese: "指令名稱（沒有指定的狀況將會顯示指令一覽）",
        })
    )
    @app_commands.choices(command = [Choice(name=cmd, value=cmd) for cmd in CMD_LIST])
    async def help(self, ctx: Context, command: str = "") -> None:
        if command == "": # shows commands list
            title = await _T({
                Locale.american_english: "Commands List",
                Locale.british_english: "Commands List",
                Locale.japanese: "コマンド一覧",
                Locale.taiwan_chinese: "指令一覽",
            }).translate(ctx.interaction.locale)
            description = ""
            for cmd in CMD_LIST:
                description += f"`/{cmd}`：{await self.titles[cmd].translate(ctx.interaction.locale)}"

            embed = Embed(title=title,
                          description=description,
                          color=CONFIG.COLOR)

        else: # shows command detail
            embed = Embed(title=f"/{command}",
                          description=await self.details[command].translate(ctx.interaction.locale),
                          color=CONFIG.COLOR)

        await ctx.send(embed=embed)
        return
