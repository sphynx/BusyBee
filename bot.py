from discord.ext.commands import Bot

from slow_games import LichessSlowGamesChecker


class BusyBee(Bot):
    async def on_ready(self):
        await self.add_cog(LichessSlowGamesChecker(self))

        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send(f"Hello, {message.author}!")

