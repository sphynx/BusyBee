import os
from pathlib import Path

from discord.ext.commands import Cog, command
from discord.ext.tasks import loop

from lichess import LichessUserChecker
from users import Users

CHECK_PERIOD = 120  # seconds

POSTED_GAMES_FILE = "data/posted_games.csv"

class PostedGames:
    def __init__(self):
        self.data = set()
        self.data_file = Path(POSTED_GAMES_FILE)
        if self.data_file.exists():
            for line in self.data_file.read_text().split("\n"):
                if line:
                    self.data.add(line)

            print(f"Loaded {len(self.data)} posted games from DB")

    def add_game(self, game_id: str) -> None:
        self.data.add(game_id)
        self._append_game(game_id)

    def game_exists(self, game_id: str) -> bool:
        return game_id in self.data

    def _append_game(self, game_id: str) -> None:
        with self.data_file.open("a") as f:
            f.write(f"{game_id}\n")

    def dump_to_file(self) -> None:
        self.data_file.write_text("\n".join(self.data))


class LichessSlowGamesChecker(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_db = Users()

        self.user_checker = LichessUserChecker(self.users_db.lichess_usernames())
        self.games_posted = PostedGames()

        thread_id = int(os.getenv("SLOW_GAMES_THREAD_ID"))
        self.thread_to_post = self.bot.get_channel(thread_id)

        print(f"Starting SlowGamesChecker with interval: {CHECK_PERIOD}s")
        self.lichess_checker.start()

    @command()
    async def link(self, ctx, lichess: str):
        """Link your Discord to your Lichess username and monitor your slow games.
        :param lichess: Lichess username
        """
        discord_id = int(ctx.author.id)

        if self.user_checker.does_user_exist(lichess):
            added = self.users_db.add_user(lichess, discord_id)
            if added:
                self.user_checker.add_user(lichess)
                msg = f"Hi {ctx.author.name}! Your Lichess account '{lichess}' was linked to your Discord id: {discord_id}"
            else:
                msg = f"Hi {ctx.author.name}! Your Lichess account '{lichess}' is already in the database"
        else:
            msg = f"Hi {ctx.author.name}! Your Lichess account '{lichess}' does not seem to exist"

        print(msg)
        await ctx.send(msg)

    @command()
    async def follow(self, ctx, lichess: str):
        """Add any Lichess username to monitor their games.
        :param lichess: Lichess username
        """
        if self.user_checker.does_user_exist(lichess):
            added = self.users_db.add_user(lichess, None)
            if added:
                msg = f"Hi {ctx.author.name}! Lichess account '{lichess}' is now monitored"
                self.user_checker.add_user(lichess)
            else:
                msg = f"Hi {ctx.author.name}! Lichess account '{lichess}' is already in the database"
        else:
            msg = f"Hi {ctx.author.name}! Lichess account '{lichess}' does not seem to exist"

        print(msg)
        await ctx.send(msg)

    @command()
    async def list(self, ctx):
        """Lists all monitored Lichess usernames"""
        users = self.users_db.lichess_usernames()
        users_str = ', '.join(users)
        msg = f"{len(users)} users are monitored: {users_str}"

        print(msg)
        await ctx.send(msg)

    def cog_unload(self):
        self.lichess_checker.cancel()

    @loop(seconds=CHECK_PERIOD)
    async def lichess_checker(self):
        playing_users = self.user_checker.check_slow_games()

        for u in playing_users:
            if not self.games_posted.game_exists(u.game_id):
                lichess = u.name
                discord_id = self.users_db.lichess_to_discord(lichess)

                if discord_id is None:
                    name = lichess
                else:
                    name = f"<@{discord_id}> ({lichess})"

                msg = f"{name} is playing a slower game ({u.clock}) on Lichess, watch here: {u.game_url}"

                await self.thread_to_post.send(msg)
                print(msg)

                self.games_posted.add_game(u.game_id)
