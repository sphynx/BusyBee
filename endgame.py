import re
from pathlib import Path

from urllib.parse import quote
from chess import Board
from discord.ext import commands
from discord.ext.commands import Cog, command

from discord.ext.commands.errors import MissingRequiredArgument

URL_PATTERN = "https://chess-endgame-trainer.mooo.com/fen/FEN_STRING/TARGET"
FENS_FILE = "data/endgames.txt"

class Endgame(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = Path(FENS_FILE)

    @command()
    async def endgame(self, ctx, *, arg: str):
        """
        Opens an position specified by FEN to play in the Endgame Trainer app
        :param arg: FEN [white/black] [win/draw]
        """

        orig_arg = arg

        # Let's try to parse the arguments
        # We support: mandatory FEN + optional arguments: "black", "white", "win", "draw"
        white = black = win = draw = False
        errors = []

        if "white" in arg.lower():
            white = True

        if "black" in arg.lower():
            black = True

        if "win" in arg.lower():
            win = True

        if "draw" in arg.lower():
            draw = True

        if white and black:
            errors.append("You can specify either 'white' or 'black', not both")

        if win and draw:
            errors.append("You can specify either 'win' or 'draw', not both")

        keywords = ["white", "black", "win", "draw"]
        for kw in keywords:
            arg = re.sub(kw, "", arg, flags=re.IGNORECASE)

        # Now we should be left with pure FEN
        fen = arg.strip()

        try:
            # Validate the FEN using `chess` package:
            _ = Board(fen=fen)
        except ValueError as e:
            errors.append(f"You have to specify a valid FEN of the position: {e}")

        if errors:
            errors_msg = '. '.join(errors)
            msg = f"There was a problem with your command: {errors_msg}"
        else:
            url = URL_PATTERN
            url = url.replace("FEN_STRING", fen)

            if draw:
                url = url.replace("TARGET", "draw")
            else:
                url = url.replace("/TARGET", "")

            if white:
                url += "?player=w"
            elif black:
                url += "?player=b"

            # To properly encode spaces in FEN:
            quoted_url = quote(url, safe=":/?=")

            self.log_url(quoted_url)
            msg = f"Please play your position in Endgame Trainer: {quoted_url}"

        print(msg)
        await ctx.send(msg)

    @endgame.error
    async def info_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send('endgame command requires FEN argument, '
                           'for example: `$endgame R7/6k1/P5p1/5p1p/5P1P/r5P1/5K2/8 b - - 0 1`')
        else:
            await ctx.send(f'There was an error with the command: {str(error)}')


    def log_url(self, url: str) -> None:
        with self.data_file.open("a") as f:
            f.write(f"{url}\n")
