from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, data, trans
from functions import save


class SettingsWin(QTabWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.check = data['settings']
		self.names = {
			j: i
			for _ in trans['settings'].values()
			for i, j in _['options'].items()
		}
		self.checkboxes = {}
		self.radiobuttons = {}
		self.autoCheck = False

		self.initUI()

	def initUI(self):
		lyt = self.calculateTab()
		self.addNewTab(lyt, trans['settings']['settingsTab1']['title'])
		lyt = self.historyTab()
		self.addNewTab(lyt, trans['settings']['settingsTab2']['title'])
		lyt = self.languageTab()
		self.addNewTab(lyt, trans['settings']['settingsTab3']['title'])
		self.setFont(font)

		self.apply.setEnabled(False)

		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(trans['windowTitles']['settingsWin'])
		self.resize(600, 400)
		self.setMaximumSize(self.width(), self.height())

	def addEntry(self, layout: QVBoxLayout, button: QCheckBox) -> QVBoxLayout:
		button.setFont(font)
		if isinstance(button, QCheckBox):
			button.stateChanged.connect(self.checked)
		else:
			button.clicked.connect(self.clicked)

		hbox = QHBoxLayout()
		hbox.addWidget(button)
		hbox.addStretch(1)
		layout.addLayout(hbox)
		return layout

	def addNewTab(self, inner: QVBoxLayout, name: str):
		widget = QWidget()
		outer = QVBoxLayout()
		s = QScrollArea()

		inner.addStretch()
		s.setLayout(inner)
		outer.addWidget(s)
		self.addBottomButton(outer, 0)
		widget.setLayout(outer)

		self.updateStatus()
		self.addTab(widget, name)

	def calculateTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in trans['settings']['settingsTab1']['options'].items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.addEntry(l, self.checkboxes[i])
		return l

	def historyTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in trans['settings']['settingsTab2']['options'].items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.addEntry(l, self.checkboxes[i])
		btn = QPushButton(trans['settings']['settingsTab2']['buttonClearHistory'])
		btn.setFont(font)
		btn.clicked.connect(self.clear_history)
		l.addWidget(btn)
		return l

	def languageTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in trans['settings']['settingsTab3']['options'].items():
			self.radiobuttons[i] = QRadioButton(j)
			l = self.addEntry(l, self.radiobuttons[i])
			if i == data['settings']['language']:
				self.radiobuttons[i].setChecked(True)
		return l

	def checked(self):
		sender = self.sender()

		if not self.autoCheck:
			self.apply.setEnabled(True)

			self.check[self.names[sender.text()]] = sender.isChecked()
			if sender.text() == trans['settings']['settingsTab1']['options']['_floatToFraction']:
				self.check['_fractionToFloat'] = False
			elif sender.text() == trans['settings']['settingsTab1']['options']['_fractionToFloat']:
				self.check['_floatToFraction'] = False
			self.updateStatus()

	def addBottomButton(self, layout: QVBoxLayout, mode: int = 0):
		hbox = QHBoxLayout()

		ok = QPushButton(trans['buttonOk'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton(trans['buttonCancel'])
		cancel.setFont(font)
		cancel.clicked.connect(self.clicked)

		self.apply = QPushButton(trans['buttonApply'])
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
		if sender.text() == trans['buttonOk'] or sender.text() == trans['buttonCancel'] or\
			sender.text() == trans['buttonApply']:
			if sender.text() == trans['buttonOk'] or sender.text() == trans['buttonApply']:
				for i in self.check:
					if i[0] == '_':
						data['settings'][i] = self.check[i]
				for i in self.radiobuttons.values():
					if i.isChecked():
						data['settings']['language'] = self.names[i.text()]
				self.apply.setEnabled(False)
				save('data.json', data)
			if sender.text() == trans['buttonOk'] or sender.text() == trans['buttonCancel']:
				self.close()

	def updateStatus(self):
		self.autoCheck = True
		bools = [self.check[i] for i in self.check if '_' == i[0]]
		for bl, name in zip(bools, self.names.values()):
			try:
				self.checkboxes[name].setChecked(bl)
			except KeyError:
				pass
		self.autoCheck = False

	def clear_history(self):
		if QMessageBox.question(
				self,
				trans['remindTexts']['title'],
				trans['remindTexts']['clearHistory']['remind1'],
				QMessageBox.Ok | QMessageBox.Cancel,
				QMessageBox.Cancel
		) == QMessageBox.Ok:
			data['history'] = []
			save('data.json', data)
			QMessageBox.information(
				self,
				trans['remindTexts']['title'],
				trans['remindTexts']['clearHistory']['remind1'] ,
				QMessageBox.Ok, QMessageBox.Ok)