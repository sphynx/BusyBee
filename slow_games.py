import os

from discord.ext import tasks
from discord.ext.commands import Cog

from lichess import LichessUserChecker

CHECK_PERIOD = 60 # seconds


class LichessSlowGamesChecker(Cog):
    def __init__(self, bot):
        self.bot = bot

        users = (
            "ChessIsHard101",
            "Hepatiaaa",
            "LordPuffington",
            "MatthewKCanada",
            "NicholasJSloan",
            "Phenomenon10",
            "ProfessorJaeger",
            "Squire_Western",
            "Zaxman",
            "danbock",
            "e_rider",
            "jdannan",
            "johngdon",
            "kiwiPete",
            "mvsguru",
            "rufusson_dufus",
            "sofaking83",
            "sphynx",
            "thechesslobster",
            "thinkmaster",
            "timpeverett",
        )

        self.user_checker = LichessUserChecker(users)
        self.games_posted = set()

        thread_id = os.getenv("SLOW_GAMES_THREAD_ID")
        self.thread_to_post = self.bot.get_channel(int(thread_id))

        self.lichess_checker.start()

    def cog_unload(self):
        self.lichess_checker.cancel()

    @tasks.loop(seconds=CHECK_PERIOD)
    async def lichess_checker(self):
        playing_users = self.user_checker.check_slow_games()

        for u in playing_users:
            if u.game_id not in self.games_posted:
                await self.thread_to_post.send(
                    f"{u.name} is playing a slower game ({u.clock}) on Lichess, watch here: {u.game_url}")
                print(f"{u.name} is playing a slower game {u.clock}, watch here: {u.game_url}")
                self.games_posted.add(u.game_id)
