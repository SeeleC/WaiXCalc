from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel


class EnhancedQLabel(QLabel):
    clicked = pyqtSignal()
    mouseEnter = pyqtSignal()
    mouseLeave = pyqtSignal()

    def __init__(self, parent=None):
        super(EnhancedQLabel, self).__init__(parent)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()

    def enterEvent(self, a0: QEvent) -> None:
        self.setText('<u>%s</u>' % self.text())
        self.mouseEnter.emit()

    def leaveEvent(self, a0: QEvent) -> None:
        self.setText(self.text()[3:-4])
        self.mouseLeave.emit()
