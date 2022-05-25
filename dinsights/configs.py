# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Configs:
    devmode: bool = False
    talk_channel: str = ""
    verbose: int = 0

    @property
    def log_level(self) -> str:
        if self.verbose < 0:
            self.verbose = 0

        if self.verbose == 0:
            return "INFO"
        if self.verbose == 1:
            return "DEBUG"

        return "TRACE"


configs: Configs = Configs()
