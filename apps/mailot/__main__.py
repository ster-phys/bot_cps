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
import os
from glob import glob
from os.path import abspath, basename, dirname, splitext

from discord import Activity, ActivityType, Intents, Object
from discord.ext import commands

from ..config import config


logger = logging.getLogger(f"{__name__}")


class Bot(commands.Bot):
    def __init__(self) -> None:
        activity = Activity(name="bot_cps", type=ActivityType.playing)

        super().__init__(command_prefix="/", help_command=None,
                         intents=Intents.all(), activity=activity)

    async def setup_hook(self) -> None:
        root_path = dirname(abspath(__file__))
        files = glob(f"{root_path}/[!_]*.py")

        for ext in map(lambda file: splitext(basename(file))[0], files):
            await self.load_extension(f"apps.mailot.{ext}")

        self.tree.copy_global_to(guild=Object(config.guilds.bot_cps))
        await self.tree.sync(guild=Object(config.guilds.bot_cps))

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}({self.user.id})")


    def run(self, token: str) -> None:
        super().run(token, root_logger=True)


if __name__ == "__main__":
    bot = Bot()
    bot.run(os.environ["DISCORD_TOKEN"])
