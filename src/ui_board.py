from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from src.core import BLACK, BOARD_SIZE, CELL_SIZE, WHITE, Game

THEMES = {
    "light": {
        "board": QColor("#2d7a2d"),  # Классический зеленый
        "grid": QColor("#1a5c1a"),  # Темно-зеленая сетка
        "hint": QColor(0, 0, 0, 70),  # Темные полупрозрачные точки
    },
    "dark": {
        "board": QColor("#2c3e50"),  # Темно-синий/серый (ночной режим)
        "grid": QColor("#1a252f"),  # Почти черная сетка
        "hint": QColor(255, 255, 255, 70),  # Светлые полупрозрачные точки
    },
}


class BoardWidget(QWidget):
    cell_clicked = pyqtSignal(int, int)

    def __init__(self, game: Game):
        super().__init__()
        self.game = game
        self.setFixedSize(BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
        self.theme_name = "light"  # по умолчанию

    def set_theme(self, theme_name: str):
        """Меняет тему виджета и запрашивает перерисовку"""
        if theme_name in THEMES:
            self.theme_name = theme_name
            self.update()  # Заставляет Qt вызвать paintEvent

    def paintEvent(self, _event):
        """вызывается PyQt автоматически"""

        painter = QPainter(self)  # привязка к виджету
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # вкл сглаживание

        board = self.game.board
        valid = set(self.game.valid_moves)  # чтобы было O(1) при (r, c) in valid

        # Получаем текущие цвета доски
        colors = THEMES[self.theme_name]

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # координаты верхнего левого угла текущей клетки в пикселях
                x, y = c * CELL_SIZE, r * CELL_SIZE
                cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2  # центр клетки
                m = 6  # отступ фишки от края клетки

                # Рисуем клетку с цветами из словаря
                painter.fillRect(x, y, CELL_SIZE, CELL_SIZE, colors["board"])
                painter.setPen(QPen(colors["grid"], 1))  # контуры, толщина 1px
                # нет заливке!, иначе drawRect закрасил бы клетку цветом предыдущей нарисованной фишки.
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(x, y, CELL_SIZE, CELL_SIZE)

                # Рисуем фишки (оставляем черно/белыми, это классика)
                piece = board[r][c]
                if piece == BLACK:
                    painter.setBrush(QBrush(QColor("#111111")))
                    painter.setPen(QPen(QColor("#555555"), 1))
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
                    painter.setBrush(QBrush(colors["hint"]))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(cx - 8, cy - 8, 16, 16)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            col = int(event.position().x()) // CELL_SIZE
            row = int(event.position().y()) // CELL_SIZE
            # береженого бог бережет
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                self.cell_clicked.emit(row, col)  # этот сигнал поймает MainWindow
