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

__all__ = (
    "Cog",
)


from asyncio import Task, create_task
from logging import Logger
from traceback import print_exception

from discord.ext import commands
from discord.ext.commands import Bot, Context


class Cog(commands.Cog):
    """
    Base class which all cogs used in this repository should
    inherit from.
    """
    def __init__(self, bot: Bot, logger: Logger) -> None:
        """Constructor of this class.

        Parameters
        ----------
        bot: :class:`discord.ext.commands.Bot`
            ``disocord.py`` bot class.
        logger: :class:`logging.Logger`
            Instances of the Logger class represent a single logging channel.

        """
        super().__init__()
        self.bot: Bot = bot
        self.logger: Logger = logger
        task = create_task(self._run_once_when_ready())
        task.add_done_callback(self._error_handler)

    def _error_handler(self, task: Task) -> None:
        exc = task.exception()
        if exc:
            print_exception(type(exc), exc, exc.__traceback__)

    async def _run_once_when_ready(self) -> None:
        await self.bot.wait_until_ready()
        await self.run_once_when_ready()

    async def run_once_when_ready(self) -> None:
        """
        A method that is called when the bot is ready.
        Processes only once.
        """
        pass

    async def cog_before_invoke(self, ctx: Context) -> None:
        self.logger.info(f"[{ctx.prefix}{ctx.command}]"\
                         f" has been used by {ctx.author}({ctx.author.id}).")
        return await super().cog_before_invoke(ctx)

    async def cog_load(self) -> None:
        self.logger.info(f"Cog {self.__cog_name__} has been loaded.")
        return await super().cog_load()

    async def cog_unload(self) -> None:
        self.logger.info(f"Cog {self.__cog_name__} has been unloaded.")
        return await super().cog_unload()
