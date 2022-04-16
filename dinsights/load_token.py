# -*- coding: utf-8 -*-

from pathlib import Path

from loguru import logger


def load_token(filepath: str | Path) -> str:
    if isinstance(filepath, str):
        filepath = Path(filepath)
    filepath = filepath.resolve()

    logger.info(f"load token. {filepath=}")

    token: str = ""
    with filepath.open("r") as fp:
        token = list(fp)[0]

    logger.info("Success to load token")
    return token


TOKEN: str = load_token(Path("./token.txt"))
