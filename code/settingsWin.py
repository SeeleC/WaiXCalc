from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, data, save


class SettingsWin(QTabWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)
		
		self.options = data['options']

		self.initUI()

	def initUI(self):
		self.compute = QWidget()
		self.computeUI()
		self.addTab(self.compute, '计算')

		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.setWindowTitle('设置')
		self.resize(600, 400)
		self.setMaximumSize(self.width(), self.height())

	def addEntry(self, layout: QVBoxLayout, button: QRadioButton or QCheckBox):
		button.setFont(font)
		button.stateChanged.connect(self.checked)

		hbox = QHBoxLayout()
		hbox.addWidget(button)
		hbox.addStretch(1)
		layout.addLayout(hbox)
		return layout

	def computeUI(self):
		layout = QVBoxLayout()
		scroll = QScrollArea()
		layout2 = QVBoxLayout()

		self.names = {
			'仅显示分数结果': '_floatToFraction',
			'仅显示小数结果': '_fractionToFloat',
		}

		self.checkboxes = {}
		start = 0
		self.autoChecked = True
		for name in self.names.keys():
			self.checkboxes[start] = QCheckBox(name)
			self.addEntry(layout2, self.checkboxes[start])
			start += 1
		self.autoChecked = False

		self.updateWedget()

		layout2.addStretch()
		scroll.setLayout(layout2)
		layout.addWidget(scroll)
		self.addBottomButton(layout, 0)
		self.compute.setLayout(layout)
		self.apply.setEnabled(False)

	def checked(self):
		sender = self.sender()

		if not self.autoChecked:
			self.apply.setEnabled(True)

			event = self.names[sender.text()]

			self.options[event] = sender.isChecked()
			if event == '_floatToFraction':
				self.options['_fractionToFloat'] = False
			elif event == '_fractionToFloat':
				self.options['_floatToFraction'] = False
			self.updateWedget()

	def addBottomButton(self, layout: QVBoxLayout, mode: int = 0):
		hbox = QHBoxLayout()

		ok = QPushButton('确定')
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton('取消')
		cancel.setFont(font)
		cancel.clicked.connect(self.clicked)

		self.apply = QPushButton('应用')
		self.apply.setFont(font)
		self.apply.clicked.connect(self.clicked)

		if mode == 0:
			hbox.addStretch(1)
			hbox.addWidget(ok)
			hbox.addWidget(cancel)
		elif mode == 1:
			hbox.addStretch(1)
			hbox.addWidget(ok)
			hbox.addWidget(cancel)
			hbox.addWidget(self.apply)
		layout.addLayout(hbox)

	def clicked(self):
		sender = self.sender()
		if sender.text() == '确定' or sender.text() == '取消' or sender.text() == '应用':
			if sender.text() == '确定' or sender.text() == '应用':
				for i in self.options:
					if i[0] == '_':
						data['options'][i] = self.options[i]
				self.apply.setEnabled(False)
				save('data.npy', data, allow_pickle=True, fix_imports=True)
			if sender.text() == '确定' or sender.text() == '取消':
				self.close()

	def updateWedget(self):
		self.autoChecked = True
		self.bools = [self.options[i] for i in self.options if '_' == i[0]]
		for bl, code in zip(self.bools, list(range(len(self.names)))):
				self.checkboxes[code].setChecked(bl)
		self.autoChecked = False
