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

import json
import logging
from collections import UserDict
from io import BytesIO
from random import choice
from typing import Literal

from compass import HeroData, Role, get_translator
from discord import (ButtonStyle, Embed, File, Interaction, Locale,
                     PartialEmoji, ui)
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.interactions import Interaction

from .base import Cog, View
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Roulette(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Roulette")


data = HeroData()


class Roulette(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.user_argument: dict[int, Argument] = {}


    @commands.hybrid_command(
        description = _("ヒーロールーレット"),
    )
    async def roulette(self, ctx: Context) -> None:
        argument = self.user_argument.get(ctx.author.id, Argument())
        await argument.send_hero(ctx.interaction)
        self.user_argument[ctx.author.id] = argument
        return

    @commands.hybrid_command(
        name = "roulette-setting",
        description = _("ヒーロールーレットの設定"),
    )
    async def roulette_setting(self, ctx: Context) -> None:
        await ctx.defer(ephemeral=True)
        argument = self.user_argument.get(ctx.author.id, Argument())
        view = RouletteView(ctx.interaction, argument)
        await ctx.send(view=view, ephemeral=True)
        self.user_argument[ctx.author.id] = argument
        return


class Argument(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.data: dict[Literal["original", "collabo"] | Role, bool]
        self.data = {role: True for role in Role}
        self.data.update({"original": True, "collabo": True,})

    def __bool__(self) -> bool:
        """Checks that this is legal parameter."""
        flag = False
        for role in Role:
            flag |= self.data[role]
        return (self.data["original"] or self.data["collabo"]) and flag

    def update(self, key: Literal["original", "collabo"] | Role) -> None:
        self.data[key] = not self.data[key]
        if not bool(self):
            self.data[key] = not self.data[key]
        return

    @property
    def args(self) -> tuple[Role]:
        """Obtains ``compass.HeroData.get_hero`` arguments."""
        retval: list[Role] = []
        for role in Role:
            if self.data[role]:
                retval.append(role)
        return tuple(retval)

    @property
    def kwargs(self) -> dict[Literal["original", "collabo"], bool]:
        """Obtains ``compass.HeroData.get_hero`` keyword arguments."""
        return {
            "original": self.data["original"],
            "collabo": self.data["collabo"],
        }

    async def send_hero(self, interaction: Interaction) -> None:
        """Generates hero ``discord.Embed`` from this and sends its."""
        await interaction.response.defer()

        hero = data.get_hero(*self.args, **self.kwargs)
        img = getattr(hero, choice(["icon", "image"]))

        image_bytes = BytesIO()
        img.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        file = File(fp=image_bytes, filename=f"{interaction.user.id}.png")

        translator = get_translator(interaction.locale.value)

        embed = Embed(color=hero.color)
        embed.set_author(name=translator(hero.name),
                         icon_url=f"attachment://{file.filename}")

        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, file=file)
        else:
            await interaction.followup.send(embed=embed, file=file)


class RoleButton(ui.Button):
    """Role ``Button`` for roulette setting."""
    def __init__(self, role: Role) -> None:
        super().__init__()

        self.view: RouletteView # just for typing

        self.style = ButtonStyle.blurple
        self.row = 0

        with open(path.emoji_json, "r") as f:
            emojis = json.load(f)["role"]

        key = f"role_{role.name.lower()}"
        self.emoji = PartialEmoji.from_str(emojis[key])

        self.key = role

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.update(self.key)
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)


class OriginalButton(ui.Button):
    """Original ``Button`` for roulette setting."""
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: RouletteView # just for typing

        self.label = _("オリジナル").to(locale)
        self.style = ButtonStyle.blurple
        self.row = 1

        self.key = "original"

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.update(self.key)
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)


class CollaboButton(ui.Button):
    """Collabo ``Button`` for roulette setting."""
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: RouletteView # just for typing

        self.label = _("コラボ").to(locale)
        self.style = ButtonStyle.blurple
        self.row = 1

        self.key = "collabo"

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.update(self.key)
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)


class ResetButton(ui.Button):
    """Reset ``Button`` for roulette setting."""
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: RouletteView # just for typing

        self.label = _("初期化").to(locale)
        self.style = ButtonStyle.red
        self.row = 2

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.__init__()
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)


class ExecuteButton(ui.Button):
    """Execute ``Button`` for roulette setting."""
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: RouletteView # just for typing

        self.label = _("実行").to(locale)
        self.style = ButtonStyle.green
        self.row = 2

    async def callback(self, interaction: Interaction) -> None:
        await self.view.argument.send_hero(interaction)


class RouletteView(View):
    def __init__(self, interaction: Interaction, argument: Argument):
        super().__init__("roulette-setting", 600, logger)
        self.locale: Locale = interaction.locale
        self.argument: Argument = argument

        for role in Role:
            self.add_item(RoleButton(role))

        self.add_item(OriginalButton(self.locale))
        self.add_item(CollaboButton(self.locale))
        self.add_item(ResetButton(self.locale))
        self.add_item(ExecuteButton(self.locale))

        self.update_style()

    def update_style(self) -> None:
        """Updates all buttons style."""

        for child in self.children:
            if hasattr(child, "key"):
                if self.argument[child.key]:
                    child.style = ButtonStyle.blurple
                else:
                    child.style = ButtonStyle.gray
