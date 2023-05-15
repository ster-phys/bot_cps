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
from io import BytesIO
from typing import Literal

from compass import StageData
from discord import File, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Stage(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Stage")


class Stage(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.data = StageData()

    @commands.hybrid_command(
        description = _("ステージガチャ"),
    )
    @app_commands.describe(
        number = _("１チームあたりの人数を選んでね！"),
    )
    async def stage(self, ctx: Context, number: Literal[2, 3] = 3) -> None:
        await ctx.defer()

        ret_stage = self.data.get_stage(number=number, only_available=False)

        img = ret_stage.generate_image(ctx.interaction.locale.value)

        image_bytes = BytesIO()
        img.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        await ctx.send(file=File(fp=image_bytes, filename=f"{ctx.author.id}.png"))
        return
