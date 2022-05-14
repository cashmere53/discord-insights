# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Optional

from loguru import logger

# ロードするTokenファイルの順番
LOADING_FILE_ORDER: list[str] = [
    # 1 docker secrets
    "/run/secrets/token",
    # 2 local
    "./token.txt",
]


def _find_token_file() -> Path:
    """
    LOADING_FILE_ORDERに記載されいてる順番でファイル存在の有無をチェックし、最初に見つかったファイルパスを返す

    Raises:
        FileNotFoundError: LOADING_FILE_ORDER記載のパスをすべてチェックしたが、存在しなかった

    Returns:
        Path: 最初に見つかったファイル
    """
    ret_path: Optional[Path] = None
    for path in map(Path, LOADING_FILE_ORDER):
        path = path.resolve()
        if not path.exists():
            continue
        if not path.is_file():
            continue

        ret_path = path
        break

    if ret_path is None:
        raise FileNotFoundError("token file is not found.")

    return ret_path


def load_token(filepath: str | Path) -> str:
    """
    指定されたパスの中身をトークンとしてをロードする

    Args:
        filepath (str | Path): トークンファイル

    Returns:
        str: Token
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    filepath = filepath.resolve()

    logger.info(f"load token. {str(filepath)}")

    # token: str = ""
    # with filepath.open("r") as fp:
    #     token = list(fp)[0]
    token: str = filepath.read_text(encoding="utf-8").rstrip("\r\n")

    logger.info("Success to load token")
    return token


TOKEN: str = load_token(_find_token_file())
