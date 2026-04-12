from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QCloseEvent, QDesktopServices, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.core import BLACK, Game, count_pieces
from src.ui_board import BoardWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация данных
        self.game = Game()

        # Настройка главного окна
        self.setWindowTitle("Реверси (Отелло)")

        # Сборка интерфейса по частям
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()

        # Окно принимает минимально возможный размер под все виджеты
        self.adjustSize()
        self.setFixedSize(self.size())  #  Жестко фиксируем этот размер
        self._update_ui()

    def _setup_menu(self):
        """Создает верхнее системное меню."""
        menu_bar = self.menuBar()

        # --- Меню "Игра" ---
        game_menu = menu_bar.addMenu("Игра")

        new_game_action = QAction("Новая игра", self)
        new_game_action.triggered.connect(self._new_game)
        game_menu.addAction(new_game_action)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)

        # --- Меню "Справка" ---
        help_menu = menu_bar.addMenu("Справка")

        rules_action = QAction("Правила игры (F2)", self)
        rules_action.triggered.connect(self._show_help)
        help_menu.addAction(rules_action)

        help_menu.addSeparator()

        github_action = QAction("Исходный код (GitHub)", self)
        github_action.triggered.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://github.com/Kurmambet/reversi.git")
            )
        )
        help_menu.addAction(github_action)

    def _setup_ui(self):
        """Создает центральную часть окна (доска, текст, кнопки)."""
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setFont(QFont("Arial", 12))

        self.board_widget = BoardWidget(self.game)
        self.board_widget.cell_clicked.connect(self._on_cell_clicked)

        btn_new = QPushButton("Новая игра")
        btn_new.setFont(QFont("Arial", 11))
        btn_new.clicked.connect(self._new_game)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(self.status_label)
        layout.addWidget(self.score_label)
        layout.addWidget(self.board_widget)
        layout.addWidget(btn_new)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _setup_statusbar(self):
        """Настраивает строку состояния внизу окна."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage(
            "Горячие клавиши: [ЛКМ] - Ход | [F2] - Справка | [Esc] - Выход"
        )

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

    # Обработка закрытия окна
    def closeEvent(self, event: QCloseEvent):
        """Вызывается при попытке закрыть окно (крестиком или программно)."""
        # Создаем диалоговое окно с вопросом
        reply = QMessageBox.question(
            self,
            "Подтверждение выхода",  # Заголовок
            "Вы действительно хотите выйти из игры?\nТекущий прогресс будет потерян.",  # Текст
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Кнопки
            QMessageBox.StandardButton.No,  # Кнопка по умолчанию (чтобы случайно не нажать Enter)
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()  # Разрешаем закрытие
        else:
            event.ignore()  # Отменяем закрытие, игра продолжается

    # Обработка клавиатуры
    def keyPressEvent(self, event: QKeyEvent):
        """Вызывается при нажатии любой клавиши, пока окно активно."""

        if event.key() == Qt.Key.Key_Escape:
            # встроенный метод .close() окна автоматически вызовет closeEvent
            self.close()

        # Обработка клавиши F2
        elif event.key() == Qt.Key.Key_F2:
            self._show_help()

        else:
            # Если нажали другую клавишу, передаем событие дальше (стандартное поведение)
            super().keyPressEvent(event)

    def _show_help(self):
        """окно с правилами."""
        help_text = (
            "ПРАВИЛА ИГРЫ 'РЕВЕРСИ'\n\n"
            "Цель игры — чтобы ваших фишек на доске оказалось больше, чем фишек противника.\n\n"
            "Как ходить:\n"
            "Вы должны поставить свою фишку так, чтобы между ней и одной из "
            "ваших старых фишек оказался непрерывный ряд фишек противника "
            "(по вертикали, горизонтали или диагонали). "
            "Все 'закрытые' фишки противника перевернутся и станут вашими.\n\n"
            "Горячие клавиши:\n"
            "- Левый клик — сделать ход\n"
            "- F2 — показать эту справку\n"
            "- Esc — выход из программы"
        )

        # окно с кнопкой "ОК"
        QMessageBox.information(self, "Справка по игре", help_text)
