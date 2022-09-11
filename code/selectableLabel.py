from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class SelectableLabel(QLabel):
    def __init__(self, *__args):
        super(SelectableLabel, self).__init__(__args)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
