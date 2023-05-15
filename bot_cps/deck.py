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
from collections import UserDict
from io import BytesIO
from random import choice, sample, shuffle
from typing import Literal

from compass import Attribute, CardData, Rarity
from discord import ButtonStyle, Embed, File, Interaction, Locale, ui
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.interactions import Interaction

from .base import Cog, View
from .config import config
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Deck(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Deck")


data: CardData = CardData()


class Deck(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.user_argument: dict[int, Argument] = {}

    @commands.hybrid_command(
        description = _("ランダムなデッキを生成する"),
    )
    async def deck(self, ctx: Context) -> None:
        argument = self.user_argument.get(ctx.author.id, Argument())
        await argument.send_deck(ctx.interaction)
        self.user_argument[ctx.author.id] = argument
        return

    @commands.hybrid_command(
        name = "deck-setting",
        description = _("デッキの設定"),
    )
    async def deck_setting(self, ctx: Context) -> None:
        await ctx.defer(ephemeral=True)

        argument = self.user_argument.get(ctx.author.id, Argument())
        view = DeckView(ctx.interaction, argument)
        await ctx.send(view=view, ephemeral=True)
        self.user_argument[ctx.author.id] = argument


class Argument(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.data: dict[Literal["balance", "random", \
                                "season", "normal", "collabo"] | Attribute | Rarity, bool]
        self.data.update({"balance": True, "random": False,})
        self.data.update({"season": False, "normal": True, "collabo": True})
        self.data.update({attribute: True for attribute in Attribute})
        self.data.update({rarity: False for rarity in Rarity})
        self.data[Rarity.UR] = True

    def __bool__(self) -> bool:
        """Checks that this is legal parameter."""
        flag1 = self.data["season"] or self.data["normal"] or self.data["collabo"]
        flag2, flag3 = False, False
        for attribute in Attribute:
            flag2 |= self.data[attribute]
        for rarity in Rarity:
            flag3 |= self.data[rarity]
        return flag1 and flag2 and flag3


    def update(self, key: Literal["balance", "random", \
                                  "season", "normal", "collabo"] | Attribute | Rarity) -> None:
        if key in ["balance", "random"]:
            self.data["balance"] = not self.data["balance"]
            self.data["random"] = not self.data["random"]
        else:
            self.data[key] = not self.data[key]
            if not bool(self):
                self.data[key] = not self.data[key]
        return


    @property
    def args(self) -> tuple[Attribute | Rarity]:
        """Obtains ``compass.CardData.get_cards`` arguments."""
        retval = []
        for attribute in Attribute:
            if self.data[attribute]:
                retval.append(attribute)
        for rarity in Rarity:
            if self.data[rarity]:
                retval.append(rarity)
        return tuple(retval)

    @property
    def kwargs(self) -> dict[Literal["season", "normal", "collabo"], bool]:
        """Obtains ``compass.CardData.get_cards`` keyword arguments."""
        return {
            "season": self.data["season"],
            "normal": self.data["normal"],
            "collabo": self.data["collabo"],
        }


    async def send_deck(self, interaction: Interaction) -> None:
        """Generates deck ``discord.Embed`` from this and sends its."""

        await interaction.response.defer()

        pool: CardData = data.get_cards(*self.args, **self.kwargs)

        if self.data["random"]:
            cards = CardData(sample(pool, k=4))
        else: # self.data["balance"] == True
            divided_pool: dict[Literal["off", "def", "sup", "rec"], CardData] = pool.divide()

            for each_pool in divided_pool.values():
                shuffle(each_pool)

            if divided_pool["rec"] == []:
                patterns = [["off","def","def","def"],["off","off","def","def"],
                            ["off","off","off","def"],["off","def","def","sup"],
                            ["def","def","sup","sup"],["def","def","def","sup"],]
            else:
                patterns = [["off","off","def","rec"],["off","def","def","rec"],
                            ["off","def","rec","rec"],["off","sup","def","rec"],
                            ["sup","sup","def","rec"],["sup","def","def","rec"],
                            ["off","off","def","def"],["off","def","def","def"],]

            pattern = choice(patterns)
            shuffle(pattern)

            cards = []
            for type_ in pattern:
                if divided_pool[type_] != []:
                    cards.append(divided_pool[type_].pop())

            cards = CardData(cards)

            if len(cards) != 4:
                content = _("その条件ではデッキを生成できません").to(interaction.locale)
                await interaction.followup.send(content=content)
                return

        img = cards.generate_deck(locale=interaction.locale.value)

        image_bytes = BytesIO()
        img.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        file = File(fp=image_bytes, filename=f"{interaction.user.id}.png")


        title = _("デッキ総合力（Lv.200）").to(interaction.locale)
        embed = Embed(title=title, color=config.color)
        embed.set_image(url=f"attachment://{file.filename}")

        text = _("データ提供：やぎシミュ").to(interaction.locale)
        embed.set_footer(text=text,
                            icon_url="http://yagitools.html.xdomain.jp/compas-deck/img/bg_credit.png")

        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, file=file)
        else:
            await interaction.followup.send(embed=embed, file=file)


class ArgumentButton(ui.Button):
    def __init__(self, key: Literal["balance", "random", \
                                    "season", "normal", "collabo"] | Attribute | Rarity,
                 label: str, style: ButtonStyle, row: int) -> None:
        super().__init__()

        self.view: DeckView # just for typing

        self.style = style
        self.label = label
        self.row = row

        self.default_style = style
        self.key = key

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.update(self.key)
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)

class ResetButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: DeckView # just for typing

        self.label = _("初期化").to(locale)
        self.style = ButtonStyle.red
        self.row = 4

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.argument.__init__()
        self.view.update_style()
        await interaction.followup.edit_message(interaction.message.id, view=self.view)

class ExecuteButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: DeckView # just for typing

        self.label = _("実行").to(locale)
        self.style = ButtonStyle.green
        self.row = 4

    async def callback(self, interaction: Interaction) -> None:
        await self.view.argument.send_deck(interaction)


class DeckView(View):
    def __init__(self, interaction: Interaction, argument: Argument):
        super().__init__("deck", 600, logger)
        self.locale: Locale = interaction.locale
        self.argument: Argument = argument

        for key, label, style, row in [
            ("normal", _("恒常").to(self.locale), ButtonStyle.blurple, 0,),
            ("collabo", _("コラボ").to(self.locale), ButtonStyle.blurple, 0,),
            ("season", _("シーズン").to(self.locale), ButtonStyle.blurple, 0,),
            (Attribute.FIRE, _("火").to(self.locale), ButtonStyle.red, 1,),
            (Attribute.WATER, _("水").to(self.locale), ButtonStyle.blurple, 1,),
            (Attribute.WOOD, _("木").to(self.locale), ButtonStyle.green, 1,),
            (Rarity.UR, "UR", ButtonStyle.green, 2,),
            (Rarity.SR, "SR", ButtonStyle.green, 2,),
            (Rarity.R, "R", ButtonStyle.green, 2,),
            (Rarity.N, "N", ButtonStyle.green, 2,),
            ("balance", _("バランス").to(self.locale), ButtonStyle.blurple, 3,),
            ("random", _("ランダム").to(self.locale), ButtonStyle.blurple, 3,),
        ]:
            self.add_item(ArgumentButton(key, label, style, row))

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
