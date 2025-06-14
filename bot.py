from discord.ext.commands import Bot

from endgame import Endgame
from slow_games import LichessSlowGamesChecker


class BusyBee(Bot):

    async def on_ready(self):
        # Add all cogs here:
        await self.add_cog(LichessSlowGamesChecker(self))
        await self.add_cog(Endgame(self))

        print(f'Logged on as {self.user}')

