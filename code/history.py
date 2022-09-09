from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QMessageBox, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from win32mica import ApplyMica, MICAMODE
from os import remove

from colorModeDetect import Detector
from enhancedQLabel import EnhancedQLabel
from subWindow import SubWindow
from settings import rFont, tFont
from functions import get_trans, get_options, get_reversed_list, get_enhanced_messagebox, get_data, load_theme


class History(SubWindow):
    historyReversion = pyqtSignal()

    def __init__(self, history):
        super().__init__()
        self.setWindowFlag(Qt.WindowCloseButtonHint)

        self.options: dict = get_options()
        self.data = get_data()
        self.trans = get_trans()
        self.history: list = history

        self.focus_entry = ''

        self.detector = Detector(self)
        self.detector.colorModeChanged.connect(self.detect_dark_mode)
        self.detector.start()

        self.init_ui()

    def init_ui(self):
        self.setFont(rFont)
        outer = QVBoxLayout()

        self.area = QScrollArea()
        self.area.setAutoFillBackground(True)
        self.area.setWidgetResizable(True)
        inner = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(inner)

        for i in [f + ' ' for f in get_reversed_list(self.history)]:
            self.add_entry(i, inner)
        inner.addStretch(1)

        self.area.setWidget(widget)
        outer.addWidget(self.area)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        clear = QPushButton(self.trans['button.clear_history'])
        clear.clicked.connect(self.clear_history)

        ok = QPushButton(self.trans['button.back'])
        ok.clicked.connect(self.close)

        hbox.addWidget(clear)
        hbox.addWidget(ok)

        outer.addLayout(hbox)

        load_theme(self)

        close_action = QAction(self)
        close_action.setShortcuts(['Return', 'Escape'])
        close_action.triggered.connect(self.close)
        self.addAction(close_action)

        self.setLayout(outer)
        self.setWindowTitle(self.trans['window.history.title'])
        self.setWindowIcon(QIcon('resource/images/icon.jpg'))
        self.resize(600, 400)

    def add_entry(self, formula, layout):
        f, r = formula.split(' = ')
        texts = [f+' =', r]
        if self.data['enableDarkMode']:
            colors = ['color:#838383;', 'color:#cccccc;']
        else:
            colors = ['color:#838383;', 'color:#0c0c0c;']
        fonts = [rFont, tFont]

        for text, color, font in zip(texts, colors, fonts):
            box = QHBoxLayout()
            box.addStretch(1)
            label = EnhancedQLabel(text)
            label.clicked.connect(self.revert_history)
            label.setFont(font)
            label.setStyleSheet(color)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignRight)
            box.addWidget(label)
            layout.addLayout(box)

    def apply_mica(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        if self.data['enableDarkMode'] or self.options['settings.4.selector.2'] == 'colorMode.dark':
            ApplyMica(int(self.winId()), MICAMODE.DARK)
        else:
            ApplyMica(int(self.winId()), MICAMODE.LIGHT)

    def clear_history(self):
        self.history.clear()

        try:
            remove('data/history.json')
        except FileNotFoundError:
            pass

        self.close()
        get_enhanced_messagebox(
            QMessageBox.Icon.NoIcon,
            self.trans['hint.history.title'],
            self.trans['hint.history.clear'],
            self,
            self.data['enableDarkMode']
        ).show()

    def revert_history(self):
        sender = self.sender()

        if '=' in sender.text():
            self.focus_entry = sender.text()[3:-6]
        else:
            self.focus_entry = sender.text()[3:-4]
        self.historyReversion.emit()

        self.close()
