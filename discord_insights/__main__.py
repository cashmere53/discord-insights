# -*- coding: utf-8 -*-

from discord import Intents

from discord_insights.client import InsightsClient
from discord_insights.load_token import TOKEN


def run_client() -> None:
    intents: Intents = Intents.default()
    intents.presences = True
    intents.members = True
    intents.messages = True
    intents.guilds = True
    intents.voice_states = True

    client: InsightsClient = InsightsClient(intents=intents)

    client.run(TOKEN)


if __name__ == "__main__":
    run_client()
