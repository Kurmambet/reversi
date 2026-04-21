import sys
import time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen

from src.ui_main import MainWindow


def create_splash_pixmap() -> QPixmap:
    """Создает картинку-заставку программно, без внешних файлов."""
    pixmap = QPixmap(500, 300)
    pixmap.fill(QColor("#2d7a2d"))  # Зеленый фон доски

    painter = QPainter(pixmap)
    painter.setPen(QColor("white"))

    # Заголовок
    painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
    painter.drawText(
        pixmap.rect(),
        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        "\nРЕВЕРСИ (ОТЕЛЛО)",
    )

    # Описание
    painter.setFont(QFont("Arial", 12))
    description = (
        "\n\n\n\n"
        "Классическая настольная логическая игра.\n"
        "Захватывайте фишки противника, окружая их своими!\n\n"
        "Возможности:\n"
        "- Игра для двух игроков\n"
        "- Подсчет очков в реальном времени\n"
        "- Подсказки доступных ходов\n"
    )
    painter.drawText(
        pixmap.rect(),
        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
        description,
    )

    # Автор
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(
        pixmap.rect(),
        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
        "Курсовая работа.  \n2026 г.   \n",
    )

    painter.end()
    return pixmap


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    # заставка
    splash_pixmap = create_splash_pixmap()
    splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    # имитация долгую загрузку
    # app.processEvents() заставляет окно отрисоваться немедленно
    app.processEvents()
    time.sleep(2.5)  # Пауза 2.5 секунды

    window = MainWindow()
    window.show()

    # Закрываем заставку, когда появилось главное окно
    splash.finish(window)

    sys.exit(app.exec())
