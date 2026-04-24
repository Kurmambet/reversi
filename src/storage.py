import json
from pathlib import Path

from src.core import Game, get_valid_moves

SAVE_FILE = Path("savegame.json")


# def save_game(game: Game) -> None:
#     """Сохраняет матрицу доски и текущий ход в JSON-файл."""
#     data = {
#         "board": game.board,  # list[list[int]], 8x8
#         "current_player": game.current_player,  # int: 1 (BLACK) или 2 (WHITE)
#     }
#     SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_game(game: Game) -> None:
    """Сохраняет матрицу доски и текущий ход в JSON-файл."""
    # сериализация вручную чтобы выглядело нормально
    board_lines = ["  [" + ", ".join(map(str, row)) + "]" for row in game.board]
    board_str = "[\n" + ",\n".join(board_lines) + "\n  ]"

    result = (
        f'{{\n  "board": {board_str},\n  "current_player": {game.current_player}\n}}'
    )
    SAVE_FILE.write_text(result, encoding="utf-8")


def load_game(game: Game) -> bool:
    """
    Загружает состояние из файла в переданный объект игры.
    Возвращает True при успехе, False если файл не найден или повреждён.
    """
    if not SAVE_FILE.exists():
        return False
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        game.board = data["board"]
        game.current_player = data["current_player"]
        game.valid_moves = get_valid_moves(game.board, game.current_player)
        return True
    except (KeyError, json.JSONDecodeError):
        return False
