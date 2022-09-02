from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from win32mica import ApplyMica, MICAMODE

from settings import font, tFont
from functions import get_trans, get_options, get_history, get_reversed_list


class HistoryWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowCloseButtonHint)

        self.options = get_options()
        self.history = get_history()
        self.trans = get_trans()

        self.init_ui()

    def init_ui(self):
        self.setFont(font)
        outer = QVBoxLayout()

        area = QScrollArea()
        area.setWidgetResizable(True)
        inner = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(inner)

        for i in [f + ' ' for f in get_reversed_list(self.history)]:
            self.add_entry(i, inner)
        inner.addStretch(1)

        area.setWidget(widget)
        outer.addWidget(area)

        hbox = QHBoxLayout()
        hbox.addStretch(1)

        clear = QPushButton(self.trans['button.clear_history'])
        clear.clicked.connect(self.clear_history)

        ok = QPushButton(self.trans['button.back'])
        ok.setShortcut('Escape')
        ok.clicked.connect(self.close)

        hbox.addWidget(clear)
        hbox.addWidget(ok)

        outer.addLayout(hbox)

        if self.options['settings.4.option']:
            self.setAttribute(Qt.WA_TranslucentBackground)
            ApplyMica(int(self.winId()), MICAMODE.LIGHT)

        self.setLayout(outer)
        self.setWindowTitle(self.trans['window.history.title'])
        self.setWindowIcon(QIcon('resource/images/icon.jpg'))
        self.resize(600, 400)

    def add_entry(self, formula, layout):
        f, r = formula.split(' = ')

        f_box = QHBoxLayout()
        f_box.addStretch(1)

        f_label = QLabel(f + ' =')
        f_label.setFont(font)
        f_label.setStyleSheet('color:#838383;')
        f_box.addWidget(f_label)

        r_box = QHBoxLayout()
        r_box.addStretch(1)

        r_label = QLabel(r)
        r_label.setFont(tFont)
        r_label.setStyleSheet('color:#0c0c0c;')
        r_box.addWidget(r_label)

        layout.addLayout(f_box)
        layout.addLayout(r_box)

    def clear_history(self):
        save('data/history.json', [])
        get_translated_messagebox(
            QMessageBox.Icon.Information,
            self.trans['window.hint.title'],
            self.trans['settings.2.hint.2'],
            self
        ).show()
