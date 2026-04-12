from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from src.core import BLACK, BOARD_SIZE, CELL_SIZE, WHITE, Game


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
