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
# - BOT_CPS_TOKEN
#
# See the <compass.README.md> file for the meaning of environment variables.

import logging
from os import remove
from os.path import basename, exists
from tempfile import mkstemp
from typing import Literal

from discord import (ButtonStyle, Embed, File, Interaction, Locale, Message,
                     app_commands, ui)
from discord.ext import commands
from discord.ext.commands import Bot, Context

import compass
from compass import CardData

from .base import CogBase, ViewBase
from .config import CONFIG
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Card(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Card")

class Card(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

    async def run_once_when_ready(self) -> None:
        try:
            self.data = CardData()
        except:
            self.logger.warning("The client cannot use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Searches for card details or deck status.",
            Locale.british_english: "Searches for card details or deck status.",
            Locale.japanese: "カードの詳細またはデッキのステータスを調べる",
            Locale.taiwan_chinese: "查詢卡片的能力與體質",
        })
    )
    @app_commands.describe(
        cards = _T({
            Locale.american_english: "Enters card names separated by spaces (max. 4)",
            Locale.british_english: "Enters card names separated by spaces (max. 4)",
            Locale.japanese: "カードの名前を空白区切りで入力してね！（最大４つ）",
            Locale.taiwan_chinese: "請輸入卡片名稱，不同卡片用空格分開",
        }),
        level = _T({
            Locale.american_english: "Specifies card level.",
            Locale.british_english: "Specifies card level.",
            Locale.japanese: "カードのレベルを指定してね！",
            Locale.taiwan_chinese: "請指定卡片的等級！",
        })
    )
    async def card(self, ctx: Context, cards: str, level: Literal["20", "30", "40", "50", "60"] = "50") -> None:
        cards = [self.data[card] for card in cards.split()[:4]]
        if len(cards) == 1:
            view = DetailView(ctx.interaction, cards[0], int(level))
        else:
            view = DeckView(ctx.interaction, cards, int(level))

        view.message = await ctx.send(embed=await view.embed(), files=view.files(), view=view)
        return


class DetailView(ViewBase):
    def __init__(self, interaction: Interaction, card: compass.Card, level: int):
        super().__init__("card", 180, logger)
        self.locale: Locale = interaction.locale

        self.card: compass.Card = card
        self.level: int = int(level)
        _, self.iconpath = mkstemp(".png")
        self.iconname = basename(self.iconpath)
        _, self.filepath = mkstemp(".png")
        self.filename = basename(self.filepath)
        icon = card.image
        icon.crop((0, 0, icon.width, icon.width)).save(self.iconpath)

        self.run()

        self.message: Message = None

    def run(self) -> None:
        """Generates image and buttons."""
        self.clear_items()
        for level in ["20", "30", "40", "50", "60"]:
            self.add_item(getattr(self, f"level_{level}"))
        self.remove_item(getattr(self, f"level_{self.level}"))
        self.card.generate_image(self.filepath, level=self.level, locale=str(self.locale))
        return

    async def on_timeout(self) -> None:
        self.disable()
        await self.message.edit(view=self)
        if exists(self.iconpath):
            remove(self.iconpath)
        if exists(self.filepath):
            remove(self.filepath)
        return await super().on_timeout()

    async def when_pressed(self, interaction: Interaction, level: int) -> None:
        self.level = level
        self.message = interaction.message
        self.run()
        await interaction.response.edit_message(embed=await self.embed(),
                                                attachments=self.files(),
                                                view=self)
        return

    @ui.button(label="Lv.20", style=ButtonStyle.gray)
    async def level_20(self, interaction: Interaction, button: ui.Button) -> None:
        await self.when_pressed(interaction, 20)

    @ui.button(label="Lv.30", style=ButtonStyle.gray)
    async def level_30(self, interaction: Interaction, button: ui.Button) -> None:
        await self.when_pressed(interaction, 30)

    @ui.button(label="Lv.40", style=ButtonStyle.gray)
    async def level_40(self, interaction: Interaction, button: ui.Button) -> None:
        await self.when_pressed(interaction, 40)

    @ui.button(label="Lv.50", style=ButtonStyle.gray)
    async def level_50(self, interaction: Interaction, button: ui.Button) -> None:
        await self.when_pressed(interaction, 50)

    @ui.button(label="Lv.60", style=ButtonStyle.gray)
    async def level_60(self, interaction: Interaction, button: ui.Button) -> None:
        await self.when_pressed(interaction, 60)

    async def embed(self) -> Embed:
        """|coro|

        Generates card details as ``embed``.

        """
        embed = Embed(color=self.card.attribute.color)
        embed.set_author(name=f"{self.card.name(str(self.locale)).replace('∗','＊')} Lv.{self.level}",
                         url="http://yagitools.html.xdomain.jp/compas-deck/",
                         icon_url=f"attachment://{self.iconname}")
        embed.set_image(url=f"attachment://{self.filename}")
        text = await _T({
            Locale.american_english: "Provide data: Yagi Simulator",
            Locale.british_english: "Provide data: Yagi Simulator",
            Locale.japanese: "データ提供：やぎシミュ",
            Locale.taiwan_chinese: "資料提供：ヤギシミュ（山羊模擬器）",
        }).translate(self.locale)
        embed.set_footer(text=text,
                         icon_url="http://yagitools.html.xdomain.jp/compas-deck/img/bg_credit.png")
        return embed

    def files(self) -> list[File]:
        """Obtains ``file``s as ``list``."""
        return [
            File(self.iconpath, filename=self.iconname),
            File(self.filepath, filename=self.filename),
        ]

class DeckView(ViewBase):
    def __init__(self, interaction: Interaction, cards: list[compass.Card], level: int):
        super().__init__("card", 180, logger)
        self.locale: Locale = interaction.locale

        self.cards: CardData = CardData(cards)
        self.levels: list[int] = [level for _ in self.cards]
        _, self.filepath = mkstemp(".png")
        self.filename = basename(self.filepath)

        self.pointer: int = 0

        self.run(self.locale)

        self.message: Message = None

    def run(self, locale: Locale) -> None:
        """Generates image."""
        self.cards.generate_deck(self.filepath, self.levels, str(locale))

    async def when_pressed(self, interaction: Interaction, image: bool = False) -> None:
        self.message = interaction.message
        if image:
            self.run(self.locale)
        await interaction.response.edit_message(embed=await self.embed(),
                                                attachments=self.files(),
                                                view=self)
        return

    @ui.button(label="＜", style=ButtonStyle.gray)
    async def left(self, interaction: Interaction, button: ui.Button) -> None:
        self.pointer = self.pointer - 1 if self.pointer != 0 else self.pointer
        await self.when_pressed(interaction)
        return

    @ui.button(label="−", style=ButtonStyle.gray)
    async def minus(self, interaction: Interaction, button: ui.Button) -> None:
        self.levels[self.pointer] = self.levels[self.pointer] - 10 if self.levels[self.pointer] != 20 else self.levels[self.pointer]
        await self.when_pressed(interaction, True)
        return

    @ui.button(label="＋", style=ButtonStyle.gray)
    async def plus(self, interaction: Interaction, button: ui.Button) -> None:
        self.levels[self.pointer] = self.levels[self.pointer] + 10 if self.levels[self.pointer] != 60 else self.levels[self.pointer]
        await self.when_pressed(interaction, True)
        return

    @ui.button(label="＞", style=ButtonStyle.gray)
    async def right(self, interaction: Interaction, button: ui.Button) -> None:
        self.pointer = self.pointer + 1 if self.pointer != len(self.cards)-1 else self.pointer
        await self.when_pressed(interaction)
        return

    async def on_timeout(self) -> None:
        self.disable()
        await self.message.edit(view=self)
        if exists(self.filepath):
            remove(self.filepath)
        return await super().on_timeout()

    async def embed(self) -> Embed:
        """|coro|

        Generates card details as ``embed``.

        """
        title = await _T({
            Locale.american_english: "Total Deck Status",
            Locale.british_english: "Total Deck Status",
            Locale.japanese: "デッキ総合力",
            Locale.taiwan_chinese: "卡組綜合力",
        }).translate(self.locale) + f"（Lv.{sum(self.levels)}）"
        embed = Embed(title=title, color=CONFIG.COLOR)
        embed.set_image(url=f"attachment://{self.filename}")
        text = await _T({
            Locale.american_english: "Provide data: Yagi Simulator",
            Locale.british_english: "Provide data: Yagi Simulator",
            Locale.japanese: "データ提供：やぎシミュ",
            Locale.taiwan_chinese: "資料提供：ヤギシミュ（山羊模擬器）",
        }).translate(self.locale) + "　" + "".join(["■" if i == self.pointer else "□"
                                                    for i in range(4)])
        embed.set_footer(text=text,
                         icon_url="http://yagitools.html.xdomain.jp/compas-deck/img/bg_credit.png")
        return embed

    def files(self) -> list[File]:
        """Obtains ``file``s as ``list``."""
        return [
            File(self.filepath, filename=self.filename),
        ]
