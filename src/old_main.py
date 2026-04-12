import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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


# ─────────────────────────── ВИДЖЕТ ДОСКИ ─────────────────────────────────────


class BoardWidget(QWidget):
    cell_clicked = pyqtSignal(int, int)  # строка, столбец

    BOARD_COLOR = QColor("#2d7a2d")
    GRID_COLOR = QColor("#1a5c1a")
    HINT_COLOR = QColor(0, 0, 0, 70)

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.setFixedSize(BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)

    def paintEvent(self, _event):
        """вызывается PyQt автоматически"""

        painter = QPainter(self)  # привязка к виджету
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # вкл сглаживание

        board = self.game.board
        valid = set(self.game.valid_moves)  #  чтобы было O(1) при (r, c) in valid

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # координаты верхнего левого угла текущей клетки в пикселях
                x, y = c * CELL_SIZE, r * CELL_SIZE
                cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2  # центр клетки
                m = 6  # отступ фишки от края клетки

                # Клетка
                painter.fillRect(x, y, CELL_SIZE, CELL_SIZE, self.BOARD_COLOR)
                painter.setPen(QPen(self.GRID_COLOR, 1))  # контуры, толщина 1px
                # Отключаем заливку (NoBrush), иначе drawRect закрасил бы клетку цветом предыдущей нарисованной фишки.
                painter.setBrush(Qt.BrushStyle.NoBrush)  # заливка внутри контуров
                painter.drawRect(x, y, CELL_SIZE, CELL_SIZE)  # Рисует рамку клетки

                piece = board[r][c]

                if piece == BLACK:
                    painter.setBrush(QBrush(QColor("#111111")))  # Заливка
                    painter.setPen(QPen(QColor("#555555"), 1))  # Контур
                    painter.drawEllipse(
                        x + m, y + m, CELL_SIZE - 2 * m, CELL_SIZE - 2 * m
                    )

                elif piece == WHITE:
                    painter.setBrush(QBrush(QColor("#f0f0f0")))
                    painter.setPen(QPen(QColor("#999999"), 1))
                    painter.drawEllipse(
                        x + m, y + m, CELL_SIZE - 2 * m, CELL_SIZE - 2 * m
                    )

                elif (r, c) in valid:  # подсказка доступного хода
                    painter.setBrush(QBrush(self.HINT_COLOR))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(cx - 8, cy - 8, 16, 16)

    def mousePressEvent(self, event):
        """когда клик внутри границ BoardWidget"""

        if event.button() == Qt.MouseButton.LeftButton:
            # Пиксели -> Индексы матрицы
            col = int(event.position().x()) // CELL_SIZE
            row = int(event.position().y()) // CELL_SIZE
            # береженого бог бережет
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                self.cell_clicked.emit(row, col)  # этот сигнал поймает MainWindow


# ─────────────────────────── ГЛАВНОЕ ОКНО ─────────────────────────────────────


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = Game()
        self.setWindowTitle("Реверси (Отелло)")

        self.status_label = QLabel()  # Ходят белые/черные
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.score_label = QLabel()  # счёт
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setFont(QFont("Arial", 12))

        self.board_widget = BoardWidget(self.game)
        self.board_widget.cell_clicked.connect(self._on_cell_clicked)

        btn_new = QPushButton("Новая игра")
        btn_new.setFont(QFont("Arial", 11))
        btn_new.clicked.connect(self._new_game)

        layout = QVBoxLayout()  # вертикально
        layout.setSpacing(8)  # 8px между виджетами
        layout.setContentsMargins(12, 12, 12, 12)  # от краев окна
        layout.addWidget(self.status_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.board_widget)
        layout.addWidget(btn_new)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.adjustSize()  # авторазмеры окна
        self._update_ui()

    def _on_cell_clicked(self, row: int, col: int):
        if self.game.make_move(row, col):
            self.board_widget.update()  # дергает paintEvent в виджете доски
            self._update_ui()

    def _update_ui(self):
        black, white = count_pieces(self.game.board)
        self.score_label.setText(f"⚫ Чёрные: {black}   ⚪ Белые: {white}")

        if self.game.game_over:
            if black > white:
                text = "Игра окончена! Победили чёрные"
            elif white > black:
                text = "Игра окончена! Победили белые"
            else:
                text = "Игра окончена! Ничья"
        else:
            name = "Чёрные" if self.game.current_player == BLACK else "Белые"
            text = f"Ходят: {name}"
        self.status_label.setText(text)

    def _new_game(self):
        self.game.reset()
        self.board_widget.update()
        self._update_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Управляет циклом событий, настройками ОС и стилями
    window = MainWindow()
    window.show()
    sys.exit(app.exec())  # запуск Event Loop
