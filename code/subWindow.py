from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget

from functions import switch_color_mode


class SubWindow(QWidget):
    windowClose = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.windowClose.emit()

    def detect_dark_mode(self):
        switch_color_mode(self)
