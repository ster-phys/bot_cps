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
from io import BytesIO

import discord
from compass import HeroData
from discord import ButtonStyle, Interaction, PartialEmoji, ui
from discord.ext import commands
from discord.ext.commands import Bot, Context
from PIL.PngImagePlugin import PngImageFile

from .base import Cog, View
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Emoji(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Emoji")


class Emoji(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        with open(path.emoji_json, "r") as f:
            data = json.load(f)["hero"]

        self.emojis = [PartialEmoji.from_str(data[key]) for key in data]

    @commands.hybrid_command(
        description = _("コンパスのアイコンを絵文字として追加する"),
    )
    async def emoji(self, ctx: Context) -> None:
        await ctx.defer()

        if not hasattr(self, "emojis"):
            content = _("追加できる絵文字はないよ！").to(ctx.interaction.locale)
            await ctx.send(content=content, ephemeral=True)
            return

        if ctx.author.id != ctx.guild.owner_id:
            content = _("鯖主のみ使用できます！").to(ctx.interaction.locale)
            await ctx.send(content=content, ephemeral=True)
            return

        emojis = []
        guild_emojis = ctx.guild.emojis

        for emoji in self.emojis:
            flag = False
            for g_emoji in guild_emojis:
                if emoji.name == g_emoji.name:
                    flag = True
            if not flag:
                emojis.append(emoji)

        if len(emojis) == 0:
            content = _("追加できる絵文字はないよ！").to(ctx.interaction.locale)
            await ctx.send(content=content, ephemeral=True)
        else:
            await ctx.send(view=EmojiView(emojis), ephemeral=True)
        return

class EmojiButton(ui.Button):
    def __init__(self, emoji: discord.PartialEmoji) -> None:
        super().__init__()
        self.style = ButtonStyle.gray
        self.emoji = emoji

    def get_icon(self) -> PngImageFile:
        """Obtains icon image from partial emoji."""

        hd = HeroData()
        for hero in hd:
            if self.emoji.name ==str(hero):
                return hero.icon

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        try:
            self.disabled = True

            img = self.get_icon()

            image_bytes = BytesIO()
            img.save(image_bytes, "PNG", quality=100, optimize=True)
            image_bytes.seek(0)

            image = image_bytes.read()

            reason = _("{0} の実行した /emoji コマンドにより追加").to(interaction.locale)
            reason = reason.format(interaction.user)
            await interaction.guild.create_custom_emoji(name=self.emoji.name, image=image,
                                                        reason=reason)
        except:
            pass

        await interaction.followup.edit_message(interaction.message.id, view=self.view)
        return

class EmptyButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()
        self.style = ButtonStyle.gray
        self.label = "ㅤ"
        self.disabled = True

class EmojiView(View):
    def __init__(self, emojis: list[discord.Emoji]):
        super().__init__("emoji", 600, logger)
        self.index: int = 0
        self.emojis: list[list[discord.Emoji]] = []
        self.buttons: list[list[ui.Button]] = []
        self.max_index = len(emojis) //20 +int(bool(len(emojis)%20)) -1

        for i in range(self.max_index +1):
            partial = emojis[i *20 : (i +1) *20]
            self.emojis.append(partial)
            self.buttons.append([EmojiButton(emoji) for emoji in partial])

        self.add_items()

    def add_items(self) -> None:
        self.clear_items()

        for button in self.buttons[self.index]:
            self.add_item(button)
        for _ in range(20 - len(self.buttons[self.index])):
            self.add_item(EmptyButton())

        self.add_item(self.left_side)  # -5
        self.add_item(self.left)       # -4
        self.add_item(self.number)     # -3
        self.add_item(self.right)      # -2
        self.add_item(self.right_side) # -1

        self.children[-5].disabled = True if self.index == 0 else False
        self.children[-4].disabled = True if self.index == 0 else False
        self.children[-3].label = f"{self.index+1}/{self.max_index+1}"
        self.children[-2].disabled = True if self.index == self.max_index else False
        self.children[-1].disabled = True if self.index == self.max_index else False

    @ui.button(label="≪", style=ButtonStyle.gray, row=4)
    async def left_side(self, interaction: Interaction, button: ui.Button) -> None:
        await interaction.response.defer()
        self.index = 0
        self.add_items()
        await interaction.followup.edit_message(interaction.message.id, view=self)
        return

    @ui.button(label="＜", style=ButtonStyle.gray, row=4)
    async def left(self, interaction: Interaction, button: ui.Button) -> None:
        await interaction.response.defer()
        self.index = self.index if self.index == 0 else self.index - 1
        self.add_items()
        await interaction.followup.edit_message(interaction.message.id, view=self)
        return

    @ui.button(label="1/4", style=ButtonStyle.gray, row=4, disabled=True)
    async def number(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @ui.button(label="＞", style=ButtonStyle.gray, row=4)
    async def right(self, interaction: Interaction, button: ui.Button) -> None:
        await interaction.response.defer()
        self.index = self.index if self.index == self.max_index else self.index + 1
        self.add_items()
        await interaction.followup.edit_message(interaction.message.id, view=self)
        return

    @ui.button(label="≫", style=ButtonStyle.grey, row=4)
    async def right_side(self, interaction: Interaction, button: ui.Button) -> None:
        await interaction.response.defer()
        self.index = self.max_index
        self.add_items()
        await interaction.followup.edit_message(interaction.message.id, view=self)
        return
