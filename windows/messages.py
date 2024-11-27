from __future__ import annotations

from enum import Enum

from PyQt5.QtWidgets import QMessageBox


class MessageBox:
    class IconType(Enum):
        INFORMATION = QMessageBox.Information
        WARNING = QMessageBox.Warning

    @staticmethod
    def show_message(
            *,
            title: str,
            text: str,
            icon: IconType,
            buttons: QMessageBox.StandardButtons | QMessageBox.StandardButton,
            ) -> bool:
        dlg = QMessageBox()
        dlg.setWindowTitle(title)
        dlg.setText(text)
        dlg.setIcon(icon.value)
        dlg.setStandardButtons(buttons)

        result = dlg.exec()
        confirmed = (result == QMessageBox.Ok)
        return confirmed

    @staticmethod
    def show_information_message(*, title: str, text: str) -> None:
        MessageBox.show_message(
                title=title,
                text=text,
                icon=MessageBox.IconType.INFORMATION,
                buttons=QMessageBox.Ok,
                )

    @staticmethod
    def show_warning_message(*, title: str, text: str) -> None:
        MessageBox.show_message(
                title=title,
                text=text,
                icon=MessageBox.IconType.WARNING,
                buttons=QMessageBox.Ok,
                )
