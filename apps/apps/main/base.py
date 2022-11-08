"""
A library that provides Bot Launcher Managed by bot_cps

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
from datetime import datetime, timedelta, timezone
from logging import Logger
from typing import Any

from discord import ButtonStyle, Embed, Interaction, Locale, ui
from discord.app_commands import check
from discord.ext.commands import Context

from bot_cps import base
from bot_cps.translator import _T

from ..config import CONFIG, PATH
from .exception import NotAgreed

logger = logging.getLogger(__name__)


def save_log(interaction: Interaction, cmd: str, **kwargs: Any) -> None:
    """Saves log to ``LOG_FILE``.

    Parameters
    ----------
    interaction: :class:``discord.Interaction``
        Target interaction.
    cmd: :class:`str`
        Target command name.
    **kwargs: Any
        Arguments of the target command.

    """
    date = (interaction.created_at + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")

    user_id = interaction.user.id
    guild_name = interaction.guild.name
    guild_id = interaction.guild_id
    channel_name = interaction.channel.name
    channel_id = interaction.channel_id

    log = f"{date},{interaction.user},{user_id},{guild_name},{guild_id},"\
          f"{channel_name},{channel_id},{interaction.type},{cmd},"

    for key in kwargs.keys():
        log += f"{key}: {kwargs[key]} "

    with open(PATH.LOG_FILE, "a") as f:
        f.write(log + "\n")

    return

async def send_log(interaction: Interaction, cmd: str, **kwargs: Any) -> None:
    """Sends log to ``CHANNEL_ID``.

    Parameters
    ----------
    interaction: :class:``discord.Interaction``
        Target interaction.
    cmd: :class:`str`
        Target command name.
    **kwargs: Any
        Arguments of the target command.

    """
    date = (interaction.created_at + timedelta(hours=9)).strftime("%s")
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
    channel = await interaction.client.fetch_channel(CONFIG.CHANNEL_IDs.COMMAND)
    await channel.send(embed=embed)
    return


class YesButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()
        self.style = ButtonStyle.green

        self._Tlabel = _T({
            Locale.american_english: "Yes",
            Locale.british_english: "Yes",
            Locale.japanese: "同意する",
            Locale.taiwan_chinese: "同意",
        })

    async def callback(self, interaction: Interaction) -> None:
        self.view.disable()
        self.view.add_user_to_agreed(interaction)
        content = await _T({
            Locale.american_english: "You have agreed to the Terms of Service.",
            Locale.british_english: "You have agreed to the Terms of Service.",
            Locale.japanese: "利用規約に同意しました",
            Locale.taiwan_chinese: "已同意使用條款",
        }).translate(interaction.locale)
        await interaction.response.edit_message(content=content, view=self.view)
        return

class NoButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()
        self.style = ButtonStyle.red

        self._Tlabel = _T({
            Locale.american_english: "No",
            Locale.british_english: "No",
            Locale.japanese: "同意しない",
            Locale.taiwan_chinese: "不同意",
        })

    async def callback(self, interaction: Interaction) -> None:
        self.view.disable()
        content = await _T({
            Locale.american_english: "You have **not** agreed to the Terms of Service.",
            Locale.british_english: "You have **not** agreed to the Terms of Service.",
            Locale.japanese: "利用規約の同意に拒否しました",
            Locale.taiwan_chinese: "已拒絕同意使用條款",
        }).translate(interaction.locale)
        await interaction.response.edit_message(content=content, view=self.view)
        return

class Confirm(base.ViewBase):
    """Confirm button for the Terms of Service."""
    def __init__(self, interaction: Interaction):
        super().__init__("tos", 180, logger)
        self.locale = interaction.locale
        self.add_item(YesButton())
        self.add_item(NoButton())

    async def interaction_check(self, interaction: Interaction) -> bool:
        # The button to agree to the Terms of Service must be available to
        # those who have not agreed to the Terms of Service.
        self.logger.info(f"[View: {self.related}]"\
                         f" has been used by {interaction.user}({interaction.user.id}).")
        save_log(interaction, self.related)
        await send_log(interaction, self.related)
        return True

    def add_user_to_agreed(self, interaction: Interaction) -> dict:
        """Adds the user to the agreed list."""
        with open(PATH.AGREED_JSON, "r") as f:
            agreed_list = json.load(f)

        date = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y/%m/%d %H:%M:%S")
        agreed = {"id":int(str(interaction.user.id)), "date":date}
        agreed_list.append(agreed)

        with open(PATH.AGREED_JSON, "w") as f:
            json.dump(agreed_list, f, indent=4, ensure_ascii=False)

        return agreed


async def confirm_tos(interaction: Interaction) -> None:
    """
    Sends buttons to confirm whether or not the user agrees
    to the Terms of Service.
    """
    content = await _T({
        Locale.american_english: "Do you agree to the Terms of Service?",
        Locale.british_english: "Do you agree to the Terms of Service?",
        Locale.japanese: "利用規約に同意しますか？",
        Locale.taiwan_chinese: "您同意使用條款嗎？",
    }).translate(interaction.locale)

    async with Confirm(interaction) as view:
        await interaction.followup.send(content=content, view=view, ephemeral=True)
    return

async def send_tos(interaction: Interaction) -> None:
    """Sends the Terms of Service."""
    embeds: list[Embed] = []

    with open(PATH.TERMS_OF_SERVICE, "r") as f:
        tos = f.readlines()

    TOS_FORMER = "".join(tos[:32])
    TOS_LATTER = "".join(tos[33:])

    title = await _T({
        Locale.american_english: "Terms of Service",
        Locale.british_english: "Terms of Service",
        Locale.japanese: "利用規約",
        Locale.taiwan_chinese: "使用條款",
    }).translate(interaction.locale)

    embeds.append(Embed(title=title, description=TOS_FORMER,
                        color=CONFIG.COLOR))

    title = await _T({
        Locale.american_english: "Terms of Service (cont.)",
        Locale.british_english: "Terms of Service (cont.)",
        Locale.japanese: "利用規約（続き）",
        Locale.taiwan_chinese: "使用條款（接續）",
    }).translate(interaction.locale)

    embeds.append(Embed(title=title, description=TOS_LATTER,
                        color=CONFIG.COLOR))

    # sends tos
    if not interaction.response.is_done():
        await interaction.response.send_message(embeds=embeds, ephemeral=True)
    else:
        await interaction.followup.send(embeds=embeds, ephemeral=True)

    return

async def check_agreed(interaction: Interaction) -> None:
    """Confirms agreement to the Terms of Service."""

    def check_in_agreed_list(interaction: Interaction) -> dict:
        """Checks whether the user is in the agreed list."""
        with open(PATH.AGREED_JSON, "r") as f:
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


# overrides cog_before_invoke
async def cog_before_invoke(self: base.CogBase, ctx: Context) -> None:
    """
    After outputting the log, it checks whether the user
    agrees with the Terms of Service.
    """
    self.logger.info(f"[{ctx.prefix}{ctx.command}]"\
                     f" has been used by {ctx.author}({ctx.author.id}).")
    save_log(ctx.interaction, ctx.command, **ctx.kwargs)
    await send_log(ctx.interaction, ctx.command, **ctx.kwargs)
    await check_agreed(ctx.interaction)

base.CogBase.cog_before_invoke = cog_before_invoke


# overrides context_menu_before_invoke
def _context_menu_before_invoke(logger: Logger, name: str):
    """When using ``context_menu``, it outputs a log and checks
    whether the user agrees with the Terms of Service.
    """
    async def predicate(interaction: Interaction) -> bool:
        logger.info(f"[Context Menu: {name}]"\
                    f" has been used by {interaction.user}({interaction.user.id}).")
        save_log(interaction, interaction.command.name)
        await send_log(interaction, interaction.command.name)
        await check_agreed(interaction)
        return True

    return check(predicate)

base.context_menu_before_invoke = _context_menu_before_invoke


# overrides interaction_check
async def interaction_check(self, interaction: Interaction) -> bool:
    """
    After outputting the log, it checks whether the user
    agrees with the Terms of Service.

    """
    self.logger.info(f"[View: {self.related}]"\
                     f" has been used by {interaction.user}({interaction.user.id}).")
    save_log(interaction, self.related)
    await send_log(interaction, self.related)
    await check_agreed(interaction)
    return True

base.ViewBase.interaction_check = interaction_check
