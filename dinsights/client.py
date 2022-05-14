# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Optional

from discord import (
    Activity,
    ActivityType,
    BaseActivity,
    Client,
    CustomActivity,
    Game,
    Guild,
    Intents,
    Member,
    Message,
    Spotify,
    StageChannel,
    Status,
    Streaming,
    TextChannel,
    VoiceChannel,
    VoiceState,
)
from discord.abc import GuildChannel
from loguru import logger


def _find_channel(member: Member, channel_name: str) -> Optional[TextChannel]:
    """メンバーインスタンスから指定したチャンネル名のインスタンスを取得する

    Args:
        member (Member): メンバーインスタンス
        channel_name (str): 取得したいTextChannelインスタンスのチャンネル名

    Returns:
        Optional[TextChannel]: 指定したチャンネル名のインスタンス
        見つからない場合はNoneを返す
    """
    member_guild: Guild = member.guild
    guild_channel: list[GuildChannel] = member_guild.channels
    talk_channels: list[TextChannel] = list(filter(lambda x: isinstance(x, TextChannel), guild_channel))

    talk_channel: Optional[TextChannel] = None
    for channel in talk_channels:
        if str(channel) == channel_name:
            talk_channel = channel
            break

    logger.debug(f"{talk_channel=}")
    return talk_channel


def _is_joining_in_voice_channel(member: Member) -> bool:
    """メンバーがボイスチャンネルに参加しているか

    Args:
        member (Member): ボイスチャンネルに参加しているか確認するメンバーインスタンス

    Returns:
        bool: True=ボイスチャンネルに参加している、False=参加していない
    """
    return member.voice is not None


async def _tweet_to_talk_channel(talk_channel: Optional[TextChannel], message: Optional[str]) -> None:
    """指定したTextChannelにメッセージを送信する

    Args:
        talk_channel (Optional[TextChannel]): 送信したいTextChannelインスタンス
        message (str): 送信するメッセージ
    """
    if talk_channel is None:
        return
    if message is None:
        return
    if len(message) == 0:
        return

    logger.info(f'tweets to "{message}" to {talk_channel.name} at {talk_channel.guild.name}')
    await talk_channel.send(message)


def _extract_name_from_activity(activity: Optional[BaseActivity]) -> str:
    """BaseActivityインスタンスからアクティビティ名を取得する

    Args:
        activity (Optional[BaseActivity]): アクティビティ名を取得したいBaseActivityインスタンス

    Returns:
        str: アクティビティ名
    """
    activity_name: str = "None"
    if (
        activity is not None
        and isinstance(activity, (Activity, Game, Streaming, CustomActivity))
        and activity.name is not None
    ):
        activity_name = activity.name

    return activity_name


def _check_change_status(name: str, before: Status, after: Status) -> Optional[str]:
    """前後のメンバーステータスから変更をチェックする

    Args:
        name (str): チェックするメンバーの名前
        before (Status): 変更前ステータス
        after (Status): 変更後ステータス

    Returns:
        Optional[str]: 変更メッセージ Noneは変更なし
    """
    if before == after:
        return None

    message: str = f"{name} is change status. {before} -> {after}"

    logger.info(message)
    return message


def _check_change_activity(
    name: str, before: Optional[BaseActivity | Spotify], after: Optional[BaseActivity | Spotify]
) -> Optional[str]:
    """前後のメンバーアクティビティから変更をチェックする

    Args:
        name (str): チェックするメンバーの名前
        before (Optional[BaseActivity  |  Spotify]): 変更前のアクティビティ
        after (Optional[BaseActivity  |  Spotify]): 変更後のアクティビティ

    Returns:
        Optional[str]: 変更メッセージ Noneは変更なし
    """
    if before == after:
        return None
    if (
        before is not None
        and after is not None
        and before.name is not None
        and after.name is not None
        and before.name == after.name
    ):
        return None

    if isinstance(before, Spotify) or isinstance(after, Spotify):
        return None

    before_activity_name: str = _extract_name_from_activity(before)
    after_activity_name: str = _extract_name_from_activity(after)

    message: str = f"{name} is change activity. {before_activity_name} -> {after_activity_name}"
    return message


class InsightsClient(Client):
    def __init__(self, *, intents: Intents, talk_channel: str, dev_mode: bool = False, version: str) -> None:
        super().__init__(intents=intents)
        self.talk_channel: str = talk_channel
        self.dev_mode: bool = dev_mode
        self.version = version

    async def on_ready(self) -> None:
        logger.info(f"we have logged in as {self.user}. version={self.version}")

        if self.dev_mode:
            logger.info("Launch in development mode")
            dev_activity: Activity = Activity(
                name="Develop Mode",
                type=ActivityType.playing,
                state="In dev mode",
                details="launch in development mode",
            )
            await self.change_presence(activity=dev_activity)

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
        logger.debug(repr(before))
        logger.debug(repr(after))

        if not _is_joining_in_voice_channel(after):
            return

        talk_channel: Optional[TextChannel] = _find_channel(after, self.talk_channel)

        message: list[Optional[str]] = [
            _check_change_status(after.display_name, before.status, after.status),
            _check_change_activity(after.display_name, before.activity, after.activity),
        ]

        await _tweet_to_talk_channel(talk_channel, "\n".join(filter(None, message)))

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

        if message == "":
            return

        await _tweet_to_talk_channel(talk_channel, message)
