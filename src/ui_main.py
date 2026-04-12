from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

from src.core import BLACK, Game, count_pieces
from src.ui_board import BoardWidget


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
