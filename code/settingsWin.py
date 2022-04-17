from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from os import listdir

from settings import font
from functions import save, get_trans, get_data


class SettingsWin(QTabWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.data = get_data()
		self.trans = get_trans()
		self.check = self.data['settings']
		self.names = {
			j: i
			for _ in self.trans['settings'].values()
			for i, j in _['options'].items()
		}
		self.checkboxes = {}
		self.radiobuttons = {}
		self.autoCheck = False
		self.changeLang = False

		self.initUI()

	signal = pyqtSignal(bool)

	def initUI(self):
		lyt = self.calculateTab()
		self.addNewTab(lyt, self.trans['settings']['settingsTab1']['title'])
		lyt = self.historyTab()
		self.addNewTab(lyt, self.trans['settings']['settingsTab2']['title'])
		lyt = self.languageTab()
		self.addNewTab(lyt, self.trans['settings']['settingsTab3']['title'])
		self.setFont(font)

		self.apply.setEnabled(False)

		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(self.trans['windowTitles']['settingsWin'])
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
		for i, j in self.trans['settings']['settingsTab1']['options'].items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.addEntry(l, self.checkboxes[i])
		return l

	def historyTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in self.trans['settings']['settingsTab2']['options'].items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.addEntry(l, self.checkboxes[i])
		btn = QPushButton(self.trans['settings']['settingsTab2']['buttonClearHistory'])
		btn.setFont(font)
		btn.clicked.connect(self.clear_history)
		l.addWidget(btn)
		return l

	def languageTab(self) -> QVBoxLayout:
		l = QVBoxLayout()

		for i in sorted(listdir('resource/lang')):
			i = i[:-5]
			if i != 'template':
				if i in self.trans['settings']['settingsTab3']['options'].keys():
					name = self.trans['settings']['settingsTab3']['options'][i]
				else:
					name = i
				self.radiobuttons[i] = QRadioButton(name)
				l = self.addEntry(l, self.radiobuttons[i])
				if i == self.data['settings']['language']:
					self.radiobuttons[i].setChecked(True)
		return l

	def checked(self):
		sender = self.sender()

		if not self.autoCheck:
			self.apply.setEnabled(True)

			self.check[self.names[sender.text()]] = sender.isChecked()
			if sender.text() == self.trans['settings']['settingsTab1']['options']['_floatToFraction']:
				self.check['_fractionToFloat'] = False
			elif sender.text() == self.trans['settings']['settingsTab1']['options']['_fractionToFloat']:
				self.check['_floatToFraction'] = False
			self.updateStatus()

	def addBottomButton(self, layout: QVBoxLayout, mode: int = 0):
		hbox = QHBoxLayout()

		ok = QPushButton(self.trans['buttonOk'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton(self.trans['buttonCancel'])
		cancel.setFont(font)
		cancel.clicked.connect(self.clicked)

		self.apply = QPushButton(self.trans['buttonApply'])
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
		if sender.text() == self.trans['buttonOk'] or sender.text() == self.trans['buttonCancel'] or\
			sender.text() == self.trans['buttonApply']:
			if sender.text() == self.trans['buttonOk'] or sender.text() == self.trans['buttonApply']:
				for i in self.check:
					if i[0] == '_':
						self.data['settings'][i] = self.check[i]
				for i in self.radiobuttons.values():
					if i.isChecked() and self.names[i.text()] != self.data['settings']['language']:
						self.data['settings']['language'] = self.names[i.text()]
						save('data/data.json', self.data)
						self.signal.emit(True)
						break
				self.apply.setEnabled(False)
				save('data/data.json', self.data)
			if sender.text() == self.trans['buttonOk'] or sender.text() == self.trans['buttonCancel']:
				self.close()

	def updateStatus(self):
		self.autoCheck = True
		bools = [self.check[i] for i in self.check if '_' == i[0]]
		for bl, name in zip(bools, self.check.keys()):
			try:
				self.checkboxes[name].setChecked(bl)
			except KeyError:
				pass
		self.autoCheck = False

	def clear_history(self):
		if QMessageBox.question(
				self,
				self.trans['remindTexts']['title'],
				self.trans['remindTexts']['clearHistory']['remind1'],
				QMessageBox.Ok | QMessageBox.Cancel,
				QMessageBox.Cancel
		) == QMessageBox.Ok:
			self.data['history'] = []
			save('data/data.json', self.data)
			QMessageBox.information(
				self,
				self.trans['remindTexts']['title'],
				self.trans['remindTexts']['clearHistory']['remind2'],
				QMessageBox.Ok, QMessageBox.Ok)
