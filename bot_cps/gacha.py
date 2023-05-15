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
from random import choices, shuffle

from compass import Attribute, CardData, Rarity
from discord import File, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import Cog
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Gacha(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Gacha")


# prepares choices for name argument
with open(path.gacha_json, "r") as f:
    gacha_data = json.load(f)

gacha_list = [app_commands.Choice(name=_(data["name"]), value=idx)
              for idx, data in enumerate(gacha_data)]


class Gacha(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.data = CardData()

    @commands.hybrid_command(
        description = _("ガチャシミュレーター"),
    )
    @app_commands.describe(
        name = _("シミュレートするガチャの名前を指定してね！"),
    )
    @app_commands.choices(name=gacha_list)
    async def gacha(self, ctx: Context, name: int) -> None:
        await ctx.defer()

        data = gacha_data[name]
        cards = CardData([])

        rarities = choices([*data["weight"]], [*data["weight"].values()], k=data["k"])

        for rarity in [*data["weight"]]:
            population = CardData([])
            weights = []
            k = sum(el==rarity for el in rarities)
            for condition in data[rarity]:
                args = list(map(lambda el: Attribute(el), condition["attributes"])) \
                     + list(map(lambda el: Rarity(el), condition["rarities"]))
                tmp = self.data.get_cards(*args, **condition["kwargs"], themes=condition["themes"])
                population.extend(tmp)
                weights.extend([condition["weight"]]*len(tmp))
            cards.extend(choices(population, weights, k=k))

        shuffle(cards)
        cards = CardData(sorted(cards, key=lambda card: card.rarity))

        img = cards.generate_large_image()

        image_bytes = BytesIO()
        img.save(image_bytes, "PNG", quality=100, optimize=True)
        image_bytes.seek(0)

        await ctx.send(file=File(fp=image_bytes, filename=f"{ctx.author.id}.png"))
        return
