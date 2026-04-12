import sys

from PyQt6.QtWidgets import QApplication

from src.ui_main import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Управляет циклом событий, настройками ОС и стилями
    window = MainWindow()
    window.show()
    sys.exit(app.exec())  # запуск Event Loop
