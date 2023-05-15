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
from enum import Enum
from random import sample
from typing import Callable

from discord import (ButtonStyle, Embed, File, Interaction, Locale, Member,
                     Message, app_commands, ui)
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.interactions import Interaction

from .base import Cog, View, context_menu_before_invoke
from .config import config
from .path import path
from .translator import locale_str as _


logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Team(bot))


async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Team")


class Team(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)

        self.team_dict: dict[int, TeamManagementView] = {}
        self.ctx_menu_join = app_commands.ContextMenu(name="/team join",
                                                      callback=self.context_menu_join)
        self.ctx_menu_leave = app_commands.ContextMenu(name="/team leave",
                                                       callback=self.context_menu_leave)
        self.bot.tree.add_command(self.ctx_menu_join)
        self.bot.tree.add_command(self.ctx_menu_leave)

    async def cog_unload(self) -> None:
        await super().cog_unload()
        self.bot.tree.remove_command(self.ctx_menu_join.name, type=self.ctx_menu_join.type)
        self.bot.tree.remove_command(self.ctx_menu_leave.name, type=self.ctx_menu_leave.type)
        return

    @commands.hybrid_command(
        description = _("チーム分けを行う"),
    )
    async def team(self, ctx: Context) -> None:
        await ctx.defer()

        if ctx.guild.id in self.team_dict:
            self.team_dict[ctx.guild.id].disable()
            old = self.team_dict[ctx.guild.id]

            if old.members == [] and old.number == 3:
                team_mgmt = TeamManagementView(ctx.interaction)
            else:
                content = _("以前に使用したデータがあります．初期化しますか？").to(ctx.interaction.locale)
                view = Confirm(ctx.interaction)
                await ctx.send(content=content, view=view, ephemeral=True)
                await view.wait()
                if view.value:
                    team_mgmt = TeamManagementView(ctx.interaction)
                else:
                    team_mgmt = TeamManagementView.continuted(ctx.interaction, old)

            try:
                await old.message.edit(view=old)
            except:
                pass

        else:
            team_mgmt = TeamManagementView(ctx.interaction)

        team_mgmt.message = await ctx.send(embed=team_mgmt.embed, view=team_mgmt)
        self.team_dict[ctx.guild.id] = team_mgmt


    @context_menu_before_invoke(logger, "/team join")
    async def context_menu_join(self, interaction: Interaction, member: Member) -> None:
        """Adds the member to ``team_dict``."""
        await interaction.response.defer(ephemeral=True)

        guild_id: int = interaction.guild_id

        if guild_id not in self.team_dict:
            content = _("先に `/team` コマンドを使用してね！").to(interaction.locale)
            await interaction.followup.send(content=content, ephemeral=True)
            return

        team_mgmt = self.team_dict[guild_id]

        if member not in team_mgmt.members:
            team_mgmt.members.append(member)
            content = _("{0} を追加したよ！").to(interaction.locale)
            await interaction.followup.send(content=content.format(member),
                                            ephemeral=True)
        else:
            content = _("{0} は既に追加されてるよ！").to(interaction.locale)
            await interaction.followup.send(content=content.format(member),
                                            ephemeral=True)

        try:
            team_mgmt.message = await team_mgmt.message.edit(embed=team_mgmt.embed,
                                                             view=team_mgmt)
        except:
            pass


    @context_menu_before_invoke(logger, "/team leave")
    async def context_menu_leave(self, interaction: Interaction, member: Member) -> None:
        """Removes member from ``team_dict``."""
        await interaction.response.defer(ephemeral=True)

        guild_id: int = interaction.guild_id

        if guild_id not in self.team_dict:
            content = _("先に `/team` コマンドを使用してね！").to(interaction.locale)
            await interaction.followup.send(content=content, ephemeral=True)
            return

        team_mgmt = self.team_dict[guild_id]

        if member in team_mgmt.members:
            team_mgmt.members.remove(member)
            content = _("{0} を辞退させたよ！").to(interaction.locale)
            await interaction.followup.send(content=content.format(member),
                                            ephemeral=True)
        else:
            content = _("{0} は既に辞退しているよ！").to(interaction.locale)
            await interaction.followup.send(content=content.format(member),
                                            ephemeral=True)

        try:
            team_mgmt.message = await team_mgmt.message.edit(embed=team_mgmt.embed,
                                                             view=team_mgmt)
        except:
            pass



class JoinButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = _("参加").to(locale)
        self.style = ButtonStyle.green

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.message = interaction.message
        if interaction.user not in self.view.members:
            self.view.members.append(interaction.user)
        await interaction.followup.edit_message(interaction.message.id, embed=self.view.embed)


class LeaveButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = _("辞退").to(locale)
        self.style = ButtonStyle.red

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.message = interaction.message
        if interaction.user in self.view.members:
            self.view.members.remove(interaction.user)
        await interaction.followup.edit_message(interaction.message.id, embed=self.view.embed)


class SyncButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = _("同期").to(locale)
        self.style = ButtonStyle.green

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.message = interaction.message
        if interaction.user.voice:
            self.view.members = interaction.user.voice.channel.members.copy()
        await interaction.followup.edit_message(interaction.message.id, embed=self.view.embed)


class DivideButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = _("実行").to(locale)
        self.style = ButtonStyle.blurple

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        self.view.message = interaction.message

        if len(self.view.members) < 2 * self.view.number:
            content = _("{0}人ずつのチームに分けるには{1}人以上必要だよ！").to(interaction.locale)
            content = content.format(self.view.number, 2*self.view.number)
            await interaction.response.send_message(content)
            return

        members = list(map(lambda member: str(member), self.view.members))
        td = TeamDivide(members, self.view.number)
        await interaction.followup.send(files=td.files, embeds=td.embeds)
        return


class PlusButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = "＋"
        self.style = ButtonStyle.grey

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.message = interaction.message
        self.view.number = self.view.number + 1 if self.view.number != 10 else 10
        await interaction.followup.edit_message(interaction.message.id, embed=self.view.embed)


class MinusButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: TeamManagementView # just for typing

        self.label = "−"
        self.style = ButtonStyle.grey

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.message = interaction.message
        self.view.number = self.view.number - 1 if self.view.number != 1 else 1
        await interaction.followup.edit_message(interaction.message.id, embed=self.view.embed)


class BlankButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()

        self.label = "ㅤ"
        self.style = ButtonStyle.gray
        self.disabled = True


class TeamManagementView(View):
    def __init__(self, interaction: Interaction) -> None:
        """Constructor of this class.

        Parameters
        ----------
        bot: :class:`discord.ext.commands.Bot`
            Represents a Discord bot.
        interaction: :class:`discord.Interaction`
            Target interaction.

        """
        super().__init__("team", None, logger)
        self.locale: Locale = interaction.locale

        self.message: Message | None = None
        self.members: list[Member] = []
        self.number: int = 3

        self.title = _("チーム分け参加者リスト（計 {0} 人）").to(self.locale)
        self.footer = _("１チームあたりの人数：{0}").to(self.locale)

        self.icon_url = interaction.client.user.avatar.url

        self.add_item(JoinButton(self.locale))
        self.add_item(LeaveButton(self.locale))
        self.add_item(BlankButton())
        self.add_item(SyncButton(self.locale))
        self.add_item(BlankButton())

        self.add_item(BlankButton())
        self.add_item(MinusButton(self.locale))
        self.add_item(DivideButton(self.locale))
        self.add_item(PlusButton(self.locale))
        self.add_item(BlankButton())


    @classmethod
    def continuted(cls, interaction: Interaction, obj: "TeamManagementView") -> "TeamManagementView":
        new = cls(interaction)
        new.members = obj.members
        new.number = obj.number
        return new

    @property
    def embed(self) -> Embed:
        """Generates team management board as ``Embed``."""

        title = self.title.format(len(self.members))
        footer = self.footer.format(self.number)

        description = ""
        if self.members != []:
            func: Callable[[Member], str] = lambda member: f"**{member.name}**#{member.discriminator}"
            description = "・" + "\n・".join(list(map(func, self.members)))

        embed = Embed(title=title, description=description, color=config.color)
        embed.set_footer(text=footer, icon_url=self.icon_url)

        return embed



class YesButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: Confirm # just for typing

        self.label = _("はい").to(locale)
        self.style = ButtonStyle.green

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.disable()
        self.view.value = True
        await interaction.followup.edit_message(interaction.message.id, view=self.view)
        return


class NoButton(ui.Button):
    def __init__(self, locale: Locale) -> None:
        super().__init__()

        self.view: Confirm # just for typing

        self.label = _("いいえ").to(locale)
        self.style = ButtonStyle.red

    async def callback(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.view.disable()
        self.view.value = False
        await interaction.followup.edit_message(interaction.message.id, view=self.view)
        return


class Confirm(View):
    """
    Confirm button for team division.
    This view must be initialised asynchronously.
    """
    def __init__(self, interaction: Interaction) -> None:
        """Constructor of this class.

        Parameters
        ----------
        interaction: :class:`discord.Interaction`
            Target interaction.

        """
        super().__init__("team", 30, logger)

        self.locale = interaction.locale
        self.value = True
        self.add_item(YesButton(self.locale))
        self.add_item(NoButton(self.locale))



class Color(tuple[int, str], Enum):

    BLUE = (0x0000ff, path.blue_team)
    RED = (0xFF0000, path.red_team)
    WHITE = (0xFFFFFF, path.white_team)

    def __int__(self) -> int:
        return self.value[0]

    def __str__(self) -> str:
        return self.value[1]


class TeamDivide(object):
    """Divides members into teams.

    ```python
    td = TeamDivide(members, number)
    await send_message(files=td.files, embeds=td.embeds)
    ```

    """

    def __init__(self, members: list[str], number: int) -> None:
        """Constructor of this class.

        Parameters
        ----------
        members: List[:class:`str`]
            Member names list.
        number: :class:`int`
            Number of people per team.

        """

        self.members: set = set(members)
        self.number: int = number
        self.files: list[File] = []
        self.embeds: list[Embed] = []
        self.length: int = len(members)

        self.run()

    def run(self) -> None:
        for _ in range(self.length//(2*self.number)):
            self.prepare(self.generate_team(), Color.BLUE)
            self.prepare(self.generate_team(), Color.RED)
        if len(self.members) != 0:
            self.prepare(list(self.members), Color.WHITE)
        return

    def generate_team(self) -> list[str]:
        """Generates team."""
        output: list[str] = sample(self.members, self.number)
        self.members ^= set(output)
        return output

    def prepare(self, members: list[str], color: Color) -> None:
        """Prepares discord ``Embed``s and ``File``s."""
        file = File(str(color), f"{hash(members[0])}.png")
        embed = Embed(color=int(color))
        embed.set_author(name="　".join(members),
                         icon_url=f"attachment://{file.filename}")
        self.files.append(file)
        self.embeds.append(embed)
        return
