from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton, QMessageBox,
	QLabel, QLineEdit, QComboBox
)
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtCore import Qt, pyqtSignal

from settings import font
from functions import save, get_trans, get_data, get_trans_entry, get_trans_info


class SettingsWin(QTabWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.data = get_data()
		self.trans = get_trans()
		self.check = self.data['settings']
		self.names = {
			j: i
			for _ in range(1, 4)
			for i, j in get_trans_entry(self.trans, f'settings.{_}').items()
		}
		self.languages = get_trans_info()
		self.checkboxes: dict[str: QCheckBox] = {}
		self.radiobuttons: dict[str: QRadioButton] = {}
		self.autoCheck = False
		self.changeLanguage = False
		self.changedFont = ''

		self.initUI()

	language_signal = pyqtSignal(bool)
	font_signal = pyqtSignal(bool)
	options_signal = pyqtSignal(bool)

	def initUI(self):
		lyt = self.calculateTab()
		self.addNewTab(lyt, self.trans['settings.1.title'])
		lyt = self.styleTab()
		self.addNewTab(lyt, self.trans['settings.4.title'])
		lyt = self.historyTab()
		self.addNewTab(lyt, self.trans['settings.2.title'])
		lyt = self.languageTab()
		self.addNewTab(lyt, self.trans['settings.3.title'])
		self.setFont(font)

		self.apply.setEnabled(False)

		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(self.trans['window.settings.title'])
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

		self.update_status()
		self.addTab(widget, name)

	def calculateTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in get_trans_entry(self.trans, 'settings.1.option').items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.addEntry(l, self.checkboxes[i])
		return l

	def historyTab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		# for i, j in self.trans['settings']['settingsTab2']['options'].items():
		# 	self.checkboxes[i] = QCheckBox(j)
		# 	l = self.addEntry(l, self.checkboxes[i])
		self.checkboxes['settings.2.option'] = QCheckBox(self.trans['settings.2.option'])
		l = self.addEntry(l, self.checkboxes['settings.2.option'])

		btn = QPushButton(self.trans['settings.2.button'])
		btn.setFont(font)
		btn.clicked.connect(self.clear_history)
		l.addWidget(btn)
		return l

	def languageTab(self) -> QVBoxLayout:
		l = QVBoxLayout()

		for name, id in get_trans_info().items():
			self.radiobuttons[id] = QRadioButton(name)
			l = self.addEntry(l, self.radiobuttons[id])

			if id == self.data['language']:
				self.radiobuttons[id].setChecked(True)

		return l

	def styleTab(self) -> QVBoxLayout:
		l = QVBoxLayout()

		hbox = QHBoxLayout()

		cblbl = QLabel(self.trans['settings.4.text.1'])
		cblbl.setFont(font)
		hbox.addWidget(cblbl)

		self.cb = QComboBox()
		database = QFontDatabase()
		self.cb.addItems(database.families())
		self.cb.setCurrentText(self.data['font'])
		hbox.addWidget(self.cb)

		hbox.addStretch(1)

		l.addLayout(hbox)

		lbl = QLabel(self.trans['settings.4.text.2'])
		lbl.setFont(font)
		l.addWidget(lbl)

		self.le = QLineEdit()
		self.le.setFont(font)
		self.le.setText(self.data['qss_code'])
		l.addWidget(self.le)

		return l

	def checked(self):
		sender = self.sender()

		if not self.autoCheck:
			self.apply.setEnabled(True)

			self.check[self.names[sender.text()]] = sender.isChecked()
			if sender.text() == self.trans['settings.1.option.2']:
				self.check['settings.1.option.3'] = False
			elif sender.text() == self.trans['settings.1.option.3']:
				self.check['settings.1.option.2'] = False
			self.update_status()

	def addBottomButton(self, layout: QVBoxLayout, mode: int = 0):
		hbox = QHBoxLayout()

		ok = QPushButton(self.trans['button.ok'])
		ok.setFont(font)
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton(self.trans['button.cancel'])
		cancel.setFont(font)
		cancel.clicked.connect(self.clicked)

		self.apply = QPushButton(self.trans['button.apply'])
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
		if sender.text() in [self.trans['button.ok'], self.trans['button.cancel'], self.trans['button.apply']]:
			if sender.text() in [self.trans['button.ok'], self.trans['button.apply']]:

				for i in self.check:
					self.data['settings'][i] = self.check[i]

				for i in self.radiobuttons.values():
					if i.isChecked() and self.languages[i.text()] != self.data['language']:
						self.data['language'] = self.languages[i.text()]
						save('data/data.json', self.data)
						self.language_signal.emit(True)
						break

				if self.cb.currentText() != self.data['font']:
					self.data['font'] = self.cb.currentText()
					save('data/data.json', self.data)
					self.font_signal.emit(True)

				if self.le.text() != self.data['qss_code']:
					self.data['qss_code'] = self.le.text()
					QMessageBox.information(self, self.trans['window.hint.title'], self.trans['settings.4.hint'], QMessageBox.Ok)

				self.apply.setEnabled(False)
				save('data/data.json', self.data)
				self.options_signal.emit(True)

			if sender.text() in [self.trans['button.ok'], self.trans['button.cancel']]:
				self.close()

	def update_status(self):
		self.autoCheck = True
		bools = [self.check[i] for i in self.check]
		for bool, name in zip(bools, self.check.keys()):
			try:
				self.checkboxes[name].setChecked(bool)
			except KeyError:
				pass

			if name == 'settings.1.option.1':
				for i in range(2):
					self.checkboxes[f'settings.1.option.{i + 2}'].setEnabled(bool)

		self.autoCheck = False

	def clear_history(self):
		if QMessageBox.question(
				self,
				self.trans['window.hint.title'],
				self.trans['settings.2.hint.1'],
				QMessageBox.Ok | QMessageBox.Cancel,
				QMessageBox.Cancel
		) == QMessageBox.Ok:
			self.data['history'] = []
			save('data/data.json', self.data)
			QMessageBox.information(
				self,
				self.trans['window.hint.title'],
				self.trans['settings.2.hint.2'],
				QMessageBox.Ok, QMessageBox.Ok
			)
