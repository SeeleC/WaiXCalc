from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget

from functions import switch_color_mode


class SubWindow(QWidget):
    windowClose = pyqtSignal()

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.windowClose.emit()

    def detect_dark_mode(self):
        switch_color_mode(self)
