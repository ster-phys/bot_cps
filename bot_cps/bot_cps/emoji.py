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
#
# See the <./config.py> file for the meaning of environment variables.

import logging

import discord
from discord import ButtonStyle, Interaction, Locale, ui
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import CogBase, ViewBase
from .exception import EmojiNotFound
from .translator import _T
from .utils import get_emojis

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Emoji(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Emoji")

class Emoji(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        try:
            self.emojis = get_emojis(self.bot, "hero")
        except EmojiNotFound as e:
            self.logger.error(*e.args)
            self.logger.warning("The client cannot use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Adds #Compass icons as emojis.",
            Locale.british_english: "Adds #Compass icons as emojis.",
            Locale.japanese: "コンパスのアイコンを絵文字として追加する",
            Locale.taiwan_chinese: "將#compass內的英雄頭像追加到表情符號",
        })
    )
    async def emoji(self, ctx: Context) -> None:
        if not hasattr(self, "emojis"):
            content = await _T({
                Locale.american_english: "There are no emojis which can be added!",
                Locale.british_english: "There are no emojis which can be added!",
                Locale.japanese: "追加できる絵文字はないよ！",
                Locale.taiwan_chinese: "沒有能追加的表情符號喔！",
            }).translate(ctx.interaction.locale)
            await ctx.send(content=content, ephemeral=True)
            return

        if ctx.author.id != ctx.guild.owner_id:
            content = await _T({
                Locale.american_english: "This command is available only to the server owner!",
                Locale.british_english: "This command is available only to the server owner!",
                Locale.japanese: "鯖主のみ使用できます！",
                Locale.taiwan_chinese: "只有群組擁有者可以使用！",
            }).translate(ctx.interaction.locale)
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
            content = await _T({
                Locale.american_english: "There are no emojis which can be added!",
                Locale.british_english: "There are no emojis which can be added!",
                Locale.japanese: "追加できる絵文字はないよ！",
                Locale.taiwan_chinese: "沒有能追加的表情符號喔！",
            }).translate(ctx.interaction.locale)
            await ctx.send(content=content, ephemeral=True)
        else:
            await ctx.send(view=EmojiView(emojis), ephemeral=True)
        return

class EmojiButton(ui.Button):
    def __init__(self, emoji: discord.Emoji) -> None:
        super().__init__()
        self.style = ButtonStyle.gray
        self.emoji = emoji
        self.original_emoji: discord.Emoji = emoji

    async def callback(self, interaction: Interaction) -> None:
        try:
            self.disabled = True
            image = await self.original_emoji.read()
            reason = await _T({
                Locale.american_english: f"This emoji was added by /emoji command executed by {interaction.user}.",
                Locale.british_english: f"This emoji was added by /emoji command executed by {interaction.user}.",
                Locale.japanese: f"{interaction.user} の実行した /emoji コマンドにより追加",
                Locale.taiwan_chinese: f"依 {interaction.user} 輸入的 /emoji 指令追加",
            }).translate(interaction.locale)
            await interaction.guild.create_custom_emoji(name=self.emoji.name, image=image, reason=reason)
        except:
            pass

        await interaction.response.edit_message(view=self.view)
        return

class EmptyButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()
        self.style = ButtonStyle.gray
        self.label = "ㅤ"
        self.disabled = True

class EmojiView(ViewBase):
    def __init__(self, emojis: list[discord.Emoji]):
        super().__init__("emoji", 600, logger)
        self.index: int = 0
        self.emojis: list[list[discord.Emoji]] = []
        self.buttons: list[list[ui.Button]] = []
        self.max_index = len(emojis)//20 + int(bool(len(emojis)%20)) - 1

        for i in range(self.max_index + 1):
            partial = emojis[i*20 : (i+1)*20]
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
        self.index = 0
        self.add_items()
        await interaction.response.edit_message(view=self)
        return

    @ui.button(label="＜", style=ButtonStyle.gray, row=4)
    async def left(self, interaction: Interaction, button: ui.Button) -> None:
        self.index = self.index if self.index == 0 else self.index - 1
        self.add_items()
        await interaction.response.edit_message(view=self)
        return

    @ui.button(label="1/4", style=ButtonStyle.gray, row=4, disabled=True)
    async def number(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @ui.button(label="＞", style=ButtonStyle.gray, row=4)
    async def right(self, interaction: Interaction, button: ui.Button) -> None:
        self.index = self.index if self.index == self.max_index else self.index + 1
        self.add_items()
        await interaction.response.edit_message(view=self)
        return

    @ui.button(label="≫", style=ButtonStyle.grey, row=4)
    async def right_side(self, interaction: Interaction, button: ui.Button) -> None:
        self.index = self.max_index
        self.add_items()
        await interaction.response.edit_message(view=self)
        return
