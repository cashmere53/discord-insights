"""client.pyのテストコード."""

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from discord import Activity, ActivityType, CustomActivity, Game, Intents, Spotify, Status, Streaming, TextChannel

from dinsights.client import (
    InsightsClient,
    _check_change_activity,
    _check_change_status,
    _check_change_voice_status,
    _extract_name_from_activity,
    _find_channel,
    _is_joining_in_voice_channel,
    _tweet_to_talk_channel,
)

pytest_plugins = ("pytest_asyncio",)

if TYPE_CHECKING:
    from discord import Member, VoiceState


class TestFindChannel:
    """_find_channel関数のテスト."""

    def test_find_channel_success(self) -> None:
        """指定したチャンネル名が見つかる場合."""
        # モックの作成 - spec=TextChannelでisinstance()をパスさせる
        mock_text_channel = MagicMock(spec=TextChannel)
        mock_text_channel.__str__ = Mock(return_value="general")

        mock_voice_channel = Mock()
        mock_voice_channel.__class__.__name__ = "VoiceChannel"

        mock_guild = Mock()
        mock_guild.channels = [mock_text_channel, mock_voice_channel]

        mock_member = Mock()
        mock_member.guild = mock_guild

        # テスト実行
        result = _find_channel(mock_member, "general")

        # 検証
        assert result == mock_text_channel

    def test_find_channel_not_found(self) -> None:
        """指定したチャンネル名が見つからない場合."""
        mock_text_channel = MagicMock(spec=TextChannel)
        mock_text_channel.__str__ = Mock(return_value="random")

        mock_guild = Mock()
        mock_guild.channels = [mock_text_channel]

        mock_member = Mock()
        mock_member.guild = mock_guild

        result = _find_channel(mock_member, "general")

        assert result is None

    def test_find_channel_no_text_channels(self) -> None:
        """TextChannelが存在しない場合."""
        mock_voice_channel = Mock()
        mock_voice_channel.__class__.__name__ = "VoiceChannel"

        mock_guild = Mock()
        mock_guild.channels = [mock_voice_channel]

        mock_member = Mock()
        mock_member.guild = mock_guild

        result = _find_channel(mock_member, "general")

        assert result is None

    def test_find_channel_multiple_channels(self) -> None:
        """複数のTextChannelがある場合、最初にマッチしたものを返す."""
        mock_channel1 = MagicMock(spec=TextChannel)
        mock_channel1.__str__ = Mock(return_value="general")

        mock_channel2 = MagicMock(spec=TextChannel)
        mock_channel2.__str__ = Mock(return_value="general")

        mock_guild = Mock()
        mock_guild.channels = [mock_channel1, mock_channel2]

        mock_member = Mock()
        mock_member.guild = mock_guild

        result = _find_channel(mock_member, "general")

        assert result == mock_channel1


class TestIsJoiningInVoiceChannel:
    """_is_joining_in_voice_channel関数のテスト."""

    def test_is_joining_when_in_voice_channel(self) -> None:
        """ボイスチャンネルに参加している場合."""
        mock_member = Mock()
        mock_member.voice = Mock()
        mock_member.voice.afk = False

        result = _is_joining_in_voice_channel(mock_member)

        assert result is True

    def test_is_not_joining_when_voice_is_none(self) -> None:
        """voiceがNoneの場合 - 参加していない."""
        mock_member = Mock()
        mock_member.voice = None

        result = _is_joining_in_voice_channel(mock_member)

        assert result is False

    def test_is_not_joining_when_afk(self) -> None:
        """AFKチャンネルにいる場合."""
        mock_member = Mock()
        mock_member.voice = Mock()
        mock_member.voice.afk = True

        result = _is_joining_in_voice_channel(mock_member)

        assert result is False


class TestTweetToTalkChannel:
    """_tweet_to_talk_channel関数のテスト."""

    @pytest.mark.asyncio
    async def test_tweet_success(self) -> None:
        """正常にメッセージを送信できる場合."""
        mock_channel = AsyncMock()
        mock_channel.name = "general"
        mock_channel.guild.name = "Test Server"

        message = "Hello, World!"

        await _tweet_to_talk_channel(mock_channel, message)

        mock_channel.send.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_tweet_when_channel_is_none(self) -> None:
        """チャンネルがNoneの場合、送信しない."""
        mock_channel = None
        message = "Hello"

        await _tweet_to_talk_channel(mock_channel, message)

        # 例外が発生しないことを確認

    @pytest.mark.asyncio
    async def test_tweet_when_message_is_none(self) -> None:
        """メッセージがNoneの場合、送信しない."""
        mock_channel = AsyncMock()

        await _tweet_to_talk_channel(mock_channel, None)

        mock_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_tweet_when_message_is_empty(self) -> None:
        """メッセージが空文字列の場合、送信しない."""
        mock_channel = AsyncMock()

        await _tweet_to_talk_channel(mock_channel, "")

        mock_channel.send.assert_not_called()


class TestExtractNameFromActivity:
    """_extract_name_from_activity関数のテスト."""

    def test_extract_name_from_activity(self) -> None:
        """Activityから名前を取得."""
        activity = Activity(name="Playing Game", type=ActivityType.playing)

        result = _extract_name_from_activity(activity)

        assert result == "Playing Game"

    def test_extract_name_from_game(self) -> None:
        """Gameから名前を取得."""
        game = Game(name="Minecraft")

        result = _extract_name_from_activity(game)

        assert result == "Minecraft"

    def test_extract_name_from_streaming(self) -> None:
        """Streamingから名前を取得."""
        streaming = Streaming(name="Streaming on Twitch", url="https://twitch.tv/test")

        result = _extract_name_from_activity(streaming)

        assert result == "Streaming on Twitch"

    def test_extract_name_from_custom_activity(self) -> None:
        """CustomActivityから名前を取得."""
        custom = CustomActivity(name="Custom Status")

        result = _extract_name_from_activity(custom)

        assert result == "Custom Status"

    def test_extract_name_when_activity_is_none(self) -> None:
        """アクティビティがNoneの場合."""
        result = _extract_name_from_activity(None)

        assert result == "None"

    def test_extract_name_when_name_is_none(self) -> None:
        """アクティビティのnameがNoneの場合."""
        activity = Activity(name=None, type=ActivityType.playing)

        result = _extract_name_from_activity(activity)

        assert result == "None"

    def test_extract_name_from_spotify(self) -> None:
        """Spotifyアクティビティの場合 - サポート外."""
        spotify = Mock(spec=Spotify)
        spotify.name = "Listening to Spotify"

        result = _extract_name_from_activity(spotify)

        # SpotifyはBaseActivityを継承していないため、"None"を返す
        assert result == "None"


class TestCheckChangeStatus:
    """_check_change_status関数のテスト."""

    def test_status_changed(self) -> None:
        """ステータスが変更された場合."""
        result = _check_change_status("TestUser", Status.online, Status.idle)

        assert result is not None
        assert "TestUser" in result
        assert "online" in result
        assert "idle" in result

    def test_status_not_changed(self) -> None:
        """ステータスが変更されていない場合."""
        result = _check_change_status("TestUser", Status.online, Status.online)

        assert result is None

    def test_status_change_to_offline(self) -> None:
        """オフラインに変更された場合."""
        result = _check_change_status("TestUser", Status.online, Status.offline)

        assert result is not None
        assert "offline" in result


class TestCheckChangeActivity:
    """_check_change_activity関数のテスト."""

    def test_activity_changed(self) -> None:
        """アクティビティが変更された場合."""
        before = Activity(name="Game1", type=ActivityType.playing)
        after = Activity(name="Game2", type=ActivityType.playing)

        result = _check_change_activity("TestUser", before, after)

        assert result is not None
        assert "TestUser" in result
        assert "Game1" in result
        assert "Game2" in result

    def test_activity_not_changed(self) -> None:
        """アクティビティが変更されていない場合."""
        before = Activity(name="Game1", type=ActivityType.playing)
        after = Activity(name="Game1", type=ActivityType.playing)

        result = _check_change_activity("TestUser", before, after)

        assert result is None

    def test_activity_changed_from_none(self) -> None:
        """アクティビティがNoneから何かに変更された場合."""
        after = Game(name="Minecraft")

        result = _check_change_activity("TestUser", None, after)

        assert result is not None
        assert "None" in result
        assert "Minecraft" in result

    def test_activity_changed_to_none(self) -> None:
        """アクティビティが何かからNoneに変更された場合."""
        before = Game(name="Minecraft")

        result = _check_change_activity("TestUser", before, None)

        assert result is not None
        assert "Minecraft" in result
        assert "None" in result

    def test_activity_spotify_before(self) -> None:
        """変更前がSpotifyの場合はNoneを返す."""
        spotify = Mock(spec=Spotify)
        after = Game(name="Game")

        result = _check_change_activity("TestUser", spotify, after)

        assert result is None

    def test_activity_spotify_after(self) -> None:
        """変更後がSpotifyの場合はNoneを返す."""
        before = Game(name="Game")
        spotify = Mock(spec=Spotify)

        result = _check_change_activity("TestUser", before, spotify)

        assert result is None

    def test_activity_both_none(self) -> None:
        """両方Noneの場合."""
        result = _check_change_activity("TestUser", None, None)

        assert result is None


class TestCheckChangeVoiceStatus:
    """_check_change_voice_status関数のテスト."""

    def test_joins_voice_channel(self) -> None:
        """ボイスチャンネルに参加した場合."""
        mock_before: VoiceState = Mock()
        mock_before.channel = None

        mock_after: VoiceState = Mock()
        mock_after.channel = Mock()
        mock_after.channel.name = "General Voice"

        result = _check_change_voice_status("TestUser", mock_before, mock_after)

        assert result is not None
        assert "joins" in result
        assert "TestUser" in result
        assert "General Voice" in result

    def test_lefts_voice_channel(self) -> None:
        """ボイスチャンネルから退出した場合."""
        mock_before: VoiceState = Mock()
        mock_before.channel = Mock()
        mock_before.channel.name = "General Voice"

        mock_after: VoiceState = Mock()
        mock_after.channel = None

        result = _check_change_voice_status("TestUser", mock_before, mock_after)

        assert result is not None
        assert "lefts" in result
        assert "TestUser" in result
        assert "General Voice" in result

    def test_no_change_in_voice_channel(self) -> None:
        """ボイスチャンネルの変更がない場合."""
        mock_channel = Mock()
        mock_channel.name = "General Voice"

        mock_before: VoiceState = Mock()
        mock_before.channel = mock_channel

        mock_after: VoiceState = Mock()
        mock_after.channel = mock_channel

        result = _check_change_voice_status("TestUser", mock_before, mock_after)

        assert result is None

    def test_both_none(self) -> None:
        """両方Noneの場合."""
        mock_before: VoiceState = Mock()
        mock_before.channel = None

        mock_after: VoiceState = Mock()
        mock_after.channel = None

        result = _check_change_voice_status("TestUser", mock_before, mock_after)

        assert result is None


class TestInsightsClient:
    """InsightsClientクラスのテスト."""

    def test_client_initialization(self) -> None:
        """クライアントの初期化."""
        intents = Intents.default()

        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            dev_mode=True,
            version="1.0.0",
        )

        assert client.talk_channel == "general"
        assert client.dev_mode is True
        assert client.version == "1.0.0"

    def test_client_initialization_defaults(self) -> None:
        """クライアントの初期化 - デフォルト値."""
        intents = Intents.default()

        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        assert client.talk_channel == "general"
        assert client.dev_mode is False
        assert client.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_on_ready_normal_mode(self) -> None:
        """on_readyイベント - 通常モード."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            dev_mode=False,
            version="1.0.0",
        )

        mock_user = Mock()
        mock_user.name = "TestBot"

        # Bot.user is a read-only property, so we patch the class property
        with (
            patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)),
            patch.object(client, "change_presence", new=AsyncMock()) as mock_presence,
        ):
            await client.on_ready()

            # 通常モードではpresence変更は呼ばれない
            mock_presence.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_ready_dev_mode(self) -> None:
        """on_readyイベント - 開発モード."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            dev_mode=True,
            version="1.0.0",
        )

        mock_user = Mock()
        mock_user.name = "TestBot"

        with (
            patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)),
            patch.object(client, "change_presence", new=AsyncMock()) as mock_presence,
        ):
            await client.on_ready()

            # 開発モードではpresence変更が呼ばれる
            mock_presence.assert_called_once()
            call_args = mock_presence.call_args
            activity = call_args.kwargs["activity"]
            assert activity.name == "Develop Mode"

    @pytest.mark.asyncio
    async def test_on_message_hello(self) -> None:
        """on_messageイベント - $helloコマンド."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_user = Mock()

        with patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)):
            mock_message = AsyncMock()
            mock_message.author = Mock()
            mock_message.author.bot = False
            mock_message.content = "$hello"
            mock_message.channel.send = AsyncMock()

            await client.on_message(mock_message)

            mock_message.channel.send.assert_called_once_with("Hello!")

    @pytest.mark.asyncio
    async def test_on_message_bye(self) -> None:
        """on_messageイベント - $byeコマンド."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_user = Mock()

        with patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)):
            mock_message = AsyncMock()
            mock_message.author = Mock()
            mock_message.author.bot = False
            mock_message.author.__str__ = Mock(return_value="TestUser")
            mock_message.content = "$bye"
            mock_message.channel.send = AsyncMock()

            await client.on_message(mock_message)

            mock_message.channel.send.assert_called_once()
            call_args = mock_message.channel.send.call_args[0][0]
            assert "bye!" in call_args

    @pytest.mark.asyncio
    async def test_on_message_from_self(self) -> None:
        """自分自身のメッセージは無視する."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_user = Mock()

        with patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)):
            mock_message = AsyncMock()
            mock_message.author = mock_user
            mock_message.content = "$hello"
            mock_message.channel.send = AsyncMock()

            await client.on_message(mock_message)

            mock_message.channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_message_from_bot(self) -> None:
        """他のボットからのメッセージは無視する."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_user = Mock()

        with patch.object(type(client), "user", new_callable=lambda: property(lambda _: mock_user)):
            mock_message = AsyncMock()
            mock_message.author = Mock()
            mock_message.author.bot = True
            mock_message.content = "$hello"
            mock_message.channel.send = AsyncMock()

            await client.on_message(mock_message)

            mock_message.channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_presence_update_not_in_voice(self) -> None:
        """ボイスチャンネルにいない場合は何もしない."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_before: Member = Mock()
        mock_after: Member = Mock()
        mock_after.voice = None

        with patch("dinsights.client._tweet_to_talk_channel") as mock_tweet:
            await client.on_presence_update(mock_before, mock_after)

            mock_tweet.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_voice_state_update_with_afk(self) -> None:
        """AFKチャンネルの場合は何もしない."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_member: Member = Mock()
        mock_before: VoiceState = Mock()
        mock_before.afk = True
        mock_after: VoiceState = Mock()
        mock_after.afk = False

        with patch("dinsights.client._tweet_to_talk_channel") as mock_tweet:
            await client.on_voice_state_update(mock_member, mock_before, mock_after)

            mock_tweet.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_presence_update_with_status_change(self) -> None:
        """ボイスチャンネルにいる状態でステータスが変更された場合."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_before: Member = Mock()
        mock_before.status = Status.offline
        mock_before.activity = None

        mock_after: Member = Mock()
        mock_after.status = Status.online
        mock_after.activity = None
        mock_after.display_name = "TestUser"
        mock_after.voice = Mock()
        mock_after.voice.afk = False

        mock_channel = MagicMock(spec=TextChannel)
        mock_channel.send = AsyncMock()

        with (
            patch("dinsights.client._find_channel", return_value=mock_channel),
            patch("dinsights.client._tweet_to_talk_channel", new=AsyncMock()) as mock_tweet,
        ):
            await client.on_presence_update(mock_before, mock_after)

            mock_tweet.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_voice_state_update_with_join(self) -> None:
        """ボイスチャンネルに参加した場合."""
        intents = Intents.default()
        client = InsightsClient(
            intents=intents,
            talk_channel="general",
            version="1.0.0",
        )

        mock_member: Member = Mock()
        mock_member.display_name = "TestUser"

        mock_before: VoiceState = Mock()
        mock_before.afk = False
        mock_before.channel = None

        mock_after: VoiceState = Mock()
        mock_after.afk = False
        mock_after.channel = Mock()
        mock_after.channel.name = "Voice Channel"

        mock_channel = MagicMock(spec=TextChannel)
        mock_channel.send = AsyncMock()

        with (
            patch("dinsights.client._find_channel", return_value=mock_channel),
            patch("dinsights.client._tweet_to_talk_channel", new=AsyncMock()) as mock_tweet,
        ):
            await client.on_voice_state_update(mock_member, mock_before, mock_after)

            mock_tweet.assert_called_once()
