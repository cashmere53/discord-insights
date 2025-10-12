from __future__ import annotations

from discord import (
    Activity,
    ActivityType,
    BaseActivity,
    CustomActivity,
    Game,
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
from discord.ext.commands import Bot
from loguru import logger


def _find_channel(member: Member, channel_name: str) -> TextChannel | None:
    """メンバーインスタンスから指定したチャンネル名のインスタンスを取得する.

    Args:
        member (Member): メンバーインスタンス
        channel_name (str): 取得したいTextChannelインスタンスのチャンネル名

    Returns:
        Optional[TextChannel]: 指定したチャンネル名のインスタンス
        見つからない場合はNoneを返す
    """
    guild_channels = member.guild.channels
    talk_channels = [ch for ch in guild_channels if isinstance(ch, TextChannel)]

    talk_channel: TextChannel | None = None
    for channel in talk_channels:
        if str(channel) == channel_name:
            talk_channel = channel
            break

    logger.debug(f"{talk_channel=}")
    return talk_channel


def _is_joining_in_voice_channel(member: Member) -> bool:
    """メンバーがボイスチャンネルに参加しているか.

    Args:
        member (Member): ボイスチャンネルに参加しているか確認するメンバーインスタンス

    Returns:
        bool: True=ボイスチャンネルに参加している、False=参加していない
    """
    if member.voice is None:
        return False

    return not member.voice.afk


async def _tweet_to_talk_channel(talk_channel: TextChannel | None, message: str | None) -> None:
    """指定したTextChannelにメッセージを送信する.

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


def _extract_name_from_activity(activity: BaseActivity | None) -> str:
    """BaseActivityインスタンスからアクティビティ名を取得する.

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


def _check_change_status(name: str, before: Status, after: Status) -> str | None:
    """前後のメンバーステータスから変更をチェックする.

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
    name: str, before: BaseActivity | Spotify | None, after: BaseActivity | Spotify | None
) -> str | None:
    """前後のメンバーアクティビティから変更をチェックする.

    Args:
        name (str): チェックするメンバーの名前
        before (Optional[BaseActivity  |  Spotify]): 変更前のアクティビティ
        after (Optional[BaseActivity  |  Spotify]): 変更後のアクティビティ

    Returns:
        Optional[str]: 変更メッセージ Noneは変更なし
    """
    if before == after:
        return None

    # Spotifyは別途処理
    if isinstance(before, Spotify) or isinstance(after, Spotify):
        return None

    # BaseActivityの場合、nameがない可能性があるため、_extract_name_from_activityで取得した名前で比較
    before_name = _extract_name_from_activity(before)
    after_name = _extract_name_from_activity(after)

    if before_name == after_name:
        return None

    message: str = f"{name} is change activity. {before_name} -> {after_name}"
    return message


def _check_change_voice_status(
    name: str,
    before: VoiceState,
    after: VoiceState,
) -> str | None:
    before_channel: VoiceChannel | StageChannel | None = before.channel
    after_channel: VoiceChannel | StageChannel | None = after.channel

    message: str = ""

    if before_channel is None and after_channel is not None:
        message = f"{name} joins Voice Channel at {after_channel.name}"

    if before_channel is not None and after_channel is None:
        message = f"{name} lefts Voice Channel at {before_channel.name}"

    if message == "":
        return None

    return message


class InsightsClient(Bot):
    def __init__(self, *, intents: Intents, talk_channel: str, dev_mode: bool = False, version: str) -> None:
        super().__init__("!dis", intents=intents)
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
        logger.debug(message)

        if message.author == self.user:
            return

        if message.author.bot:
            return

        if message.content.startswith("$hello"):
            await message.channel.send("Hello!")

        if message.content.startswith("$bye"):
            await message.channel.send(f"bye! {message.author}")

    async def on_presence_update(self, before: Member, after: Member) -> None:
        logger.info("someone presences is updated.")
        logger.debug(repr(before))
        logger.debug(repr(after))

        if not _is_joining_in_voice_channel(after):
            return

        talk_channel: TextChannel | None = _find_channel(after, self.talk_channel)

        message: list[str | None] = [
            _check_change_status(after.display_name, before.status, after.status),
            _check_change_activity(after.display_name, before.activity, after.activity),
        ]

        await _tweet_to_talk_channel(talk_channel, "\n".join(filter(None, message)))

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState) -> None:
        logger.debug(f"{member=}")
        logger.debug(f"{before=}")
        logger.debug(f"{after=}")

        logger.debug(f"check afk: {before.afk=} {after.afk=}")
        if before.afk or after.afk:
            return

        talk_channel = _find_channel(member, self.talk_channel)
        message: str | None = _check_change_voice_status(member.display_name, before, after)

        await _tweet_to_talk_channel(talk_channel, message)
