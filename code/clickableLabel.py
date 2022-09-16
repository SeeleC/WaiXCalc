from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtGui import QMouseEvent

from selectableLabel import SelectableLabel


class ClickableLabel(SelectableLabel):
    clicked = pyqtSignal()
    mouseEnter = pyqtSignal()
    mouseLeave = pyqtSignal()

    def __init__(self, *args):
        super(ClickableLabel, self).__init__(*args)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        self.clicked.emit()

    def enterEvent(self, a0: QEvent) -> None:
        self.setText('<u>%s</u>' % self.text())
        self.mouseEnter.emit()

    def leaveEvent(self, a0: QEvent) -> None:
        self.setText(self.text()[3:-4])
        self.mouseLeave.emit()
