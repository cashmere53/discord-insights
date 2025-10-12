# load_token.py テストドキュメント

## テストの概要

`test_load_token.py`は`src/dinsights/load_token.py`モジュールの包括的なテストスイートです。

**テストカバレッジ: 100%** 🎉

## テスト実行方法

```powershell
# すべてのテストを実行
uv run pytest tests/test_load_token.py -v

# カバレッジ測定付きで実行
uv run pytest tests/test_load_token.py --cov=dinsights.load_token --cov-report=term-missing -v

# HTMLカバレッジレポートを生成
uv run pytest tests/test_load_token.py --cov=dinsights.load_token --cov-report=html

# 特定のテストクラスを実行
uv run pytest tests/test_load_token.py::TestLoadToken -v

# 特定のテストケースを実行
uv run pytest tests/test_load_token.py::TestLoadToken::test_load_token_success -v
```

## テストケース一覧

### TestLoadToken クラス

`load_token`関数の動作をテストします。

1. **test_load_token_success**: 正常なトークンファイルの読み込み
2. **test_load_token_with_newline**: 改行を含むトークンファイル（改行は削除される）
3. **test_load_token_with_crlf**: CRLF改行を含むトークンファイル（改行は削除される）
4. **test_load_token_from_string_path**: 文字列パスからのトークン読み込み
5. **test_load_token_file_not_found**: 存在しないファイルでFileNotFoundErrorが発生
6. **test_load_token_empty_file**: 空ファイルでValueErrorが発生
7. **test_load_token_whitespace_only**: 空白文字のみのファイルでValueErrorが発生
8. **test_load_token_with_spaces**: 前後にスペースがあるトークン（スペースは保持される）
9. **test_load_token_permission_error**: 読み取り権限がない場合はPermissionErrorが発生 ⭐ NEW
10. **test_load_token_unexpected_error**: 予期しないエラーが発生した場合も適切に処理される ⭐ NEW

### TestFindTokenFile クラス
`_find_token_file`関数の動作をテストします。

1. **test_find_token_file_first_exists**: 最初のファイルが存在する場合
2. **test_find_token_file_second_exists**: 最初のファイルが存在せず、2番目が存在する場合
3. **test_find_token_file_none_exists**: すべてのファイルが存在しない場合にFileNotFoundErrorが発生
4. **test_find_token_file_directory_exists**: ディレクトリが存在してもスキップされる
5. **test_find_token_file_empty_list**: 検索パスが空の場合にFileNotFoundErrorが発生

### TestGetToken クラス
`get_token`関数のキャッシュ機能をテストします。

1. **test_get_token_with_cache**: キャッシュが有効な場合、2回目の呼び出しでキャッシュが使用される
2. **test_get_token_reset_cache**: キャッシュをリセットすると新しいトークンが読み込まれる
3. **test_get_token_no_file_found**: トークンファイルが見つからない場合にFileNotFoundErrorが発生

### TestResetTokenCache クラス
`reset_token_cache`関数の動作をテストします。

1. **test_reset_token_cache**: キャッシュリセット機能の動作確認

## 実装の変更点

テストを実装するために、以下の変更を`load_token.py`に加えました:

### 1. `_find_token_file`関数の改善
```python
def _find_token_file(search_paths: list[str] | None = None) -> Path:
```
- `search_paths`パラメータを追加し、テスト時にカスタムパスを指定可能に

### 2. `reset_token_cache`関数の追加
```python
def reset_token_cache() -> None:
    """キャッシュされたトークンをリセットする."""
```
- キャッシュを明示的にクリアする関数を追加

### 3. エラーハンドリングの強化
- 空白文字のみのトークンファイルも検出可能に（`if not token or not token.strip():`）
- 各種エラーケースで適切なログを出力

## カバレッジ統計

```text
Name                          Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------
src\dinsights\load_token.py      49      0     16      0   100%
---------------------------------------------------------------
TOTAL                            49      0     16      0   100%
```

### カバレッジの内訳

- **ステートメントカバレッジ**: 49/49 (100%)
- **ブランチカバレッジ**: 16/16 (100%)
- **全テストケース**: 19個すべて成功 ✅

すべてのコードパス、エラーハンドリング、条件分岐が完全にテストされています。

## テストの特徴

- **一時ディレクトリの使用**: `pytest`の`tmp_path`フィクスチャを使用してテスト用の一時ファイルを作成
- **モンキーパッチ**: `monkeypatch`を使用して`LOADING_FILE_ORDER`や`Path.read_text`をテスト用に差し替え
- **包括的なカバレッジ**: 正常系、異常系、エッジケース、エラーハンドリングをすべてカバー
- **独立性**: 各テストは独立して実行可能
- **モック**: `PermissionError`や一般的な例外をシミュレートしてエラーパスもテスト

## トラブルシューティング

### テストが失敗する場合

1. **Pythonバージョン**: Python 3.10以上が必要
2. **依存関係**: `uv run`を使用して依存関係が自動的にインストールされます
3. **キャッシュの問題**: テスト前に`reset_token_cache()`が呼ばれることを確認

### pytest が見つからない場合

```powershell
# uvを使用してテストを実行
uv run pytest tests/test_load_token.py -v
```
