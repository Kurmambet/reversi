# ─────────────────────────── КОНСТАНТЫ ────────────────────────────────────────

BOARD_SIZE = 8
CELL_SIZE = 70
EMPTY, BLACK, WHITE = 0, 1, 2
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

# ─────────────────────────── ЧИСТАЯ ЛОГИКА ────────────────────────────────────


def initial_board() -> list[list[int]]:
    """
    [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 2, 1, 0, 0, 0],
    [0, 0, 0, 1, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
    ]
    """

    board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    board[3][3] = WHITE  # d4
    board[3][4] = BLACK  # e4
    board[4][3] = BLACK  # d5
    board[4][4] = WHITE  # e5
    return board


def opponent(player: int) -> int:
    return WHITE if player == BLACK else BLACK


def get_flips(board: list, row: int, col: int, player: int) -> list[tuple]:
    """Возвращает список фишек, которые перевернутся при ходе (row, col)."""
    if board[row][col] != EMPTY:
        return []

    opp = opponent(player)
    result = []  # какие фишки надо перевернуть

    for dr, dc in DIRECTIONS:
        line = []  # в текущем направлении
        r, c = row + dr, col + dc  # первый шаг в выбранном направлении
        while (0 <= r < BOARD_SIZE) and (0 <= c < BOARD_SIZE) and (board[r][c] == opp):
            line.append((r, c))
            r += dr
            c += dc
        if (
            line
            and (0 <= r < BOARD_SIZE)
            and (0 <= c < BOARD_SIZE)
            and (board[r][c] == player)  # на которой остановились - наша фишка
        ):
            result.extend(line)
    return result  # по 8 направлениям из текущего места


def get_valid_moves(board: list, player: int) -> list[tuple]:
    """список клеток (r, c), куда текущему игроку разрешено походить"""
    return [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if get_flips(board, r, c, player)  # [] = False, да да, в питоне так работает
    ]


def apply_move(board: list, row: int, col: int, player: int) -> None:
    flips = get_flips(board, row, col, player)  # какие фишки перевернутся
    board[row][col] = player  # фишку игрока на указанную клетку
    for r, c in flips:
        board[r][c] = player


def count_pieces(board: list) -> tuple[int, int]:
    """текущий счет ч:б"""
    # sum воспринимает True как 1
    black = sum(
        board[r][c] == BLACK for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
    )
    white = sum(
        board[r][c] == WHITE for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
    )
    return black, white


# ─────────────────────────── СОСТОЯНИЕ ИГРЫ ───────────────────────────────────


# State Machine
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = initial_board()
        self.current_player = BLACK
        self.valid_moves = get_valid_moves(self.board, BLACK)
        self.game_over = False

    def make_move(self, row: int, col: int) -> bool:
        if self.game_over or (row, col) not in self.valid_moves:
            return False
        apply_move(self.board, row, col, self.current_player)
        self._advance_turn()
        return True

    def _advance_turn(self):
        next_p = opponent(self.current_player)
        moves = get_valid_moves(self.board, next_p)

        if moves:  # обычный случай — ход переходит
            self.current_player = next_p
            self.valid_moves = moves
            return

        moves = get_valid_moves(self.board, self.current_player)
        if moves:  # пас — текущий ходит снова
            self.valid_moves = moves
            return

        self.game_over = True  # оба без ходов — конец
        self.valid_moves = []  # чтобы с экрана пропали серые точки-подсказки
