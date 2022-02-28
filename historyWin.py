from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, data


class HistoryWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextEdit('history')
		text.setFont(font)
		text.setText(''.join([i[:-1] + '\n' for i in [i + ' ' for i in data['history']]]))
		text.setReadOnly(True)

		hbox = QHBoxLayout()

		ok = QPushButton('确定')
		ok.setShortcut('Return')
		ok.clicked.connect(self.close)

		hbox.addStretch(1)
		hbox.addWidget(ok)

		layout.addWidget(text)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle('历史记录')
		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.resize(600, 400)
