from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, trans


class HelpWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextBrowser()
		text.setFont(font)
		text.setHtml(trans['helpContent'])
		text.setOpenExternalLinks(True)

		hbox = QHBoxLayout()

		ok = QPushButton(trans['buttonBack'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.close)

		hbox.addStretch(1)
		hbox.addWidget(ok)

		layout.addWidget(text)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle(trans['windowTitles']['helpWin'])
		self.setWindowIcon(QIcon('resource/images\\ico.JPG'))
		self.resize(600, 400)

