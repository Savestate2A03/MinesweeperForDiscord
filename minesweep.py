from enum import IntEnum, StrEnum
from typing import TypedDict
from collections.abc import Callable


class BoardPositionData(IntEnum):
    UNK = -1
    HEADER = 0
    TILES = 1


class BoardHeader(IntEnum):
    WIDTH = 0
    HEIGHT = 1
    MINES = 2


class BoardTile(StrEnum):
    # Base
    HIDDEN = "H"
    FLAG = "F"
    MINE = "M"
    # Numbers
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"


class BoardError(IntEnum):
    UNK = -1
    OK = 0
    BAD_ROWS = 1
    BAD_COLUMNS = 2
    BOARD_REPORTED_EMPTY = 3
    BOARD_CONTAINS_WRONG_TILE = 4
    BOARD_NOT_MATCHING_ROWS = 5
    BOARD_NOT_MATCHING_COLUMNS = 6
    BOARD_HAS_VARYING_LENGTH_ROWS = 7
    BOARD_STRING_EMPTY = 8
    BOARD_STRING_INVALID = 9
    BOARD_PROPERTY_TYPES_INCORRECT = 10
    BOARD_CONTAINS_NO_ROWS_DESPITE_REPORTEDLY_SO = 11
    BOARD_CONTAINS_NO_COLUMNS_DESPITE_REPORTEDLY_SO = 12


class BoardException(Exception):
    def __init__(self, message: str, code: BoardError = BoardError.UNK) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self) -> str:
        if not self.code:
            return f"Exception was raised, but the error code was {self.code}?"
        return f'Exception raised: {self.code.name}{
            ("\nMessage: " + self.message) if self.message else ""
        }'


class DiscordTranslate:
    def __init__(self, mapping: dict[BoardTile, str]) -> None:
        self.mapping = mapping

    def get(self, key: BoardTile) -> str:
        if key not in self.mapping:
            raise KeyError(f'Tile "{key}" is not valid!')
        return self.mapping[key]


class Coordinates(TypedDict):
    x: int
    y: int


class BoardMaker:
    def __init__(
        self,
        string: str,
        mapping: DiscordTranslate = None,
        hide_board: bool = False,
        force_shown: list[Coordinates] = None,
    ) -> None:
        self.string = string
        self.mapping = mapping
        self.hide_board = hide_board
        self.force_shown = force_shown or []

        # init defaults
        self.board: list[list[BoardTile]] = []
        self.columns = 0
        self.rows = 0
        self.mines = 0
        self.flags = 0
        self.hidden = 0

    def run(self) -> None:
        # process the board through parsing/validation steps before printing
        processes: list[Callable[[], BoardError]] = [
            self._parse,
            self._validate,
            self._print_board,
            self._print_message_for_discord,
        ]

        for process in processes:
            result = process()
            if result != BoardError.OK:
                raise BoardException(f"Error in {process.__name__}", result)

    def _parse(self) -> BoardError:
        # parse input string into board data
        try:
            data = self.string.split()
            if not data:
                return BoardError.BOARD_STRING_INVALID

            header = data[BoardPositionData.HEADER].split("x")
            if len(header) != len(BoardHeader):
                return BoardError.BOARD_STRING_INVALID

            # header data to int conversions
            self.columns = int(header[BoardHeader.WIDTH])
            self.rows = int(header[BoardHeader.HEIGHT])
            self.mines = int(header[BoardHeader.MINES])

            # reset counters
            self.flags = 0
            self.hidden = 0
            self.board.clear()

            # now start parsing tiles
            tiles_data = data[BoardPositionData.TILES :]
            for tiles_row in tiles_data:
                row: list[BoardTile] = []

                for tile_char in tiles_row:
                    if tile_char not in BoardTile:
                        return BoardError.BOARD_STRING_INVALID
                    tile = BoardTile(tile_char)
                    if tile == BoardTile.FLAG:
                        self.flags += 1
                    elif tile == BoardTile.HIDDEN:
                        self.hidden += 1
                    row.append(tile)

                # append the valid row to the board
                self.board.append(row)

            # made it out alive
            return BoardError.OK

        # made it out dead
        except (ValueError, IndexError):
            return BoardError.BOARD_STRING_INVALID

    def _validate(self) -> BoardError:
        # validate board state after parsing
        try:
            # type/value checks
            if not isinstance(self.string, str):
                return BoardError.BOARD_PROPERTY_TYPES_INCORRECT
            if not self.string.strip():
                return BoardError.BOARD_STRING_EMPTY
            if not isinstance(self.board, list):
                return BoardError.BOARD_PROPERTY_TYPES_INCORRECT

            # dimensional sanity
            if self.rows < 0:
                return BoardError.BAD_ROWS
            if self.rows == 0:
                return BoardError.BOARD_REPORTED_EMPTY
            if self.columns < 0:
                return BoardError.BAD_COLUMNS
            if self.columns == 0:
                return BoardError.BOARD_REPORTED_EMPTY

            # structure checks
            if len(self.board) == 0:
                return BoardError.BOARD_CONTAINS_NO_ROWS_DESPITE_REPORTEDLY_SO
            if len(self.board[0]) == 0:
                return BoardError.BOARD_CONTAINS_NO_COLUMNS_DESPITE_REPORTEDLY_SO

            actual_rows = len(self.board)
            actual_columns = len(self.board[0])

            if actual_rows != self.rows:
                return BoardError.BOARD_NOT_MATCHING_ROWS
            if actual_columns != self.columns:
                return BoardError.BOARD_NOT_MATCHING_COLUMNS

            # check each row for valid data
            for row in self.board:
                if not isinstance(row, list):
                    return BoardError.BOARD_PROPERTY_TYPES_INCORRECT
                if len(row) != actual_columns:
                    return BoardError.BOARD_HAS_VARYING_LENGTH_ROWS
                for tile in row:
                    if tile not in BoardTile:
                        return BoardError.BOARD_CONTAINS_WRONG_TILE

            # made it out alive again
            return BoardError.OK

        # you are so dead
        except Exception:
            return BoardError.UNK

    def _print_board(self) -> BoardError:
        # print a readable board
        print("[Minesweeper Print Tool]")
        print(f"Board is {self.columns}x{self.rows} with {self.mines} mines.")
        print(f"There are {self.flags} flags placed and {self.hidden} unmarked.")

        for row in self.board:
            line = "".join(str(tile) for tile in row)
            print(line)

        return BoardError.OK

    def _is_coordinate_shown(self, x: int, y: int) -> bool:
        # check if coordinate should be shown
        if not self.hide_board:
            return True

        return any(coord["x"] == x and coord["y"] == y for coord in self.force_shown)

    def _print_message_for_discord(self) -> BoardError:
        # print out for sending to ur discord friends
        if not self.mapping:
            return BoardError.OK

        print("[Print for Discord]")
        print("## Minesweeper!")
        print(f"{self.columns} by {self.rows}, {self.mines} mines. Good luck!")

        revealed_flags = 0
        for y, row in enumerate(self.board):
            line = ""
            for x, tile in enumerate(row):
                is_shown = self._is_coordinate_shown(x, y)
                wrap = "" if is_shown else "||"

                # hide flags as mines when not shown
                display_tile = tile
                if tile == BoardTile.FLAG and not is_shown:
                    display_tile = BoardTile.MINE
                elif tile == BoardTile.FLAG and is_shown:
                    revealed_flags += 1

                line += f"{wrap}:{self.mapping.get(display_tile)}:{wrap}"

            print(line)

        remaining_mines = self.mines - revealed_flags
        flag_text = "mine" if revealed_flags == 1 else "mines"
        print(
            f"{revealed_flags} {flag_text} revealed already, {remaining_mines} to go!"
        )

        return BoardError.OK


def main() -> None:
    # example usage of our fancy minesweeper board generator
    discord_mapping = DiscordTranslate(
        {
            BoardTile.HIDDEN: "blank",
            BoardTile.FLAG: "triangular_flag_on_post",
            BoardTile.ZERO: "blue_square",
            BoardTile.ONE: "one",
            BoardTile.TWO: "two",
            BoardTile.THREE: "three",
            BoardTile.FOUR: "four",
            BoardTile.FIVE: "five",
            BoardTile.SIX: "six",
            BoardTile.SEVEN: "seven",
            BoardTile.EIGHT: "eight",
            BoardTile.MINE: "boom",
        }
    )

    # purposefully formatted poorly to test parsing
    # click "download position" after fully revealing a board
    # on https://davidnhill.github.io/JSMinesweeper/index.html
    # and replace this text with that. can't have more than 99
    # emoji in a single message tho so 9x9 or 10x9 is as big as
    # it gets.
    board_string = (
        " \n \n\t \t9x9x23 \t 3F323F200 \n\n\n FFF4FF311 \n   \t 4FF4F32F1"
        + "\t\t\t\tF32212343 "
        + "121102FFF 12F223F42 F32F2F221 F2112222F 110001F21"
    )

    # you can show coordinates as the "starting point" for the game
    force_shown_coords: list[Coordinates] = [
        {"x": 4, "y": 8},
        {"x": 5, "y": 8},
        {"x": 6, "y": 8},
    ]

    try:
        board = BoardMaker(
            board_string,
            discord_mapping,
            hide_board=True,
            force_shown=force_shown_coords,
        )
        board.run()
    except BoardException as e:
        print(f"Board processing failed: {e}")


if __name__ == "__main__":
    main()
