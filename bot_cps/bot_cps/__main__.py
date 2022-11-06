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

import sys
from os.path import dirname

# To recognise bot_cps library, appends parent directory.
sys.path.append(dirname(dirname(__file__)))

import os

from discord import Intents, Object

import bot_cps

TOKEN: str = os.environ["DISCORD_TOKEN"]
GUILD_ID: str = os.environ["BOT_CPS_GUILD_ID"]
GUILD_OBJECT = Object(id=int(GUILD_ID))

class TestBot(bot_cps.Bot):
    def __init__(self) -> None:
        super().__init__("/", intents=Intents.default())

    async def setup_hook(self) -> None:
        await super().setup_hook()
        for ext in bot_cps.EXTENSIONS:
            await self.load_extension(ext)
        self.tree.copy_global_to(guild=GUILD_OBJECT)
        await self.tree.sync(guild=GUILD_OBJECT)

if __name__ == "__main__":
    bot = TestBot()
    bot.run(TOKEN)
