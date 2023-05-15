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
    "View",
    "context_menu_before_invoke",
)


import json
import logging
from asyncio import Task, create_task
from datetime import datetime, timedelta, timezone
from logging import Logger
from traceback import print_exception
from typing import Any

from discord import ButtonStyle, Embed, Interaction, Locale, ui
from discord.app_commands import check
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.interactions import Interaction

from .config import config
from .exception import NotAgreed
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def send_log(interaction: Interaction, cmd: str, **kwargs: Any) -> None:
    """Sends log to ``client.channel_id``.

    Parameters
    ----------
    interaction: :class:``discord.Interaction``
        Target interaction.
    cmd: :class:`str`
        Target command name.
    **kwargs: Any
        Arguments of the target command.

    """

    if not hasattr(interaction.client, "channel_id"):
        return

    channel_id: int = interaction.client.channel_id
    if channel_id == 0:
        return

    date = (interaction.created_at).strftime("%s")
    description = f"Date: <t:{date}>\n"
    description += f"Name: `{interaction.user}`\n"
    description += f"Locate: `{interaction.guild.name}（{interaction.guild_id}）`\n"
    description += f"Command: `{cmd}`\n"
    description += f"Type: `{str(interaction.type)[16:]}`\n"
    description += "Kwargs:\n"
    for key in kwargs.keys():
        description += f"　{key}: `{kwargs[key]}`\n"

    embed = Embed(color=interaction.user.color, description=description)
    name = f"{interaction.user.display_name}（{interaction.user.id}）"
    embed.set_author(name=name, icon_url=interaction.user.avatar.url)
    channel = await interaction.client.fetch_channel(channel_id)
    await channel.send(embed=embed)
    return

class YesButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: Confirm # just for typing

        self.locale = locale

        self.style = ButtonStyle.green
        self.label = _("同意する").to(self.locale)

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.disable()
        self.view.add_user_to_agreed(interaction)
        content = _("利用規約に同意しました").to(self.locale)
        await interaction.followup.edit_message(interaction.message.id,
                                                content=content, view=self.view)

class NoButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: Confirm # just for typing

        self.locale = locale

        self.style = ButtonStyle.red
        self.label = _("同意しない").to(self.locale)

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.disable()
        content = _("利用規約の同意に拒否しました").to(self.locale)
        await interaction.followup.edit_message(interaction.message.id,
                                                content=content, view=self.view)

class Confirm(ui.View):
    def __init__(self, interaction: Interaction):
        super().__init__(timeout=180)
        self.related: str = "tos"
        self.logger: Logger = logger
        self.locale = interaction.locale
        self.add_item(YesButton(self.locale))
        self.add_item(NoButton(self.locale))

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
        await send_log(interaction, self.related)
        return True

    def add_user_to_agreed(self, interaction: Interaction) -> dict:
        """Adds the user to the agreed list."""
        with open(path.agreed_json, "r") as f:
            agreed_list = json.load(f)

        date = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")
        agreed = {"id":int(str(interaction.user.id)), "date":date}
        agreed_list.append(agreed)

        with open(path.agreed_json, "w") as f:
            json.dump(agreed_list, f, indent=4, ensure_ascii=False)

        return agreed

async def confirm_tos(interaction: Interaction) -> None:
    """
    Sends buttons to confirm whether or not the user agrees
    to the Terms of Service.
    """
    content = _("利用規約に同意しますか？").to(interaction.locale)
    view = Confirm(interaction)
    await interaction.followup.send(content=content, view=view, ephemeral=True)

async def send_tos(interaction: Interaction) -> None:
    """Sends the Terms of Service."""

    embeds: list[Embed] = []

    with open(path.terms_of_service, "r") as f:
        tos = f.readlines()

    tos_former = "".join(tos[:32])
    tos_latter = "".join(tos[33:])

    title = _("利用規約").to(interaction.locale)
    embeds.append(Embed(title=title, description=tos_former, color=config.color))

    title = _("利用規約（続き）").to(interaction.locale)
    embeds.append(Embed(title=title, description=tos_latter, color=config.color))

    if not interaction.response.is_done():
        await interaction.response.send_message(embeds=embeds, ephemeral=True)
    else:
        await interaction.followup.send(embeds=embeds, ephemeral=True)

async def check_agreed(interaction: Interaction) -> None:
    """Confirms agreement to the Terms of Service."""

    def check_in_agreed_list(interaction: Interaction) -> dict:
        """Checks whether the user is in the agreed list."""
        with open(path.agreed_json, "r") as f:
            agreed_list = json.load(f)

        for agreed in agreed_list:
            if agreed["id"] == interaction.user.id:
                return agreed
        return {}

    agreed = check_in_agreed_list(interaction)

    if agreed == {}:
        await send_tos(interaction)
        await confirm_tos(interaction)
        raise NotAgreed(f"{interaction.user} has not agreed to the Terms of Service.")


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
        await send_log(ctx.interaction, ctx.command, **ctx.kwargs)
        await check_agreed(ctx.interaction)
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
        await send_log(interaction, interaction.command.name)
        await check_agreed(interaction)
        return True

    return check(predicate)


class View(ui.View):
    """
    Base class which all views used in this library should
    inherit from.
    """
    def __init__(self, related: str, timeout: float | None, logger: Logger):
        """Constructor of this class.

        Parameters
        ----------
        related: :class:`str`
            A name of the command related to this view.
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
        await send_log(interaction, self.related)
        await check_agreed(interaction)
        return True
