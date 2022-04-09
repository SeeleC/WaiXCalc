from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, data, trans


class HistoryWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextEdit()
		text.setFont(font)
		text.setText(''.join([i[:-1] + '\n' for i in [i + ' ' for i in data['history']]]))
		if not data['settings']['_enableRecordHistory']:
			text.append(trans['historyDisabled'])
		text.setReadOnly(True)

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
		self.setWindowTitle(trans['windowTitles']['historyWin'])
		self.setWindowIcon(QIcon('resource/images\\ico.JPG'))
		self.resize(600, 400)
