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

# To use the Cog defined in this file, the environment variables
# listed below must be set.
#
# - BOT_CPS_GUILD_ID
# - BOT_CPS_TOKEN
#
# See the <./config.py> file for the meaning of environment variables.

import logging
from collections import UserDict
from os.path import basename
from random import choice

from discord import ButtonStyle, Embed, Emoji, File, Interaction, Locale, ui
from discord.ext import commands
from discord.ext.commands import Bot, Context

from compass import HeroData, Role

from .base import CogBase, ViewBase
from .translator import _T
from .utils import get_emojis

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Roulette(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Roulette")


data: HeroData      # use global, initialise at Roulette.run_once_when_ready
emojis: list[Emoji] # use global, initialise at Roulette.run_once_when_ready

class Roulette(CogBase):
    def __init__(self, bot) -> None:
        super().__init__(bot, logger)
        self.parameters: dict[int, RouletteParameter] = {}

    async def run_once_when_ready(self) -> None:
        try:
            global data, emojis # This is a global variable.
            data = HeroData()
            emojis = sorted(get_emojis(self.bot, "role"), key=lambda el: el.name)
        except:
            self.logger.warning("The client may not be able to use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Hero Roulette.",
            Locale.british_english: "Hero Roulette.",
            Locale.japanese: "ヒーロールーレット",
            Locale.taiwan_chinese: "英雄轉盤",
        })
    )
    async def roulette(self, ctx: Context) -> None:
        roulette_param = self.parameters.get(ctx.author.id, RouletteParameter())
        await roulette_param.send_hero(ctx.interaction)
        self.parameters[ctx.author.id] = roulette_param
        return

    @commands.hybrid_command(
        name = "roulette-setting",
        description = _T({
            Locale.american_english: "Sets parameters for roulette cmd.",
            Locale.british_english: "Sets parameters for roulette cmd.",
            Locale.japanese: "ヒーロールーレットの設定",
            Locale.taiwan_chinese: "更改英雄轉盤設定",
        })
    )
    async def roulette_setting(self, ctx: Context) -> None:
        roulette_param = self.parameters.get(ctx.author.id, RouletteParameter())

        async with RouletteParameterView(ctx.interaction, roulette_param) as view:
            await ctx.send(view=view, ephemeral=True)

        self.parameters[ctx.author.id] = roulette_param


class RouletteParameter(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.data: dict[str, bool]
        self.data.update({
            "original": True, "collabo": True
        })
        for role in Role:
            self.data.update({role.name.lower(): True})

    def __bool__(self) -> bool:
        """Checks the legal parameter."""
        flag = False
        for role in Role:
            flag |= self.data[role.name.lower()]
        return (self.data["original"] or self.data["collabo"]) and flag

    def update(self, key: str) -> None:
        self.data[key] = not self.data[key]
        if not bool(self):
            self.data[key] = not self.data[key]
        return

    @property
    def args(self) -> tuple[Role]:
        """Obtains ``HeroData.get_hero()`` arguments."""
        retval = []
        for role in Role:
            if self.data[role.name.lower()]:
                retval.append(role)
        return tuple(retval)

    @property
    def kwargs(self) -> dict[str, bool]:
        """Obtains ``HeroData.get_hero()`` keyword arguments."""
        return {
            "original": self.data["original"],
            "collabo": self.data["collabo"],
        }

    async def send_hero(self, interaction: Interaction) -> None:
        """Generates hero ``Embed`` from ``parameters`` and sends its."""
        global data # This is a global variable.
        hero = data.get_hero(*self.args, **self.kwargs)

        image_type = choice(["icon", "image"])

        filepath = getattr(hero, f"{image_type}_path")
        filename = basename(filepath)
        file = File(filepath, filename=filename)

        embed = Embed(color=getattr(hero, f"{image_type}_color"))
        embed.set_author(name=hero.name(str(interaction.locale)),
                         icon_url=f"attachment://{filename}")

        await interaction.response.send_message(embed=embed, file=file)


class RouletteParameterEmojiButton(ui.Button):
    """``Button`` for roulette setting."""
    def __init__(self, emoji: Emoji) -> None:
        super().__init__()
        self.view: RouletteParameterView # just for typing

        self.style = ButtonStyle.blurple
        self.row = 0
        self.emoji = emoji
        self.role = Role(emoji.name[5:])
        self.key = self.role.name.lower()

    async def callback(self, interaction: Interaction) -> None:
        self.view.roulette_parameter.update(self.key)
        self.view.update_style()
        await interaction.response.edit_message(view=self.view)

class RouletteParameterButton(ui.Button):
    """``Button`` for roulette setting."""
    def __init__(self, key: str, _Tlabel: _T) -> None:
        super().__init__()
        self.view: RouletteParameterView # just for typing

        self.style = ButtonStyle.blurple
        self.row = 1
        self.key = key
        self._Tlabel = _Tlabel

    async def callback(self, interaction: Interaction) -> None:
        self.view.roulette_parameter.update(self.key)
        self.view.update_style()
        await interaction.response.edit_message(view=self.view)

class RouletteParameterResetButton(ui.Button):
    """Reset ``Button`` for roulette setting."""
    def __init__(self) -> None:
        super().__init__()
        self.view: RouletteParameterView # just for typing

        self._Tlabel = _T({
            Locale.american_english: "Reset",
            Locale.british_english: "Reset",
            Locale.japanese: "初期化",
            Locale.taiwan_chinese: "初始化",
        })
        self.style = ButtonStyle.red
        self.row = 2

    async def callback(self, interaction: Interaction) -> None:
        self.view.roulette_parameter.__init__()
        self.view.update_style()
        await interaction.response.edit_message(view=self.view)

class RouletteParameterExecuteButton(ui.Button):
    """Execute ``Button`` for roulette setting."""
    def __init__(self) -> None:
        super().__init__()
        self.view: RouletteParameterView # just for typing

        self._Tlabel = _T({
            Locale.american_english: "Execute",
            Locale.british_english: "Execute",
            Locale.japanese: "実行",
            Locale.taiwan_chinese: "執行",
        })
        self.style = ButtonStyle.green
        self.row = 2

    async def callback(self, interaction: Interaction) -> None:
        await self.view.roulette_parameter.send_hero(interaction)


class RouletteParameterView(ViewBase):
    def __init__(self, interaction: Interaction, parameter: RouletteParameter):
        super().__init__("roulette-setting", 600, logger)
        self.locale: Locale = interaction.locale
        self.roulette_parameter: RouletteParameter = parameter

        global emojis # This is a global variable.
        for emoji in emojis:
            self.add_item(RouletteParameterEmojiButton(emoji))

        self.add_item(RouletteParameterButton("original",
            _Tlabel = _T({
                Locale.american_english: "Original",
                Locale.british_english: "Original",
                Locale.japanese: "オリジナル",
                Locale.taiwan_chinese: "常駐",
            })
        ))
        self.add_item(RouletteParameterButton("collabo",
            _Tlabel = _T({
                Locale.american_english: "Collabo",
                Locale.british_english: "Collabo",
                Locale.japanese: "コラボ",
                Locale.taiwan_chinese: "合作",
            })
        ))
        self.add_item(RouletteParameterResetButton())
        self.add_item(RouletteParameterExecuteButton())

        self.update_style()

    def update_style(self) -> None:
        """Updates all buttons style."""
        for child in self.children:
            if hasattr(child, "key"):
                if self.roulette_parameter[child.key]:
                    child.style = ButtonStyle.blurple
                else:
                    child.style = ButtonStyle.gray
