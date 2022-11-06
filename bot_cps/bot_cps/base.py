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

__all__ = (
    "CogBase",
    "ViewBase",
    "context_menu_before_invoke",
)

from asyncio import Task, create_task
from logging import Logger
from traceback import print_exception

from discord import Interaction, ui
from discord.app_commands import check
from discord.ext import commands
from discord.ext.commands import Bot, Context


class CogBase(commands.Cog):
    """
    Base class which all cogs used in this library should
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


def context_menu_before_invoke(logger: Logger, name: str):
    """All context menus must be decorated with this decorator.

    Parameters
    ----------
    logger: :class:`logging.Logger`
        Instances of the Logger class represent a single logging channel.
    name: :class:`str`
        Name of this context menu.

    ```python
    logger: logging.Logger = ...

    @context_menu_before_invoke(logger, "name")
    async def your_context_menu(self, interaction: Interaction, member: Member):
        pass
    ```

    """

    async def predicate(interaction: Interaction) -> bool:
        logger.info(f"[Context Menu: {name}]"\
                    f" has been used by {interaction.user}({interaction.user.id}).")
        return True

    return check(predicate)


class ViewBase(ui.View):
    """
    Base class which all views used in this library should
    inherit from.
    """
    def __init__(self, related: str, timeout: float | None, logger: Logger):
        """Constructor of this class.

        When translating the labels of items, take note of the following.
        In the item, the label pre-translation must be registered with
        the attribute ``_Tlabel``. In this view, the locale of the translation
        destination must be registered with the attribute ``locale``.
        The ``View`` itself must also be implemented using the ``async with`` syntax.

        Parameters
        ----------
        related: :class:`str`
            A Name of the command related to this view.
        timeout: :class:`float` | None
            Timeout in seconds from last interaction with the UI before
            no longer accepting input.
            If `None` then there is no timeout.
        logger: :class:`logging.Logger`
            Instances of the Logger class represent a single logging channel.

        """
        self.related: str = related
        self.logger: Logger = logger
        super().__init__(timeout=timeout)

    async def __aenter__(self) -> "ViewBase":
        """Translates all labels of children.

        The item must have a ``_Tlabel``.
        The view needs a ``locale``.

        """
        for child in self.children:
            if hasattr(child, "_Tlabel") and hasattr(self, "locale"):
                child.label = await child._Tlabel.translate(self.locale)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def disable(self) -> None:
        """Disables all children."""
        for child in self.children:
            child.disabled = True
        self.stop()
        return

    async def interaction_check(self, interaction: Interaction) -> bool:
        """
        After outputting the log, it checks whether the user
        agrees with the Terms of Service.

        Do not rewrite this method.

        """
        self.logger.info(f"[View: {self.related}]"\
                         f" has been used by {interaction.user}({interaction.user.id}).")
        return True
