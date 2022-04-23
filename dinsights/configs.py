# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import Optional


@dataclass
class Configs:
    devmode: bool
    talk_channel: str

    @classmethod
    def default(cls) -> Configs:
        return cls(devmode=False, talk_channel="game-activities")


def configure_from_environments(config: Configs) -> Configs:
    devmode: Optional[str] = getenv("DEVMODE")
    config.devmode = (devmode is not None) and (devmode.lower() in "yes true 1")

    talk_channel: Optional[str] = getenv("TALK_CHANNEL")
    if talk_channel is not None:
        config.talk_channel = talk_channel

    return config


configs: Configs = Configs.default()
configs = configure_from_environments(configs)
