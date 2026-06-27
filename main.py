import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont('Segoe UI', 10))

    # Ensure we can find our files regardless of CWD
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
