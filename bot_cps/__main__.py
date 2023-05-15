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
from argparse import ArgumentParser, Namespace
from glob import glob
from os.path import abspath, basename, dirname, splitext

from discord import Activity, ActivityType, Intents, Object
from discord.ext import commands

from .translator import Translator


logger = logging.getLogger(f"{__name__}")


def get_option() -> Namespace:
    argparser = ArgumentParser()
    argparser.add_argument("--local", action="append", default=[],
                           help="ID of the guild to which the guild commands are registered. \
                                 If not specified, these will be registered as global commands.")
    argparser.add_argument("--log", default=0,
                           help="Channel ID on which the command log is sent.")
    return argparser.parse_args()


class Bot(commands.Bot):
    def __init__(self, locals: list[int] = [], channel_id: int = 0) -> None:
        self.locals = locals
        self.channel_id = channel_id

        intents = Intents.default()

        super().__init__(command_prefix="/", help_command=None, intents=intents)

    async def setup_hook(self) -> None:
        root_path = dirname(abspath(__file__))
        files = glob(f"{root_path}/[!_]*.py")

        await self.tree.set_translator(Translator())

        for ext in map(lambda file: splitext(basename(file))[0], files):
            try:
                await self.load_extension(f"bot_cps.{ext}")
            except commands.NoEntryPointError:
                pass

        if self.locals:
            for local in self.locals:
                guild = Object(local)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user}({self.user.id})")


    def run(self, token: str) -> None:
        super().run(token, root_logger=True)


if __name__ == "__main__":
    args = get_option()
    bot = Bot(args.local, args.log)
    bot.run(os.environ["DISCORD_TOKEN"])
