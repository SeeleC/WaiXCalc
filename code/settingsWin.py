from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton, QMessageBox,
	QLabel, QLineEdit, QComboBox
)
from PyQt5.QtGui import QIcon, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from asyncio import run, create_task
from sys import getwindowsversion
from win32mica import ApplyMica, MICAMODE

from settings import __version__, tFont, rFont
from functions import save, get_trans, get_options, get_trans_entry, get_trans_info, get_data, get_translated_messagebox


class SettingsWin(QTabWidget):
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.WindowCloseButtonHint)

		self.options = get_options()
		self.data = get_data()
		self.trans = get_trans()
		self.check = {
			i: j for i, j in self.options.items()
		}
		self.names = {
			j: i
			for _ in range(1, 5)
			for i, j in get_trans_entry(self.trans, f'settings.{_}').items()
		}
		self.languages = get_trans_info()
		self.checkboxes: dict[str: QCheckBox] = {}
		self.radiobuttons: dict[str: QRadioButton] = {}
		self.autoCheck = False
		self.changeLanguage = False
		self.changedFont = ''

		self.init_ui()

	language_signal = pyqtSignal()
	font_signal = pyqtSignal()
	options_signal = pyqtSignal()
	title_signal = pyqtSignal()

	def init_ui(self):
		run(self.init_tabs())

		if self.options['settings.4.option']:
			self.setAttribute(Qt.WA_TranslucentBackground)
			if self.options['enableDarkMode']:
				ApplyMica(int(self.winId()), MICAMODE.DARK)
			else:
				ApplyMica(int(self.winId()), MICAMODE.LIGHT)

		self.setFont(rFont)
		self.setWindowIcon(QIcon('resource/images/icon.jpg'))
		self.setWindowTitle(self.trans['window.settings.title'])
		self.resize(600, 400)
		self.setMaximumSize(self.width(), self.height())

	async def init_tabs(self):
		task1 = create_task(
			self.init_tab(self.trans['settings.1.title'], self.calculate_tab)
		)
		task2 = create_task(
			self.init_tab(self.trans['settings.4.title'], self.style_tab)
		)
		task3 = create_task(
			self.init_tab(self.trans['settings.2.title'], self.history_tab)
		)
		task4 = create_task(
			self.init_tab(self.trans['settings.3.title'], self.language_tab)
		)
		task5 = create_task(
			self.init_tab(self.trans['settings.5.title'], self.about_tab)
		)

		await task1
		await task2
		await task3
		await task4
		await task5

	async def init_tab(self, title, function):
		lyt = function()
		self.add_tab(lyt, title)

	def add_option_entry(self, layout: QVBoxLayout, widget: QCheckBox) -> QVBoxLayout:
		if isinstance(widget, QCheckBox):
			widget.stateChanged.connect(self.checked)
		else:
			widget.clicked.connect(self.clicked)

		hbox = QHBoxLayout()
		hbox.addWidget(widget)
		hbox.addStretch(1)
		layout.addLayout(hbox)
		return layout

	def add_enter_entry(self, layout: QVBoxLayout, title: str, widget: QLineEdit, text: str = '') -> QVBoxLayout:
		widget.setText(text)

		hbox = QHBoxLayout()

		title_label = QLabel(title + ':')
		hbox.addWidget(title_label)
		hbox.addStretch(1)

		layout.addLayout(hbox)
		layout.addWidget(widget)

		return layout

	def add_tab(self, inner: QVBoxLayout, name: str):
		widget = QWidget()
		outer = QVBoxLayout()
		s = QScrollArea()

		inner.addStretch()
		s.setLayout(inner)
		outer.addWidget(s)
		self.add_bottom_button(outer)
		widget.setLayout(outer)

		self.update_status()
		self.addTab(widget, name)

	def calculate_tab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in get_trans_entry(self.trans, 'settings.1.option').items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.add_option_entry(l, self.checkboxes[i])
		return l

	def history_tab(self) -> QVBoxLayout:
		l = QVBoxLayout()
		for i, j in get_trans_entry(self.trans, 'settings.2.option').items():
			self.checkboxes[i] = QCheckBox(j)
			l = self.add_option_entry(l, self.checkboxes[i])
		return l

	def language_tab(self) -> QVBoxLayout:
		l = QVBoxLayout()

		for name, id in get_trans_info().items():
			self.radiobuttons[id] = QRadioButton(name)
			l = self.add_option_entry(l, self.radiobuttons[id])

			if id == self.options['language']:
				self.radiobuttons[id].setChecked(True)

		return l

	def style_tab(self) -> QVBoxLayout:
		l = QVBoxLayout()

		self.checkboxes['settings.4.option'] = QCheckBox(self.trans['settings.4.option'])
		l = self.add_option_entry(l, self.checkboxes['settings.4.option'])

		if getwindowsversion().build < 22000:
			self.checkboxes['settings.4.option'].setEnabled(False)

		hbox = QHBoxLayout()

		cblbl = QLabel(self.trans['settings.4.text.1'])
		hbox.addWidget(cblbl)

		self.cb = QComboBox()
		database = QFontDatabase()
		self.cb.addItems(database.families())
		self.cb.setCurrentText(self.options['font'])
		hbox.addWidget(self.cb)

		hbox.addStretch(1)

		l.addLayout(hbox)

		self.window_title = QLineEdit()
		self.add_enter_entry(l, self.trans['settings.4.text.2'], self.window_title, self.options['window_title'])

		return l

	def about_tab(self) -> QVBoxLayout:
		outer_vbox = QVBoxLayout()
		outer_vbox.addStretch(1)

		hbox = QHBoxLayout()
		hbox.addStretch(1)

		inner_vbox = QVBoxLayout()
		inner_vbox.addStretch(1)

		image = QLabel()
		image.setPixmap(QPixmap('resource\\images\\icon.jpg'))
		image.setFixedSize(100, 100)
		image.setScaledContents(True)
		inner_vbox.addWidget(image)

		label = QLabel(f'WaiXCalc\nBy Github@WaiZhong\nVersion {__version__}\n')
		label.setFont(tFont)
		inner_vbox.addWidget(label)

		button = QPushButton(self.trans['settings.5.button'])
		button.clicked.connect(self.clicked)
		inner_vbox.addWidget(button)

		inner_vbox.addStretch(1)
		hbox.addLayout(inner_vbox)
		hbox.addStretch(1)
		outer_vbox.addLayout(hbox)
		outer_vbox.addStretch(1)
		return outer_vbox

	def checked(self):
		sender = self.sender()

		if not self.autoCheck:
			self.check[self.names[sender.text()]] = sender.isChecked()
			if sender.text() == self.trans['settings.1.option.2']:
				self.check['settings.1.option.3'] = False
			elif sender.text() == self.trans['settings.1.option.3']:
				self.check['settings.1.option.2'] = False
			self.update_status()

	def add_bottom_button(self, layout: QVBoxLayout):
		hbox = QHBoxLayout()

		ok = QPushButton(self.trans['button.ok'])
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton(self.trans['button.cancel'])
		cancel.clicked.connect(self.clicked)

		hbox.addStretch(1)
		hbox.addWidget(ok)
		hbox.addWidget(cancel)
		layout.addLayout(hbox)

	def clicked(self):
		sender = self.sender()
		if sender.text() in [self.trans['button.ok'], self.trans['button.cancel']]:
			self.close()
			if sender.text() == self.trans['button.ok']:
				if self.checkboxes['settings.4.option'].isChecked() != self.options['settings.4.option']:
					get_translated_messagebox(
						QMessageBox.Icon.Information,
						self.trans['window.hint.title'],
						self.trans['settings.4.hint'],
						self,
						self.options['enableDarkMode']
					).show()

				for i in self.check.keys():
					self.options[i] = self.check[i]
				for i in self.radiobuttons.values():
					if i.isChecked() and self.languages[i.text()] != self.options['language']:
						self.options['language'] = self.languages[i.text()]
						save('data/options.json', self.options)
						self.language_signal.emit()
						break

				if self.cb.currentText() != self.options['font']:
					self.options['font'] = self.cb.currentText()
					save('data/options.json', self.options)
					self.font_signal.emit()

				if self.window_title.text() != self.options['window_title']:
					self.options['window_title'] = self.window_title.text()
					save('data/options.json', self.options)
					self.title_signal.emit()

				save('data/options.json', self.options)
				self.options_signal.emit()
		elif sender.text() == self.trans['settings.5.button']:
			QMessageBox.aboutQt(self, self.trans['settings.5.button'])

	def update_status(self):
		self.autoCheck = True
		for value, name in zip(self.check.values(), self.check.keys()):
			if name in self.checkboxes.keys():
				self.checkboxes[name].setChecked(value)

				if name == 'settings.1.option.1':
					for i in range(2):
						self.checkboxes[f'settings.1.option.{i + 2}'].setEnabled(value)
		self.autoCheck = False
