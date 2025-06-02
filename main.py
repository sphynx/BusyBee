import os
from pathlib import Path

from discord import Intents
from dotenv import load_dotenv

from bot import BusyBee

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = Intents.default()
    intents.message_content = True

    # Create a directory for storing the bots data
    path = Path("data")
    path.mkdir(parents=True, exist_ok=True)

    client = BusyBee(intents=intents, command_prefix="$")
    client.run(TOKEN)


