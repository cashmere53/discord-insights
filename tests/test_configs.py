"""configs.pyのテストコード."""

from dinsights.configs import Configs, configs


class TestConfigs:
    """Configsクラスのテスト."""

    def test_configs_default_values(self) -> None:
        """デフォルト値が正しく設定されている."""
        config = Configs()

        assert config.devmode is False
        assert config.talk_channel == ""
        assert config.verbose == 0

    def test_configs_with_custom_values(self) -> None:
        """カスタム値で初期化できる."""
        expected_verbose = 2
        config = Configs(
            devmode=True,
            talk_channel="general",
            verbose=expected_verbose,
        )

        assert config.devmode is True
        assert config.talk_channel == "general"
        assert config.verbose == expected_verbose

    def test_log_level_devmode_enabled(self) -> None:
        """devmodeが有効な場合、log_levelはTRACEを返す."""
        config = Configs(devmode=True, verbose=0)
        assert config.log_level == "TRACE"

        # verboseの値に関わらずTRACEを返す
        config = Configs(devmode=True, verbose=1)
        assert config.log_level == "TRACE"

        config = Configs(devmode=True, verbose=2)
        assert config.log_level == "TRACE"

    def test_log_level_verbose_0(self) -> None:
        """verbose=0の場合、log_levelはINFOを返す."""
        config = Configs(devmode=False, verbose=0)
        assert config.log_level == "INFO"

    def test_log_level_verbose_1(self) -> None:
        """verbose=1の場合、log_levelはDEBUGを返す."""
        config = Configs(devmode=False, verbose=1)
        assert config.log_level == "DEBUG"

    def test_log_level_verbose_2_or_more(self) -> None:
        """verbose=2以上の場合、log_levelはTRACEを返す."""
        config = Configs(devmode=False, verbose=2)
        assert config.log_level == "TRACE"

        config = Configs(devmode=False, verbose=3)
        assert config.log_level == "TRACE"

        config = Configs(devmode=False, verbose=10)
        assert config.log_level == "TRACE"

    def test_log_level_negative_verbose(self) -> None:
        """負のverbose値は0として扱われる."""
        config = Configs(devmode=False, verbose=-1)
        # log_levelプロパティ内でmax(verbose, 0)が実行される
        assert config.log_level == "INFO"
        # verboseの値自体は変更されない - 内部で正規化されるだけ
        assert config.verbose == -1

        config = Configs(devmode=False, verbose=-5)
        assert config.log_level == "INFO"
        assert config.verbose == -5  # noqa: PLR2004

    def test_log_level_multiple_calls(self) -> None:
        """log_levelプロパティは複数回呼び出しても同じ結果を返す."""
        config = Configs(devmode=False, verbose=1)

        # 複数回呼び出し
        result1 = config.log_level
        result2 = config.log_level
        result3 = config.log_level

        assert result1 == "DEBUG"
        assert result2 == "DEBUG"
        assert result3 == "DEBUG"

    def test_configs_immutability_with_frozen(self) -> None:
        """dataclassとして値の変更が可能であることを確認."""
        config = Configs(verbose=0)
        assert config.verbose == 0

        # dataclassはデフォルトでmutableなので変更可能
        config.verbose = 1
        assert config.verbose == 1
        assert config.log_level == "DEBUG"

    def test_talk_channel_various_strings(self) -> None:
        """talk_channelに様々な文字列を設定できる."""
        config = Configs(talk_channel="general")
        assert config.talk_channel == "general"

        config = Configs(talk_channel="123456789")
        assert config.talk_channel == "123456789"

        config = Configs(talk_channel="日本語チャンネル")
        assert config.talk_channel == "日本語チャンネル"

        config = Configs(talk_channel="")
        assert config.talk_channel == ""

    def test_dataclass_equality(self) -> None:
        """同じ値を持つConfigsインスタンスは等しい."""
        config1 = Configs(devmode=True, talk_channel="test", verbose=1)
        config2 = Configs(devmode=True, talk_channel="test", verbose=1)
        config3 = Configs(devmode=False, talk_channel="test", verbose=1)

        assert config1 == config2
        assert config1 != config3

    def test_dataclass_repr(self) -> None:
        """Configsインスタンスの文字列表現が正しい."""
        config = Configs(devmode=True, talk_channel="general", verbose=2)
        repr_str = repr(config)

        assert "Configs" in repr_str
        assert "devmode=True" in repr_str
        assert "talk_channel='general'" in repr_str
        assert "verbose=2" in repr_str


class TestConfigsSingleton:
    """グローバルconfigsインスタンスのテスト."""

    def test_global_configs_exists(self) -> None:
        """グローバルconfigsインスタンスが存在する."""
        assert configs is not None
        assert isinstance(configs, Configs)

    def test_global_configs_default_values(self) -> None:
        """グローバルconfigsのデフォルト値を確認."""
        # デフォルト値を確認 - 他のテストで変更されている可能性があるため、リセット
        configs.devmode = False
        configs.talk_channel = ""
        configs.verbose = 0

        assert configs.devmode is False
        assert configs.talk_channel == ""
        assert configs.verbose == 0

    def test_global_configs_can_be_modified(self) -> None:
        """グローバルconfigsを変更できる."""
        # 元の値を保存
        original_devmode = configs.devmode
        original_channel = configs.talk_channel
        original_verbose = configs.verbose

        try:
            # 変更
            expected_verbose = 2
            configs.devmode = True
            configs.talk_channel = "test-channel"
            configs.verbose = expected_verbose

            assert configs.devmode is True
            assert configs.talk_channel == "test-channel"
            assert configs.verbose == expected_verbose
            assert configs.log_level == "TRACE"
        finally:
            # 元に戻す
            configs.devmode = original_devmode
            configs.talk_channel = original_channel
            configs.verbose = original_verbose


class TestLogLevelEdgeCases:
    """log_levelプロパティのエッジケースをテスト."""

    def test_log_level_boundary_values(self) -> None:
        """境界値でのlog_levelの動作を確認."""
        # verbose=0とverbose=1の境界
        config = Configs(devmode=False, verbose=0)
        assert config.log_level == "INFO"

        config.verbose = 1
        assert config.log_level == "DEBUG"

        # verbose=1とverbose=2の境界
        config.verbose = 1
        assert config.log_level == "DEBUG"

        config.verbose = 2
        assert config.log_level == "TRACE"

    def test_log_level_with_very_large_verbose(self) -> None:
        """非常に大きなverbose値でもTRACEを返す."""
        config = Configs(devmode=False, verbose=999999)
        assert config.log_level == "TRACE"

    def test_log_level_with_very_small_negative_verbose(self) -> None:
        """非常に小さな負のverbose値でもINFOを返す."""
        expected_verbose = -999999
        config = Configs(devmode=False, verbose=expected_verbose)
        assert config.log_level == "INFO"
        # verboseの値自体は変更されない
        assert config.verbose == expected_verbose

    def test_devmode_priority_over_verbose(self) -> None:
        """devmodeがverboseより優先されることを確認."""
        # devmode=Trueの場合、verboseの値に関わらずTRACE
        for verbose_value in [-10, -1, 0, 1, 2, 10, 100]:
            config = Configs(devmode=True, verbose=verbose_value)
            assert config.log_level == "TRACE", f"Failed for verbose={verbose_value}"
