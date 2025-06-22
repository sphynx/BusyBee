import chess
import chess.svg
import cairosvg
import discord
from discord.ext.commands import Cog, command, MissingRequiredArgument

IMG_TMP_PATH = "data/fen_image.png"

class FenImageGenerator(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def fen(self, ctx, *, arg: str):
        """
        Generates an image specified by FEN string
        :param arg: FEN
        """

        try:
            board = chess.Board(fen=arg)
            board_to_png(board, IMG_TMP_PATH)
            file = discord.File(IMG_TMP_PATH)
            await ctx.send("Here is your position:", file=file)
        except ValueError as e:
            error = f"You have to specify a valid FEN of the position: {e}"
            await ctx.send(error)
        except Exception as e:
            await ctx.send(f"Failed to send position image: {e}")

    @fen.error
    async def info_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send('`fen` command requires FEN argument, '
                           'for example: `$fen R7/6k1/P5p1/5p1p/5P1P/r5P1/5K2/8 b - - 0 1`')
        else:
            await ctx.send(f'There was an error with the command: {str(error)}')


def fen_to_png(fen: str, png_path: str):
    board_to_png(chess.Board(fen), png_path)


def board_to_png(board: chess.Board, png_path: str):
    # Generate SVG representation of the board
    svg_data = chess.svg.board(
        board=board,
        colors={
            "margin": "#EDC9AF",
            "coord": "#8B5A2B"
        },
        size=600,
    )

    # Convert SVG to PNG
    cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=png_path)

    print(f"PNG image saved to {png_path}")

if __name__ == '__main__':
    # Example FEN string (starting position)
    fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    fen_to_png(fen_string, "chess_position4.png")