# MinesweeperForDiscord
take a fully revealed board from https://davidnhill.github.io/JSMinesweeper/index.html and put it into this thing

## example input and output
### input
```python
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

    # Test data - purposefully formatted poorly to test parsing
    board_string = (
        " \n \n\t \t9x9x23 \t 3F323F200 \n\n\n FFF4FF311 \n   \t 4FF4F32F1"
        + "\t\t\t\tF32212343 "
        + "121102FFF 12F223F42 F32F2F221 F2112222F 110001F21"
    )

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
```
### output
![image](https://github.com/user-attachments/assets/b2aaf7fb-4cb4-4530-b151-91f752aa8ce7) ![image](https://github.com/user-attachments/assets/958d2ffc-feeb-49fc-b52d-10d14391e0e8)

```
[Minesweeper Print Tool]
Board is 9x9 with 23 mines.
There are 23 flags placed and 0 unmarked.
3F323F200
FFF4FF311
4FF4F32F1
F32212343
121102FFF
12F223F42
F32F2F221
F2112222F
110001F21
[Print for Discord]
## Minesweeper!
9 by 9, 23 mines. Good luck!
||:three:||||:boom:||||:three:||||:two:||||:three:||||:boom:||||:two:||||:blue_square:||||:blue_square:||
||:boom:||||:boom:||||:boom:||||:four:||||:boom:||||:boom:||||:three:||||:one:||||:one:||
||:four:||||:boom:||||:boom:||||:four:||||:boom:||||:three:||||:two:||||:boom:||||:one:||
||:boom:||||:three:||||:two:||||:two:||||:one:||||:two:||||:three:||||:four:||||:three:||
||:one:||||:two:||||:one:||||:one:||||:blue_square:||||:two:||||:boom:||||:boom:||||:boom:||
||:one:||||:two:||||:boom:||||:two:||||:two:||||:three:||||:boom:||||:four:||||:two:||
||:boom:||||:three:||||:two:||||:boom:||||:two:||||:boom:||||:two:||||:two:||||:one:||
||:boom:||||:two:||||:one:||||:one:||||:two:||||:two:||||:two:||||:two:||||:boom:||
||:one:||||:one:||||:blue_square:||||:blue_square:||:blue_square::one::triangular_flag_on_post:||:two:||||:one:||
1 mine revealed already, 22 to go!
```
