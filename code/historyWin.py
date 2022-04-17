from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font
from functions import get_trans, get_data, get_history


class HistoryWin(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)
		
		self.data = get_data()
		self.history = get_history()
		self.trans = get_trans()

		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()

		text = QTextEdit()
		text.setFont(font)
		text.setText(''.join([i[:-1] + '\n' for i in [i + ' ' for i in self.history]]))
		if not self.data['settings']['_enableRecordHistory']:
			text.append(self.trans['historyDisabled'])
		text.setReadOnly(True)

		hbox = QHBoxLayout()

		ok = QPushButton(self.trans['buttonBack'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.close)

		hbox.addStretch(1)
		hbox.addWidget(ok)

		layout.addWidget(text)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle(self.trans['windowTitles']['historyWin'])
		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.resize(600, 400)
