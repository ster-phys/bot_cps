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
from glob import glob
from os.path import basename

from discord import Embed, app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog
from .config import config
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    bot.remove_command("help")
    await bot.add_cog(Help(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Help")


cmd_list = sorted(list(map(lambda file: basename(file), glob(path.title_dir + "/*"))))


class Help(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)


    @commands.hybrid_command(
        description = _("コマンドについて調べる"),
    )
    @app_commands.describe(
        command = _("コマンドの名前（指定しない場合，コマンド一覧が表示される）"),
    )
    @app_commands.choices(command = [Choice(name=cmd, value=cmd) for cmd in cmd_list])
    async def help(self, ctx: Context, command: str = "") -> None:
        await ctx.defer()

        if command == "": # shows commands list
            title = _("コマンド一覧").to(ctx.interaction.locale)
            description = ""
            for cmd in cmd_list:
                with open(f"{path.title_dir}/{cmd}", "r") as f:
                    content = _(f.read()).to(ctx.interaction.locale)
                description += f"`/{cmd}`：{content}"

            embed = Embed(title=title, description=description, color=config.color)

        else: # shows command detail
            with open(f"{path.detail_dir}/{command}", "r") as f:
                lines = f.readlines()
                description = ""
                for line in lines:
                    description += _(line.rstrip("\n")).to(ctx.interaction.locale) + "\n"

            embed = Embed(title=f"/{command}", description=description, color=config.color)

        await ctx.send(embed=embed)
