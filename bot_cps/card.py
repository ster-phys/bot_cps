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

import compass
from compass import CardData, get_translator
from discord import (ButtonStyle, Embed, File, Interaction, Locale, Message,
                     app_commands, ui)
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog, View
from .config import config
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Card(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Card")


class Card(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.data: CardData = CardData()

    @commands.hybrid_command(
        description = _("カードの詳細またはデッキのステータスを調べる"),
    )
    @app_commands.describe(
        cards = _("カードの名前を空白区切りで入力してね！（最大４つ）"),
        level = _("カードのレベルを指定してね！"),
    )
    async def card(self, ctx: Context, cards: str,
                   level: Literal["20", "30", "40", "50", "60"] = "50") -> None:
        await ctx.defer()

        cards = [self.data[card] for card in cards.split()[:4]]
        if len(cards) == 1:
            view = DetailView(ctx.interaction, cards[0], int(level))
        else:
            view = DeckView(ctx.interaction, cards, int(level))

        view.message = await ctx.send(embed=view.embed, files=view.files, view=view)
        return


class DetailView(View):
    def __init__(self, interaction: Interaction, card: compass.Card, level: int):
        super().__init__("card", 180, logger)

        self.locale: Locale = interaction.locale
        self.translator = get_translator(self.locale.value)

        self.card: compass.Card = card
        self.level: int = level

        self.name = self.translator(self.card.name) + " Lv.{0}"
        self.text = _("データ提供：やぎシミュ").to(self.locale)

        self.image: File | None = None
        self.message: Message | None = None

        self.update_view()

    @property
    def icon(self) -> File:
        icon = self.card.image
        icon = icon.crop((0, 0, icon.width, icon.width))

        image_bytes = BytesIO()
        icon.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        return File(fp=image_bytes, filename=f"icon.png")


    def update_view(self) -> None:
        self.clear_items()
        for level in "20", "30", "40", "50", "60":
            self.add_item(getattr(self, f"level_{level}"))
        self.remove_item(getattr(self, f"level_{self.level}"))

        image = self.card.generate_image(self.level, self.locale.value)

        image_bytes = BytesIO()
        image.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        self.image: File = File(fp=image_bytes, filename=f"image.png")


    async def on_timeout(self) -> None:
        self.disable()
        await self.message.edit(view=self)
        return await super().on_timeout()

    async def when_pressed(self, interaction: Interaction, level: int) -> None:
        await interaction.response.defer()

        self.level = level
        self.message = interaction.message
        self.update_view()
        await interaction.followup.edit_message(self.message.id, embed=self.embed,
                                                attachments=self.files, view=self)


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


    @property
    def embed(self) -> Embed:
        embed = Embed(color=self.card.attribute.color)
        embed.set_author(name=self.name.format(self.level),
                         url="http://yagitools.html.xdomain.jp/compas-deck/",
                         icon_url=f"attachment://{self.icon.filename}")
        embed.set_image(url=f"attachment://{self.image.filename}")
        embed.set_footer(text=self.text,
                         icon_url="http://yagitools.html.xdomain.jp/compas-deck/img/bg_credit.png")
        return embed

    @property
    def files(self) -> list[File]:
        return [self.icon, self.image]


class DeckView(View):
    def __init__(self, interaction: Interaction, cards: list[compass.Card], level: int):
        super().__init__("card", 180, logger)

        self.locale: Locale = interaction.locale

        self.cards: CardData = CardData(cards)
        self.levels: list[int] = [level] * len(self.cards)

        self.image: File | None = None

        self.update_view()

        self.pointer: int = 0
        self.message: Message | None = None

        self.title = _("デッキ総合力").to(self.locale) + "（Lv.{0}）"
        self.text = _("データ提供：やぎシミュ").to(self.locale) + "　{0}"


    def update_view(self) -> None:
        image = self.cards.generate_deck(self.levels, self.locale.value)

        image_bytes = BytesIO()
        image.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        self.image: File = File(fp=image_bytes, filename=f"image.png")


    async def when_pressed(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.message = interaction.message
        self.update_view()
        await interaction.followup.edit_message(self.message.id, embed=self.embed,
                                                attachments=self.files, view=self)


    @ui.button(label="＜", style=ButtonStyle.gray)
    async def left(self, interaction: Interaction, button: ui.Button) -> None:
        self.pointer = self.pointer - 1 if self.pointer != 0 else 0
        await self.when_pressed(interaction)
        return

    @ui.button(label="−", style=ButtonStyle.gray)
    async def minus(self, interaction: Interaction, button: ui.Button) -> None:
        self.levels[self.pointer] = self.levels[self.pointer] - 10 if self.levels[self.pointer] != 20 else 20
        await self.when_pressed(interaction)
        return

    @ui.button(label="＋", style=ButtonStyle.gray)
    async def plus(self, interaction: Interaction, button: ui.Button) -> None:
        self.levels[self.pointer] = self.levels[self.pointer] + 10 if self.levels[self.pointer] != 60 else 60
        await self.when_pressed(interaction)
        return

    @ui.button(label="＞", style=ButtonStyle.gray)
    async def right(self, interaction: Interaction, button: ui.Button) -> None:
        self.pointer = self.pointer + 1 if self.pointer != len(self.cards)-1 else len(self.cards)-1
        await self.when_pressed(interaction)
        return


    async def on_timeout(self) -> None:
        self.disable()
        await self.message.edit(view=self)
        return await super().on_timeout()


    @property
    def embed(self) -> Embed:
        embed = Embed(title=self.title.format(sum(self.levels)), color=config.color)
        embed.set_image(url=f"attachment://{self.image.filename}")
        embed.set_footer(text=self.text.format("".join(["■" if i == self.pointer else "□"
                                               for i in range(4)])))
        return embed

    @property
    def files(self) -> list[File]:
        return [self.image]
