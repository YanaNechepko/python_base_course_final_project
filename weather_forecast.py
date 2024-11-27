import sys

from PyQt5 import QtWidgets

from core.db import DataBase
from windows.main_window import MainWindow


def main() -> None:
    app = QtWidgets.QApplication([])
    database = DataBase()
    window = MainWindow(database)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
