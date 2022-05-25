# -*- coding: utf-8 -*-

import sys
from argparse import ArgumentParser

from discord import Intents
from loguru import logger

from dinsights import __version__
from dinsights.client import InsightsClient
from dinsights.configs import Configs
from dinsights.load_token import get_token


def cli_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument("-D", "--dev", action="store_true", help="launch development mode", dest="devmode")
    parser.add_argument("-t", "--talk-channel", help="talk channel name", metavar="CHANNEL_NAME", dest="talk_channel")
    parser.add_argument("-v", "--verbose", help="log verbosity", action="count", default=0, dest="verbose")
    parser.add_argument("--version", action="version", version=f"%(prog)s version{__version__}")

    return parser


def run_client() -> None:
    config: Configs = Configs()
    cli_parser().parse_args(namespace=config)

    logger.remove()
    logger.add(sys.stdout, level=config.log_level)

    logger.debug(config)

    token: str = get_token()

    # intents settings
    intents: Intents = Intents.default()
    intents.presences = True
    intents.members = True
    intents.messages = True
    intents.guilds = True
    intents.voice_states = True

    # make bot instance
    client: InsightsClient = InsightsClient(
        intents=intents,
        talk_channel=config.talk_channel,
        dev_mode=config.devmode,
        version=__version__,
    )

    client.run(token)


if __name__ == "__main__":
    run_client()
