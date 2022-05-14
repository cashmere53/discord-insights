# -*- coding: utf-8 -*-

__version__ = "0.2.2"

from dinsights.client import InsightsClient
from dinsights.load_token import TOKEN, load_token

__all__ = [
    "InsightsClient",
    "TOKEN",
    "load_token",
]
