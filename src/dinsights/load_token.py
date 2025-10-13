from pathlib import Path

from loguru import logger

# ロードするTokenファイルの順番
LOADING_FILE_ORDER: list[str] = [
    # 1 docker secrets
    "/run/secrets/token",
    # 2 local
    "./token.txt",
]

_token: str | None = None


def _find_token_file(search_paths: list[str] | None = None) -> Path:
    """指定された順番でファイル存在の有無をチェックし、最初に見つかったファイルパスを返す.

    Args:
        search_paths: 検索するパスのリスト。Noneの場合はLOADING_FILE_ORDERを使用

    Raises:
        FileNotFoundError: 記載のパスをすべてチェックしたが、存在しなかった

    Returns:
        Path: 最初に見つかったファイル
    """
    if search_paths is None:
        search_paths = LOADING_FILE_ORDER

    ret_path: Path | None = None
    for path_str in search_paths:
        path = Path(path_str).resolve()
        if not path.exists():
            continue
        if not path.is_file():
            continue

        ret_path = path
        break

    if ret_path is None:
        msg = "token file is not found."
        raise FileNotFoundError(msg)

    return ret_path


def load_token(filepath: str | Path) -> str:
    """指定されたパスの中身をトークンとしてロードする.

    Args:
        filepath (str | Path): トークンファイル

    Raises:
        FileNotFoundError: ファイルが存在しない
        PermissionError: ファイルの読み取り権限がない
        ValueError: トークンが空

    Returns:
        str: Token
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    filepath = filepath.resolve()

    logger.debug(f"load token. {filepath!s}")

    try:
        token: str = filepath.read_text(encoding="utf-8").rstrip("\r\n")
    except FileNotFoundError:
        logger.error(f"Token file not found: {filepath}")
        raise
    except PermissionError:
        logger.error(f"Permission denied when reading token file: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Failed to read token file: {filepath}, error: {e}")
        raise

    if not token or not token.strip():
        msg = f"Token file is empty: {filepath}"
        logger.error(msg)
        raise ValueError(msg)

    logger.info("Success to load token")
    return token


def reset_token_cache() -> None:
    """キャッシュされたトークンをリセットする."""
    global _token  # noqa: PLW0603
    _token = None


def get_token() -> str:
    """キャッシュされたトークンを取得する。キャッシュがない場合は自動検索してロードする.

    Returns:
        str: Token
    """
    global _token  # noqa: PLW0603

    if _token is not None:
        return _token

    _token = load_token(_find_token_file())
    return _token
