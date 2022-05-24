# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import Optional

from loguru import logger


@dataclass
class Configs:
    devmode: bool = False
    talk_channel: str = ""
    verbose: int = 0


def configure_from_environments(config: Configs) -> Configs:
    devmode: Optional[str] = getenv("DEVMODE")
    logger.debug(f"environment: DEVMODE={devmode}")
    config.devmode = (devmode is not None) and (devmode.lower() in {"yes", "true", "1"})

    talk_channel: Optional[str] = getenv("TALK_CHANNEL")
    logger.debug(f"environment: TALK_CHANNEL={talk_channel}")
    if talk_channel is not None:
        config.talk_channel = talk_channel

    return config


configs: Configs = Configs()
configs = configure_from_environments(configs)
