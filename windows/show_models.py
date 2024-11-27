from collections.abc import Sequence

from PyQt5 import QtCore


class DataTableViewModel(QtCore.QAbstractTableModel):
    def __init__(self, data: Sequence[str], headers: list[str]):
        super().__init__()
        self._data = data
        self._headers = headers

    def rowCount(self, parent=None) -> int:
        if parent == QtCore.QModelIndex():
            return len(self._headers)

        return 0

    def columnCount(self, parent=None) -> int:
        if parent == QtCore.QModelIndex():
            return 1

        return 0

    def data(self, index: QtCore.QModelIndex, role=None):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]

        return None

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation,
                   role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return self._headers[section]

        return None
