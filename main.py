import sys
from src.editor import Editor
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = Editor()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
