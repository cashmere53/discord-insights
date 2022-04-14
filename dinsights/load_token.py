# -*- coding: utf-8 -*-

from pathlib import Path


def load_token(filepath: Path) -> str:
    token: str = ""
    with filepath.open("r") as fp:
        token = list(fp)[0]

    return token


TOKEN: str = load_token(Path("./token.txt"))
