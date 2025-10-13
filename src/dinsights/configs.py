from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Configs:
    devmode: bool = False
    talk_channel: str = ""
    verbose: int = 0

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


configs: Configs = Configs()
