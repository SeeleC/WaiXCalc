from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep

from functions import is_dark_mode


class Detector(QThread):
    colorModeChanged = pyqtSignal()

    def __init__(self, window: QWidget):
        super().__init__()
        self.window = window

    def run(self) -> None:
        while True:
            if is_dark_mode() != self.window.data['enableDarkMode'] and\
                    self.window.options['settings.4.selector.2'] == 'colorMode.auto':
                self.colorModeChanged.emit()
            sleep(0.3)
