"""load_token.pyのテストコード."""

from pathlib import Path

import pytest

import dinsights.load_token
from dinsights.load_token import (
    _find_token_file,
    get_token,
    load_token,
    reset_token_cache,
)


class TestLoadToken:
    """load_token関数のテスト."""

    def test_load_token_success(self, tmp_path: Path) -> None:
        """正常なトークンファイルの読み込み."""
        token_file = tmp_path / "token.txt"
        expected_token = "test_token_12345"
        token_file.write_text(expected_token, encoding="utf-8")

        result = load_token(token_file)
        assert result == expected_token

    def test_load_token_with_newline(self, tmp_path: Path) -> None:
        """改行を含むトークンファイルの読み込み(改行は削除される)."""
        token_file = tmp_path / "token.txt"
        expected_token = "test_token_with_newline"
        token_file.write_text(f"{expected_token}\n", encoding="utf-8")

        result = load_token(token_file)
        assert result == expected_token

    def test_load_token_with_crlf(self, tmp_path: Path) -> None:
        """CRLF改行を含むトークンファイルの読み込み(改行は削除される)."""
        token_file = tmp_path / "token.txt"
        expected_token = "test_token_windows"
        token_file.write_text(f"{expected_token}\r\n", encoding="utf-8")

        result = load_token(token_file)
        assert result == expected_token

    def test_load_token_from_string_path(self, tmp_path: Path) -> None:
        """文字列パスからのトークン読み込み."""
        token_file = tmp_path / "token.txt"
        expected_token = "test_token_string_path"
        token_file.write_text(expected_token, encoding="utf-8")

        result = load_token(str(token_file))
        assert result == expected_token

    def test_load_token_file_not_found(self, tmp_path: Path) -> None:
        """存在しないファイルの場合はFileNotFoundErrorが発生."""
        non_existent_file = tmp_path / "non_existent.txt"

        with pytest.raises(FileNotFoundError):
            load_token(non_existent_file)

    def test_load_token_empty_file(self, tmp_path: Path) -> None:
        """空のファイルの場合はValueErrorが発生."""
        token_file = tmp_path / "empty_token.txt"
        token_file.write_text("", encoding="utf-8")

        with pytest.raises(ValueError, match="Token file is empty"):
            load_token(token_file)

    def test_load_token_whitespace_only(self, tmp_path: Path) -> None:
        """空白文字のみのファイルの場合はValueErrorが発生."""
        token_file = tmp_path / "whitespace_token.txt"
        token_file.write_text("   \n\n  ", encoding="utf-8")

        with pytest.raises(ValueError, match="Token file is empty"):
            load_token(token_file)

    def test_load_token_with_spaces(self, tmp_path: Path) -> None:
        """前後にスペースがあるトークン(改行のみ削除、スペースは保持)."""
        token_file = tmp_path / "token_with_spaces.txt"
        expected_token = "  token_with_spaces  "
        token_file.write_text(f"{expected_token}\n", encoding="utf-8")

        result = load_token(token_file)
        assert result == expected_token

    def test_load_token_permission_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """読み取り権限がない場合はPermissionErrorが発生."""
        token_file = tmp_path / "token.txt"
        token_file.write_text("test_token", encoding="utf-8")

        def mock_read_text(*args, **kwargs):  # noqa: ARG001
            msg = "Permission denied"
            raise PermissionError(msg)

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        with pytest.raises(PermissionError, match="Permission denied"):
            load_token(token_file)

    def test_load_token_unexpected_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """予期しないエラーが発生した場合も適切に処理される."""
        token_file = tmp_path / "token.txt"
        token_file.write_text("test_token", encoding="utf-8")

        def mock_read_text(*args, **kwargs):  # noqa: ARG001
            msg = "Unexpected I/O error"
            raise OSError(msg)

        monkeypatch.setattr(Path, "read_text", mock_read_text)

        with pytest.raises(OSError, match="Unexpected I/O error"):
            load_token(token_file)


class TestFindTokenFile:
    """_find_token_file関数のテスト."""

    def test_find_token_file_first_exists(self, tmp_path: Path) -> None:
        """最初のファイルが存在する場合."""
        token_file1 = tmp_path / "token1.txt"
        token_file2 = tmp_path / "token2.txt"
        token_file1.write_text("token1", encoding="utf-8")
        token_file2.write_text("token2", encoding="utf-8")

        search_paths = [str(token_file1), str(token_file2)]
        result = _find_token_file(search_paths)

        assert result.resolve() == token_file1.resolve()

    def test_find_token_file_second_exists(self, tmp_path: Path) -> None:
        """最初のファイルが存在せず、2番目が存在する場合."""
        token_file1 = tmp_path / "token1.txt"
        token_file2 = tmp_path / "token2.txt"
        token_file2.write_text("token2", encoding="utf-8")

        search_paths = [str(token_file1), str(token_file2)]
        result = _find_token_file(search_paths)

        assert result.resolve() == token_file2.resolve()

    def test_find_token_file_none_exists(self, tmp_path: Path) -> None:
        """すべてのファイルが存在しない場合はFileNotFoundErrorが発生."""
        token_file1 = tmp_path / "token1.txt"
        token_file2 = tmp_path / "token2.txt"

        search_paths = [str(token_file1), str(token_file2)]

        with pytest.raises(FileNotFoundError, match="token file is not found"):
            _find_token_file(search_paths)

    def test_find_token_file_directory_exists(self, tmp_path: Path) -> None:
        """ディレクトリが存在してもファイルでない場合はスキップ."""
        token_dir = tmp_path / "token_dir"
        token_dir.mkdir()
        token_file = tmp_path / "token.txt"
        token_file.write_text("token", encoding="utf-8")

        search_paths = [str(token_dir), str(token_file)]
        result = _find_token_file(search_paths)

        assert result.resolve() == token_file.resolve()

    def test_find_token_file_empty_list(self) -> None:
        """検索パスが空の場合はFileNotFoundErrorが発生."""
        search_paths: list[str] = []

        with pytest.raises(FileNotFoundError, match="token file is not found"):
            _find_token_file(search_paths)


class TestGetToken:
    """get_token関数のテスト."""

    def setup_method(self) -> None:
        """各テストの前にキャッシュをリセット."""
        reset_token_cache()

    def test_get_token_with_cache(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """キャッシュが有効な場合、2回目の呼び出しでキャッシュが使用される."""
        token_file = tmp_path / "token.txt"
        expected_token = "cached_token"
        token_file.write_text(expected_token, encoding="utf-8")

        # LOADING_FILE_ORDERをモンキーパッチ
        monkeypatch.setattr(
            dinsights.load_token,
            "LOADING_FILE_ORDER",
            [str(token_file)],
        )

        # 1回目の呼び出し
        result1 = get_token()
        assert result1 == expected_token

        # ファイルを変更
        token_file.write_text("new_token", encoding="utf-8")

        # 2回目の呼び出し - キャッシュが使われるため、古いトークンが返る
        result2 = get_token()
        assert result2 == expected_token

    def test_get_token_reset_cache(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """キャッシュをリセットすると新しいトークンが読み込まれる."""
        token_file = tmp_path / "token.txt"
        token_file.write_text("first_token", encoding="utf-8")

        # LOADING_FILE_ORDERをモンキーパッチ
        monkeypatch.setattr(
            dinsights.load_token,
            "LOADING_FILE_ORDER",
            [str(token_file)],
        )

        # 1回目の呼び出し
        result1 = get_token()
        assert result1 == "first_token"

        # ファイルを変更してキャッシュをリセット
        token_file.write_text("second_token", encoding="utf-8")
        reset_token_cache()

        # 2回目の呼び出し - キャッシュがリセットされたため、新しいトークンが返る
        result2 = get_token()
        assert result2 == "second_token"

    def test_get_token_no_file_found(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """トークンファイルが見つからない場合はFileNotFoundErrorが発生."""
        non_existent = str(tmp_path / "non_existent.txt")
        monkeypatch.setattr(
            dinsights.load_token,
            "LOADING_FILE_ORDER",
            [non_existent],
        )

        with pytest.raises(FileNotFoundError):
            get_token()


class TestResetTokenCache:
    """reset_token_cache関数のテスト."""

    def test_reset_token_cache(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """キャッシュリセット機能のテスト."""
        token_file = tmp_path / "token.txt"
        token_file.write_text("initial_token", encoding="utf-8")

        monkeypatch.setattr(
            dinsights.load_token,
            "LOADING_FILE_ORDER",
            [str(token_file)],
        )

        # トークンを取得してキャッシュ
        get_token()

        # キャッシュをリセット
        reset_token_cache()

        # キャッシュがリセットされたことを確認 - 次回呼び出し時に再読み込みされる
        token_file.write_text("new_token", encoding="utf-8")
        result = get_token()
        assert result == "new_token"
