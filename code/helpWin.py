from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, textFont
from functions import get_trans


class HelpWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.trans = get_trans()

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextBrowser()
		text.setFont(textFont)
		text.setHtml(self.trans['text.help.content'])
		text.setOpenExternalLinks(True)

		hbox = QHBoxLayout()

		ok = QPushButton(self.trans['button.back'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.close)

		hbox.addStretch(1)
		hbox.addWidget(ok)

		layout.addWidget(text)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle(self.trans['window.help.title'])
		self.setWindowIcon(QIcon('resource/images\\ico.JPG'))
		self.resize(600, 400)

