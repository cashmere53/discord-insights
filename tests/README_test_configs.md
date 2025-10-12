# configs.py テストドキュメント

## テストの概要

`test_configs.py`は`src/dinsights/configs.py`モジュールの包括的なテストスイートです。

**テストカバレッジ: 100%** 🎉

## テスト実行方法

```powershell
# すべてのテストを実行
uv run pytest tests/test_configs.py -v

# カバレッジ測定付きで実行
uv run pytest tests/test_configs.py --cov=dinsights.configs --cov-report=term-missing -v

# HTMLカバレッジレポートを生成
uv run pytest tests/test_configs.py --cov=dinsights.configs --cov-report=html:htmlcov_configs

# 特定のテストクラスを実行
uv run pytest tests/test_configs.py::TestConfigs -v

# 特定のテストケースを実行
uv run pytest tests/test_configs.py::TestConfigs::test_configs_default_values -v
```

## カバレッジ統計

```text
Name                       Stmts   Miss Branch BrPart  Cover
------------------------------------------------------------
src\dinsights\configs.py      18      0      6      0   100%
------------------------------------------------------------
TOTAL                         18      0      6      0   100%
```

### カバレッジの内訳

- **ステートメントカバレッジ**: 18/18 (100%)
- **ブランチカバレッジ**: 6/6 (100%)
- **全テストケース**: 19個すべて成功 ✅

すべてのコードパス、条件分岐が完全にテストされています。

## テストケース一覧

### TestConfigs クラス

`Configs`クラスの基本機能をテストします。

1. **test_configs_default_values**: デフォルト値が正しく設定されている
2. **test_configs_with_custom_values**: カスタム値で初期化できる
3. **test_log_level_devmode_enabled**: devmodeが有効な場合、log_levelはTRACEを返す
4. **test_log_level_verbose_0**: verbose=0の場合、log_levelはINFOを返す
5. **test_log_level_verbose_1**: verbose=1の場合、log_levelはDEBUGを返す
6. **test_log_level_verbose_2_or_more**: verbose=2以上の場合、log_levelはTRACEを返す
7. **test_log_level_negative_verbose**: 負のverbose値でもlog_levelは正しく動作する
8. **test_log_level_multiple_calls**: log_levelプロパティは複数回呼び出しても一貫性がある
9. **test_configs_immutability_with_frozen**: dataclassとして値の変更が可能
10. **test_talk_channel_various_strings**: talk_channelに様々な文字列を設定できる
11. **test_dataclass_equality**: 同じ値を持つConfigsインスタンスは等しい
12. **test_dataclass_repr**: Configsインスタンスの文字列表現が正しい

### TestConfigsSingleton クラス

グローバル`configs`インスタンスの動作をテストします。

1. **test_global_configs_exists**: グローバルconfigsインスタンスが存在する
2. **test_global_configs_default_values**: グローバルconfigsのデフォルト値を確認
3. **test_global_configs_can_be_modified**: グローバルconfigsを変更できる

### TestLogLevelEdgeCases クラス

`log_level`プロパティのエッジケースをテストします。

1. **test_log_level_boundary_values**: 境界値でのlog_levelの動作を確認
2. **test_log_level_with_very_large_verbose**: 非常に大きなverbose値でもTRACEを返す
3. **test_log_level_with_very_small_negative_verbose**: 非常に小さな負のverbose値でもINFOを返す
4. **test_devmode_priority_over_verbose**: devmodeがverboseより優先される

## 実装の変更点

テストを実装する過程で、以下の改善を`configs.py`に加えました：

### log_levelプロパティの副作用を削除

**変更前**:

```python
@property
def log_level(self) -> str:
    if self.devmode:
        return "TRACE"

    self.verbose = max(self.verbose, 0)  # 副作用あり!

    if self.verbose == 0:
        return "INFO"
    if self.verbose == 1:
        return "DEBUG"

    return "TRACE"
```

**変更後**:

```python
@property
def log_level(self) -> str:
    if self.devmode:
        return "TRACE"

    # verboseの値を正規化 - 副作用なし
    normalized_verbose = max(self.verbose, 0)

    if normalized_verbose == 0:
        return "INFO"
    if normalized_verbose == 1:
        return "DEBUG"

    return "TRACE"
```

**改善点**:

- プロパティが状態を変更しないため、予測可能な動作になった
- 同じインスタンスに対して`log_level`を複数回呼び出しても、`verbose`の値が変わらない
- Pythonのベストプラクティスに準拠（プロパティは副作用を持つべきではない）

## テストの特徴

- **dataclass機能のテスト**: `__eq__`, `__repr__`などの自動生成メソッドをテスト
- **プロパティのテスト**: `log_level`プロパティの全ての条件分岐をカバー
- **境界値テスト**: verbose値の境界（0, 1, 2）や極端な値（負の大きな値、正の大きな値）をテスト
- **グローバルインスタンスのテスト**: シングルトンパターンのような使い方を確認
- **エッジケース**: devmodeの優先度、負の値の処理など

## log_level の仕様

`log_level`プロパティは以下のロジックで動作します：

| devmode | verbose | log_level |
|---------|---------|-----------|
| True    | any     | TRACE     |
| False   | < 0     | INFO      |
| False   | 0       | INFO      |
| False   | 1       | DEBUG     |
| False   | >= 2    | TRACE     |

**優先順位**: devmode > verbose

## トラブルシューティング

### テストが失敗する場合

1. **Pythonバージョン**: Python 3.10以上が必要
2. **依存関係**: `uv run`を使用して依存関係が自動的にインストールされます
3. **グローバルconfigsの状態**: テスト間でグローバル`configs`の状態が影響する可能性があるため、各テストで必要に応じてリセット

### カバレッジ測定時の注意

```powershell
# モジュール名で指定する
uv run pytest tests/test_configs.py --cov=dinsights.configs

# パスで指定すると失敗する可能性がある
# uv run pytest tests/test_configs.py --cov=src/dinsights/configs.py
```
