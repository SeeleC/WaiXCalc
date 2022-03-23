from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font


class HelpWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextBrowser()
		text.setFont(font)
		with open('help.txt', 'r', encoding='utf-8') as f:
			text.setHtml(f.read())
		text.setOpenExternalLinks(True)

		hbox = QHBoxLayout()

		ok = QPushButton('返回')
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.close)

		hbox.addStretch(1)
		hbox.addWidget(ok)

		layout.addWidget(text)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle('帮助')
		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.resize(600, 400)

