import os

from discord import Intents
from dotenv import load_dotenv

from bot import BusyBee

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = Intents.default()
    intents.message_content = True

    client = BusyBee(intents=intents, command_prefix="$")
    client.run(TOKEN)
