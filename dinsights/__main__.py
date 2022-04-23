# -*- coding: utf-8 -*-

from discord import Intents

from dinsights import __version__
from dinsights.client import InsightsClient
from dinsights.load_token import TOKEN


def run_client() -> None:
    intents: Intents = Intents.default()
    intents.presences = True
    intents.members = True
    intents.messages = True
    intents.guilds = True
    intents.voice_states = True

    client: InsightsClient = InsightsClient(intents=intents, talk_channel="game-activities", version=__version__)

    client.run(TOKEN)


if __name__ == "__main__":
    run_client()
