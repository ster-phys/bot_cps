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

import logging
from enum import Enum
from random import sample
from typing import Callable

from discord import (ButtonStyle, Embed, File, Interaction, Locale, Member,
                     Message, app_commands, ui)
from discord.ext import commands
from discord.ext.commands import Bot, Context

from .base import CogBase, ViewBase, context_menu_before_invoke
from .config import CONFIG, PATH
from .translator import _T

logger = logging.getLogger(__name__)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Team(bot))

async def teardown(bot: Bot) -> None:
    await bot.remove_cog("Team")

class Team(CogBase):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, logger)
        self.team_dict: dict[int, TeamManagement] = {}
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
        description = _T({
            Locale.american_english: "Team division.",
            Locale.british_english: "Team division.",
            Locale.japanese: "チーム分けを行う",
            Locale.taiwan_chinese: "隨機分組",
        })
    )
    async def team(self, ctx: Context) -> None:
        if ctx.guild.id in self.team_dict:
            self.team_dict[ctx.guild.id].disable()
            old = self.team_dict[ctx.guild.id]

            if old.members == [] and old.number == 3:
                team_mgmt = TeamManagement(self.bot, ctx.interaction)
            else:
                async with Confirm(ctx.interaction) as view:
                    content = await _T({
                        Locale.american_english: "There is data used previously. Initialise?",
                        Locale.british_english: "There is data used previously. Initialise?",
                        Locale.japanese: "以前に使用したデータがあります．初期化しますか？",
                        Locale.taiwan_chinese: "找到過去使用的過的資料，要初始化嗎？",
                    }).translate(ctx.interaction.locale)
                    await ctx.send(content=content, view=view, ephemeral=True)
                    await view.wait()
                    if view.value: # initialises data
                        team_mgmt = TeamManagement(self.bot, ctx.interaction)
                    else:
                        team_mgmt = TeamManagement.continued(self.bot, ctx.interaction, old)
            try:
                await old.message.edit(view=old)
            except:
                pass
        else:
            team_mgmt = TeamManagement(self.bot, ctx.interaction)

        team_mgmt.message = await ctx.send(embed=await team_mgmt.embed(), view=team_mgmt)
        self.team_dict[ctx.guild.id] = team_mgmt
        return

    @context_menu_before_invoke(logger, "/team join")
    async def context_menu_join(self, interaction: Interaction, member: Member) -> None:
        """Adds the member to ``team_dict``."""
        guild_id: int = interaction.guild_id

        if guild_id not in self.team_dict:
            content = await _T({
                Locale.american_english: "Use `/team` command first.",
                Locale.british_english: "Use `/team` command first.",
                Locale.japanese: "先に `/team` コマンドを使用してね！",
                Locale.taiwan_chinese: "請先輸入 `/team` 指令！",
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content, ephemeral=True)
            return

        team_mgmt = self.team_dict[guild_id]

        if member not in team_mgmt.members:
            team_mgmt.members.append(member)
            content = await _T({
                Locale.american_english: "{0} has been added!",
                Locale.british_english: "{0} has been added!",
                Locale.japanese: "{0} を追加したよ！",
                Locale.taiwan_chinese: "已追加 {0}",
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content.format(member), ephemeral=True)
        else:
            content = await _T({
                Locale.american_english: "{0} has **already** been added!",
                Locale.british_english: "{0} has **already** been added!",
                Locale.japanese: "{0} は既に追加されてるよ！",
                Locale.taiwan_chinese: "{0} 已經被追加過了喔！"
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content.format(member), ephemeral=True)

        try:
            team_mgmt.message = await team_mgmt.message.edit(embed=await team_mgmt.embed(),
                                                             view=team_mgmt)
        except:
            pass

        return

    @context_menu_before_invoke(logger, "/team leave")
    async def context_menu_leave(self, interaction: Interaction, member: Member) -> None:
        """Removes member from ``team_dict``."""
        guild_id: int = interaction.guild_id

        if guild_id not in self.team_dict:
            content = await _T({
                Locale.american_english: "Use `/team` command first.",
                Locale.british_english: "Use `/team` command first.",
                Locale.japanese: "先に `/team` コマンドを使用してね！",
                Locale.taiwan_chinese: "請先輸入 `/team` 指令！",
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content, ephemeral=True)
            return

        team_mgmt = self.team_dict[guild_id]

        if member in team_mgmt.members:
            team_mgmt.members.remove(member)
            content = await _T({
                Locale.american_english: "{0} has been left out.",
                Locale.british_english: "{0} has been left out.",
                Locale.japanese: "{0} を辞退させたよ！",
                Locale.taiwan_chinese: "已退出 {0}"
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content.format(member), ephemeral=True)
        else:
            content = await _T({
                Locale.american_english: "{0} has **already** left.",
                Locale.british_english: "{0} has **already** left.",
                Locale.japanese: "{0} は既に辞退しているよ！",
                Locale.taiwan_chinese: "{0} 已經被退出了喔！"
            }).translate(interaction.locale)
            await interaction.response.send_message(content=content.format(member), ephemeral=True)

        try:
            team_mgmt.message = await team_mgmt.message.edit(embed=await team_mgmt.embed(),
                                                             view=team_mgmt)
        except:
            pass

        return


class TeamManagement(ViewBase):
    def __init__(self, bot: Bot, interaction: Interaction):
        """Constructor of this class.

        Parameters
        ----------
        bot: :class:`discord.ext.commands.Bot`
            Represents a Discord bot.
        interaction: :class:`discord.Interaction`
            Target interaction.

        """
        super().__init__("team", None, logger)
        self.bot: Bot = bot
        self.locale: Locale = interaction.locale

        self.message: Message = None
        self.title: _T = _T({
            Locale.american_english: "List of Team Division Participants (Total {0})",
            Locale.british_english: "List of Team Division Participants (Total {0})",
            Locale.japanese: "チーム分け参加者リスト（計 {0} 人）",
            Locale.taiwan_chinese: "各隊參加者名單（共 {0} 人）",
        })
        self.footer: _T = _T({
            Locale.american_english: "People Per Team：{0}",
            Locale.british_english: "People Per Team：{0}",
            Locale.japanese: "１チームあたりの人数：{0}",
            Locale.taiwan_chinese: "各隊人數：{0}",
        })
        self.members: list[Member] = []
        self.number: int = 3

    @ui.button(label="join", style=ButtonStyle.green)
    async def join(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message
        if interaction.user not in self.members:
            self.members.append(interaction.user)
        await interaction.response.edit_message(embed=await self.embed())

    @ui.button(label="leave", style=ButtonStyle.red)
    async def leave(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message
        if interaction.user in self.members:
            self.members.remove(interaction.user)
        await interaction.response.edit_message(embed=await self.embed())
        return

    @ui.button(label="　", style=ButtonStyle.gray, disabled=True)
    async def empty_02(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @ui.button(label="sync", style=ButtonStyle.green)
    async def sync(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message
        if interaction.user.voice:
            self.members = interaction.user.voice.channel.members.copy()
        await interaction.response.edit_message(embed=await self.embed())
        return

    @ui.button(label="　", style=ButtonStyle.gray, disabled=True)
    async def empty_04(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @ui.button(label="　", style=ButtonStyle.gray, disabled=True)
    async def empty_05(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @ui.button(label="−", style=ButtonStyle.grey)
    async def minus(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message
        self.number = self.number - 1 if self.number != 1 else self.number
        await interaction.response.edit_message(embed=await self.embed())
        return

    @ui.button(label="divide", style=ButtonStyle.blurple)
    async def divide(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message

        if len(self.members) < 2 * self.number:
            content = await _T({
                Locale.american_english: "More than {1} people are required to make a team of {0}.",
                Locale.british_english: "More than {1} people are required to make a team of {0}.",
                Locale.japanese: "{0}人ずつのチームに分けるには{1}人以上必要だよ！",
                Locale.taiwan_chinese: "一隊{0}人的隊伍需要{1}人以上參與喔！",
            }).translate(self.locale)
            content = content.format(self.number, 2*self.number)
            await interaction.response.send_message(content)
            return

        td = TeamDivide(list(map(lambda member: str(member), self.members)), self.number)
        await interaction.response.send_message(files=td.files, embeds=td.embeds)
        return

    @ui.button(label="＋", style=ButtonStyle.grey)
    async def plus(self, interaction: Interaction, button: ui.Button) -> None:
        self.message = interaction.message
        self.number = self.number + 1 if self.number != 10 else self.number
        await interaction.response.edit_message(embed=await self.embed())
        return

    @ui.button(label="　", style=ButtonStyle.gray, disabled=True)
    async def empty_09(self, interaction: Interaction, button: ui.Button) -> None:
        pass

    @classmethod
    def continued(cls, bot: Bot, interaction: Interaction, obj: "TeamManagement") -> "TeamManagement":
        new = cls(bot, interaction)
        new.members = obj.members
        new.number = obj.number
        return new

    async def embed(self) -> Embed:
        """Generates team management board as ``Embed``."""
        title = await self.title.translate(self.locale)
        title = title.format(len(self.members))

        description = ""
        if self.members != []:
            func: Callable[[Member], str] = lambda member: f"**{member.name}**#{member.discriminator}"
            description = "・" + "\n・".join(list(map(func, self.members)))

        embed = Embed(title=title, description=description, color=CONFIG.COLOR)
        text = await self.footer.translate(self.locale)
        embed.set_footer(text=text.format(self.number), icon_url=self.bot.user.avatar.url)
        return embed


class YesButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()

        self._Tlabel = _T({
            Locale.american_english: "Yes",
            Locale.british_english: "Yes",
            Locale.japanese: "はい",
            Locale.taiwan_chinese: "是",
        })
        self.style = ButtonStyle.green

    async def callback(self, interaction: Interaction) -> None:
        self.view.disable()
        self.view.value = True
        await interaction.response.edit_message(view=self.view)
        return

class NoButton(ui.Button):
    def __init__(self) -> None:
        super().__init__()

        self._Tlabel = _T({
            Locale.american_english: "No",
            Locale.british_english: "No",
            Locale.japanese: "いいえ",
            Locale.taiwan_chinese: "否",
        })
        self.style = ButtonStyle.red

    async def callback(self, interaction: Interaction) -> None:
        self.view.disable()
        self.view.value = False
        await interaction.response.edit_message(view=self.view)
        return

class Confirm(ViewBase):
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
        self.add_item(YesButton())
        self.add_item(NoButton())

class TeamColor(tuple[int, str], Enum):
    BLUE = (0x0000ff, PATH.TEAM_BLUE)
    RED = (0xFF0000, PATH.TEAM_RED)
    WHITE = (0xFFFFFF, PATH.TEAM_WHITE)

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
        # initialises attributes
        self.members: set = set(members)
        self.number: int = number
        self.files: list[File] = []
        self.embeds: list[Embed] = []
        self.length: int = len(members)
        # runs team division
        self.run()

    def run(self) -> None:
        for _ in range(self.length//(2*self.number)):
            self.prepare(self.generate_team(), TeamColor.BLUE)
            self.prepare(self.generate_team(), TeamColor.RED)
        if len(self.members) != 0:
            self.prepare(list(self.members), TeamColor.WHITE)
        return

    def generate_team(self) -> list[str]:
        """Generates team."""
        output: list[str] = sample(self.members, self.number)
        self.members ^= set(output)
        return output

    def prepare(self, members: list[str], color: TeamColor) -> None:
        """Prepares discord ``Embed``s and ``File``s."""
        file = f"{hash(members[0])}.png"
        embed = Embed(color=int(color))
        embed.set_author(name="　".join(members), icon_url=f"attachment://{file}")
        self.files.append(File(str(color), file))
        self.embeds.append(embed)
        return
