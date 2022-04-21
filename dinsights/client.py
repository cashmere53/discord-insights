# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional

from discord import (
    BaseActivity,
    Client,
    Guild,
    Intents,
    Member,
    Message,
    Spotify,
    StageChannel,
    Status,
    TextChannel,
    VoiceChannel,
    VoiceState,
)
from discord.abc import GuildChannel
from loguru import logger


def _find_channel(member: Member, channel_name: str) -> Optional[TextChannel]:
    member_guild: Guild = member.guild
    guild_channel: list[GuildChannel] = member_guild.channels
    talk_channels: list[TextChannel] = list(filter(lambda x: isinstance(x, TextChannel), guild_channel))
 
    logger.debug(f"{talk_channels=}")
 
    talk_channel: Optional[TextChannel] = None
    for channel in talk_channels:
        if str(channel) == channel_name:
            talk_channel = channel
            break

    return talk_channel


def _is_joining_in_voice_channel(member: Member) -> bool:
    return member.voice is not None


async def _tweet_to_talk_channel(talk_channel: Optional[TextChannel], message: str) -> None:
    if talk_channel is None:
        return
    if len(message) == 0:
        return 

    message: str = f'"{message}"'
    guild: Guild = talk_channel.guild
    
    logger.info(f"tweets to {message} to {talk_channel.name} at {guild.name}")
    await talk_channel.send(message)


class InsightsClient(Client):
    def __init__(self, *, intents: Intents, talk_channel: str):
        super().__init__(intents=intents)
        self.talk_channel = talk_channel

    async def on_ready(self) -> None:
        logger.info("we have logged in as {0.user}".format(self))

    async def on_message(self, message: Message) -> None:
        logger.debug(f"{message}, type={type(message)}")

        if message.author == self.user:
            return

        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")

        if message.content.startswith("$bye"):
            await message.channel.send(f"bye! {message.author}")

    async def on_member_update(self, before: Member, after: Member) -> None:
        logger.info("someone presences is updated.")
        logger.info(repr(before))
        logger.info(repr(after))

        if not _is_joining_in_voice_channel(after):
            return

        talk_channel: Optional[TextChannel] = _find_channel(after, self.talk_channel)

        await self.check_change_status(after.display_name, before.status, after.status, talk_channel)
        await self.check_change_activity(after.display_name, before.activity, after.activity, talk_channel)

    async def check_change_status(
        self,
        name: str,
        before: Status,
        after: Status,
        talk_channel: Optional[TextChannel],
    ) -> None:
        if before == after:
            return

        message: str = f"{name} is change status. {before} -> {after}"

        logger.info(message)
        await _tweet_to_talk_channel(talk_channel, message)

    async def check_change_activity(
        self,
        name: str,
        before: Optional[BaseActivity | Spotify],
        after: Optional[BaseActivity | Spotify],
        talk_channel: Optional[TextChannel],
    ) -> None:
        if before == after:
            return
        if (
            before is not None
            and after is not None
            and before.name is not None
            and after.name is not None
            and before.name == after.name
        ):
            return

        logger.debug(f"{before=}")
        logger.debug(f"{after=}")

        if isinstance(before, Spotify) or isinstance(after, Spotify):
            return

        before_activity_name: str = "None"
        if before is not None:
            before_activity_name = before.name

        after_activity_name: str = "None"
        if after is not None:
            after_activity_name = after.name

        message: str = f"{name} is change activity. {before_activity_name} -> {after_activity_name}"

        await _tweet_to_talk_channel(talk_channel, message)

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        logger.debug(f"{member=}")
        logger.debug(f"{before=}")
        logger.debug(f"{after=}")

        talk_channel: TextChannel = _find_channel(member, self.talk_channel)

        await self.check_change_voice_status(member.display_name, before, after, talk_channel)

    async def check_change_voice_status(
        self,
        name: str,
        before: VoiceState,
        after: VoiceState,
        talk_channel: Optional[TextChannel] = None,
    ) -> None:
        before_channel: Optional[VoiceChannel | StageChannel] = before.channel
        after_channel: Optional[VoiceChannel | StageChannel] = after.channel

        message: str = ""

        if before_channel is None and after_channel is not None:
            message = f"{name} joins Voice Channel at {after_channel.name}"

        if before_channel is not None and after_channel is None:
            message = f"{name} lefts Voice Channel at {before_channel.name}"

        await _tweet_to_talk_channel(talk_channel, message)
