from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel


class ClickableQLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(ClickableQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()
