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
# See the <./config.py> file for the meaning of environment variables.

import logging
from collections import UserDict
from os import remove
from os.path import basename
from random import sample, shuffle

from discord import ButtonStyle, Embed, File, Interaction, Locale, ui
from discord.ext import commands
from discord.ext.commands import Bot, Context

from compass import CardData

from .base import CogBase, ViewBase
from .config import CONFIG
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Deck(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Deck")


data: CardData # use global, initialise at Deck.run_once_when_ready

class Deck(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.parameters: dict[int, DeckParameter] = {}

    async def run_once_when_ready(self) -> None:
        try:
            global data # This is a global variable.
            data = CardData()
        except:
            self.logger.warning("The client cannot use this Cog.")

    @commands.hybrid_command(
        description = _T({
            Locale.american_english: "Generates a deck at random.",
            Locale.british_english: "Generates a deck at random.",
            Locale.japanese: "ランダムなデッキを生成する",
            Locale.taiwan_chinese: "隨機生成卡組",
        })
    )
    async def deck(self, ctx: Context) -> None:
        deck_param = self.parameters.get(ctx.author.id, DeckParameter())
        await deck_param.send_deck(ctx.interaction)
        self.parameters[ctx.author.id] = deck_param
        return

    @commands.hybrid_command(
        name = "deck-setting",
        description = _T({
            Locale.american_english: "Sets parameters for deck cmd.",
            Locale.british_english: "Sets parameters for deck cmd.",
            Locale.japanese: "デッキの設定",
            Locale.taiwan_chinese: "更改卡組設定",
        })
    )
    async def deck_setting(self, ctx: Context) -> None:
        deck_param = self.parameters.get(ctx.author.id, DeckParameter())

        async with DeckParameterView(ctx.interaction, deck_param) as view:
            await ctx.send(view=view, ephemeral=True)

        self.parameters[ctx.author.id] = deck_param


class DeckParameter(UserDict):
    def __init__(self) -> None:
        super().__init__()
        self.data: dict[str, bool]
        self.data.update({
            "balance": True, "random": False,
            "season": False, "normal": True, "collabo": True,
            "fire": True, "water": True, "wood": True,
            "UR": True, "SR": False, "R": False, "N": False
        })

    def __bool__(self) -> bool:
        """Checks the legal parameter."""
        return (self.data["season"] or self.data["normal"] or self.data["collabo"]) and \
               (self.data["fire"] or self.data["water"] or self.data["wood"]) and \
               (self.data["UR"] or self.data["SR"] or self.data["R"] or self.data["N"])

    def update(self, key: str) -> None:
        if key in ["balance", "random"]:
            self.data["balance"] = not self.data["balance"]
            self.data["random"] = not self.data["random"]
        else:
            self.data[key] = not self.data[key]
            if not bool(self):
                self.data[key] = not self.data[key]
        return

    @property
    def args(self) -> tuple[str]:
        """Obtains ``CardData.get_cards()`` arguments."""
        retval = []
        for k, v in self.data.items():
            if k not in ["balance", "random", "season", "normal", "collabo"] and v:
                retval.append(k)
        return tuple(retval)

    @property
    def kwargs(self) -> dict[str, bool]:
        """Obtains ``CardData.get_cards()`` keyword arguments."""
        return {
            "season": self.data["season"],
            "normal": self.data["normal"],
            "collabo": self.data["collabo"],
        }

    async def send_deck(self, interaction: Interaction) -> None:
        """Generates deck from ``parameters`` and sends its."""
        global data # This is a global variable.
        pool = data.get_cards(*self.args, **self.kwargs)

        if self.data["random"]:
            cards = CardData(sample(pool, k=4))
        else: # self.data["balance"] == True
            card_dicts = pool.divide()
            for value in card_dicts.values():
                shuffle(value)

            if card_dicts["rec"] == []:
                patterns = [["off","def","def","def"],["off","off","def","def"],
                            ["off","off","off","def"],["off","def","def","sup"],
                            ["def","def","sup","sup"],["def","def","def","sup"],]
            else:
                patterns = [["off","off","def","rec"],["off","def","def","rec"],
                            ["off","def","rec","rec"],["off","sup","def","rec"],
                            ["sup","sup","def","rec"],["sup","def","def","rec"],
                            ["off","off","def","def"],["off","def","def","def"],]
            shuffle(patterns)
            pattern = patterns.pop()
            shuffle(pattern)

            cards = []
            for kind in pattern:
                if card_dicts[kind] != []:
                    cards.append(card_dicts[kind].pop())

            cards = CardData(cards)

        if len(cards) != 4:
            content = await _T({
                Locale.american_english: "The deck cannot be generated under this condition.",
                Locale.british_english: "The deck cannot be generated under this condition.",
                Locale.japanese: "その条件ではデッキを生成できません",
                Locale.taiwan_chinese: "無法用該條件生成卡組",
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content)
        else:
            filepath = cards.generate_deck(locale=str(interaction.locale))
            filename = basename(filepath)
            title = await _T({
                Locale.american_english: "Total Deck Status",
                Locale.british_english: "Total Deck Status",
                Locale.japanese: "デッキ総合力",
                Locale.taiwan_chinese: "卡組綜合力",
            }).translate(interaction.locale) + f"（Lv.200）"
            embed = Embed(title=title, color=CONFIG.COLOR)
            embed.set_image(url=f"attachment://{filename}")
            text = await _T({
                Locale.american_english: "Provide data: Yagi Simulator",
                Locale.british_english: "Provide data: Yagi Simulator",
                Locale.japanese: "データ提供：やぎシミュ",
                Locale.taiwan_chinese: "資料提供：ヤギシミュ（山羊模擬器）",
            }).translate(interaction.locale)
            embed.set_footer(text=text,
                            icon_url="http://yagitools.html.xdomain.jp/compas-deck/img/bg_credit.png")
            file = File(filepath, filename=filename)
            await interaction.response.send_message(embed=embed, file=file)
            remove(filepath)
        return


class DeckParameterButton(ui.Button):
    """``Button`` for deck setting."""
    def __init__(self, key: str, style: ButtonStyle, row: int, _Tlabel: _T) -> None:
        super().__init__()
        self.view: DeckParameterView # just for typing
        self.key = key
        self.default_style: ButtonStyle = style
        self.row = row
        self._Tlabel = _Tlabel

    async def callback(self, interaction: Interaction) -> None:
        self.view.deck_parameter.update(self.key)
        self.view.update_style()
        await interaction.response.edit_message(view=self.view)

class DeckParameterResetButton(ui.Button):
    """Reset ``Button`` for deck setting."""
    def __init__(self) -> None:
        super().__init__()
        self.view: DeckParameterView # just for typing

        self._Tlabel = _T({
            Locale.american_english: "Reset",
            Locale.british_english: "Reset",
            Locale.japanese: "初期化",
            Locale.taiwan_chinese: "初始化",
        })
        self.style = ButtonStyle.red
        self.row = 4

    async def callback(self, interaction: Interaction) -> None:
        self.view.deck_parameter.__init__()
        self.view.update_style()
        await interaction.response.edit_message(view=self.view)

class DeckParameterExecuteButton(ui.Button):
    """Execute ``Button`` for deck setting."""
    def __init__(self) -> None:
        super().__init__()
        self.view: DeckParameterView # just for typing

        self._Tlabel = _T({
            Locale.american_english: "Execute",
            Locale.british_english: "Execute",
            Locale.japanese: "実行",
            Locale.taiwan_chinese: "執行",
        })
        self.style = ButtonStyle.green
        self.row = 4

    async def callback(self, interaction: Interaction) -> None:
        await self.view.deck_parameter.send_deck(interaction)


class DeckParameterView(ViewBase):
    def __init__(self, interaction: Interaction, parameter: DeckParameter):
        super().__init__("deck-setting", 600, logger)
        self.locale: Locale = interaction.locale
        self.deck_parameter: DeckParameter = parameter

        self.add_item(DeckParameterButton("normal",
            ButtonStyle.blurple, row=0,
            _Tlabel = _T({
                Locale.american_english: "Normal",
                Locale.british_english: "Normal",
                Locale.japanese: "恒常",
                Locale.taiwan_chinese: "常駐",
            })
        ))
        self.add_item(DeckParameterButton("collabo",
            ButtonStyle.blurple, row=0,
            _Tlabel = _T({
                Locale.american_english: "Collabo",
                Locale.british_english: "Collabo",
                Locale.japanese: "コラボ",
                Locale.taiwan_chinese: "合作",
            })
        ))
        self.add_item(DeckParameterButton("season",
            ButtonStyle.blurple, row=0,
            _Tlabel = _T({
                Locale.american_english: "Season",
                Locale.british_english: "Season",
                Locale.japanese: "シーズン",
                Locale.taiwan_chinese: "賽季卡",
            })
        ))
        self.add_item(DeckParameterButton("fire",
            ButtonStyle.red, row=1,
            _Tlabel = _T({
                Locale.american_english: "Fire",
                Locale.british_english: "Fire",
                Locale.japanese: "火",
                Locale.taiwan_chinese: "火",
            })
        ))
        self.add_item(DeckParameterButton("water",
            ButtonStyle.blurple, row=1,
            _Tlabel = _T({
                Locale.american_english: "Water",
                Locale.british_english: "Water",
                Locale.japanese: "水",
                Locale.taiwan_chinese: "水",
            })
        ))
        self.add_item(DeckParameterButton("wood",
            ButtonStyle.green, row=1,
            _Tlabel = _T({
                Locale.american_english: "Wood",
                Locale.british_english: "Wood",
                Locale.japanese: "木",
                Locale.taiwan_chinese: "木",
            })
        ))
        self.add_item(DeckParameterButton("UR",
            ButtonStyle.green, row=2,
            _Tlabel = _T({
                Locale.american_english: "UR",
                Locale.british_english: "UR",
                Locale.japanese: "UR",
                Locale.taiwan_chinese: "UR",
            })
        ))
        self.add_item(DeckParameterButton("SR",
            ButtonStyle.green, row=2,
            _Tlabel = _T({
                Locale.american_english: "SR",
                Locale.british_english: "SR",
                Locale.japanese: "SR",
                Locale.taiwan_chinese: "SR",
            })
        ))
        self.add_item(DeckParameterButton("R",
            ButtonStyle.green, row=2,
            _Tlabel = _T({
                Locale.american_english: "R",
                Locale.british_english: "R",
                Locale.japanese: "R",
                Locale.taiwan_chinese: "R",
            })
        ))
        self.add_item(DeckParameterButton("N",
            ButtonStyle.green, row=2,
            _Tlabel = _T({
                Locale.american_english: "N",
                Locale.british_english: "N",
                Locale.japanese: "N",
                Locale.taiwan_chinese: "N",
            })
        ))
        self.add_item(DeckParameterButton("balance",
            ButtonStyle.blurple, row=3,
            _Tlabel = _T({
                Locale.american_english: "Balance",
                Locale.british_english: "Balance",
                Locale.japanese: "バランス",
                Locale.taiwan_chinese: "均衡",
            })
        ))
        self.add_item(DeckParameterButton("random",
            ButtonStyle.blurple, row=3,
            _Tlabel = _T({
                Locale.american_english: "Random",
                Locale.british_english: "Random",
                Locale.japanese: "ランダム",
                Locale.taiwan_chinese: "隨機",
            })
        ))
        self.add_item(DeckParameterResetButton())
        self.add_item(DeckParameterExecuteButton())

        self.update_style()

    def update_style(self) -> None:
        """Updates all buttons style."""
        for child in self.children:
            if hasattr(child, "key"):
                if self.deck_parameter[child.key]:
                    child.style = child.default_style
                else:
                    child.style = ButtonStyle.gray
