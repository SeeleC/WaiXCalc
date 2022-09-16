from typing import Iterable
from PyQt5.QtWidgets import (
	QTabWidget, QWidget, QVBoxLayout, QRadioButton, QCheckBox, QHBoxLayout, QScrollArea, QPushButton, QMessageBox,
	QLabel, QLineEdit, QComboBox
)
from PyQt5.QtGui import QIcon, QFontDatabase, QPixmap, QCloseEvent
from PyQt5.QtCore import Qt, pyqtSignal
from asyncio import run, create_task
from sys import getwindowsversion
from httpx import get, HTTPStatusError, NetworkError

from colorModeDetect import Detector
from config import __version__, tFont, rFont
from functions import (
	save, get_trans, get_options, get_trans_entry, get_trans_info, get_data, get_enhanced_messagebox, load_theme,
	switch_color_mode
)


class Settings(QTabWidget):
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
		self.color_modes = {
			j: i
			for i, j in get_trans_entry(self.trans, 'colorMode').items()
		}
		self.languages = get_trans_info()
		self.checkboxes: dict[str: QCheckBox] = {}
		self.radiobuttons: dict[str: QRadioButton] = {}
		self.selectors: dict[str: QComboBox] = {}
		self.autoCheck = False
		self.changeLanguage = False
		self.changedFont = ''

		self.detector = Detector(self)
		self.detector.colorModeChanged.connect(self.detect_dark_mode)
		self.detector.start()

		self.init_ui()

	languageChanged = pyqtSignal()
	fontChanged = pyqtSignal()
	optionsChanged = pyqtSignal()
	titleChanged = pyqtSignal()
	colorOptionChanged = pyqtSignal()
	windowClose = pyqtSignal()

	def init_ui(self):
		run(self.init_tabs())

		load_theme(self)

		self.setFont(rFont)
		self.setWindowIcon(QIcon('resources/images/icon.jpg'))
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
		widget.setFont(rFont)

		hbox = QHBoxLayout()
		hbox.addWidget(widget)
		hbox.addStretch(1)
		layout.addLayout(hbox)
		return layout

	def add_enter_entry(self, layout: QVBoxLayout, title: str, widget: QLineEdit, text: str = '') -> QVBoxLayout:
		widget.setText(text)
		widget.setFont(rFont)

		hbox = QHBoxLayout()

		title_label = QLabel(title + ':')
		title_label.setFont(rFont)
		hbox.addWidget(title_label)
		hbox.addStretch(1)

		layout.addLayout(hbox)
		layout.addWidget(widget)

		return layout

	def add_selector_entry(self, layout: QVBoxLayout, title: str, flag: str, items: Iterable, current_text: str):
		hbox = QHBoxLayout()

		label = QLabel(title + ' :')
		label.setFont(rFont)
		hbox.addWidget(label)

		self.selectors[flag] = QComboBox()
		self.selectors[flag].addItems(items)
		self.selectors[flag].setCurrentText(current_text)
		self.selectors[flag].setFont(rFont)
		hbox.addWidget(self.selectors[flag])

		hbox.addStretch(1)
		layout.addLayout(hbox)

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
		layout = QVBoxLayout()
		for i, j in get_trans_entry(self.trans, 'settings.1.option').items():
			self.checkboxes[i] = QCheckBox(j)
			layout = self.add_option_entry(layout, self.checkboxes[i])
		return layout

	def closeEvent(self, a0: QCloseEvent) -> None:
		self.detector.exit()
		self.windowClose.emit()

	def detect_dark_mode(self):
		switch_color_mode(self)

	def history_tab(self) -> QVBoxLayout:
		layout = QVBoxLayout()
		for i, j in get_trans_entry(self.trans, 'settings.2.option').items():
			self.checkboxes[i] = QCheckBox(j)
			layout = self.add_option_entry(layout, self.checkboxes[i])
		return layout

	def language_tab(self) -> QVBoxLayout:
		layout = QVBoxLayout()

		for name, id in get_trans_info().items():
			self.radiobuttons[id] = QRadioButton(name)
			layout = self.add_option_entry(layout, self.radiobuttons[id])

			if id == self.options['language']:
				self.radiobuttons[id].setChecked(True)

		return layout

	def style_tab(self) -> QVBoxLayout:
		layout = QVBoxLayout()

		if not getwindowsversion().build < 22000:
			self.checkboxes['settings.4.option'] = QCheckBox(self.trans['settings.4.option'])
			layout = self.add_option_entry(layout, self.checkboxes['settings.4.option'])

		self.add_selector_entry(
			layout,
			self.trans['settings.4.selector.2'],
			'settings.4.selector.2',
			[self.trans[i] for i in get_trans_entry(self.trans, 'colorMode')],
			self.trans[self.options['settings.4.selector.2']]
		)

		database = QFontDatabase()
		self.add_selector_entry(
			layout,
			self.trans['settings.4.selector.1'],
			'settings.4.selector.1',
			database.families(),
			self.options['settings.4.selector.1']
		)

		self.window_title = QLineEdit()
		self.add_enter_entry(layout, self.trans['settings.4.text'], self.window_title, self.options['window_title'])

		return layout

	def about_tab(self) -> QVBoxLayout:
		outer_vbox = QVBoxLayout()
		outer_vbox.addStretch(1)

		hbox = QHBoxLayout()
		hbox.addStretch(1)

		inner_vbox = QVBoxLayout()
		inner_vbox.addStretch(1)

		image = QLabel()
		image.setPixmap(QPixmap('resources/images/icon.jpg'))
		image.setFixedSize(100, 100)
		image.setScaledContents(True)
		inner_vbox.addWidget(image)

		label = QLabel(f'WaiXCalc\nBy Github@SeeleC\nVersion {__version__}\n')
		label.setFont(tFont)
		inner_vbox.addWidget(label)

		button = QPushButton(self.trans['settings.5.button'])
		button.setFont(rFont)
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
		ok.setFont(rFont)
		ok.setShortcut('Return')
		ok.clicked.connect(self.clicked)

		cancel = QPushButton(self.trans['button.cancel'])
		cancel.setFont(rFont)
		cancel.setShortcut('Escape')
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
					get_enhanced_messagebox(
						QMessageBox.Icon.Information,
						self.trans['window.hint.title'],
						self.trans['settings.4.hint'],
						self,
						self.data['enableDarkMode']
					).show()

				for i in self.check.keys():
					self.options[i] = self.check[i]
				for i in self.radiobuttons.values():
					if i.isChecked() and self.languages[i.text()] != self.options['language']:
						self.options['language'] = self.languages[i.text()]
						save('data/options.json', self.options)
						self.languageChanged.emit()
						break
				for i in self.selectors.keys():
					if i == 'settings.4.selector.1' and self.selectors[i].currentText() != self.options['settings.4.selector.1']:
						self.options['settings.4.selector.1'] = self.selectors[i].currentText()
						save('data/options.json', self.options)
						self.fontChanged.emit()
					elif i == 'settings.4.selector.2' and self.selectors[i].currentText() != self.options[i]:
						self.options[i] = self.color_modes[self.selectors[i].currentText()]
						save('data/options.json', self.options)
						self.colorOptionChanged.emit()

				if self.window_title.text() != self.options['window_title']:
					self.options['window_title'] = self.window_title.text()
					save('data/options.json', self.options)
					self.titleChanged.emit()

				save('data/options.json', self.options)
				self.optionsChanged.emit()
		elif sender.text() == self.trans['settings.5.button']:
			try:
				r = get('https://api.github.com/repos/SeeleC/WaiXCalc/releases/latest')
				r.raise_for_status()
			except (HTTPStatusError, NetworkError, KeyError) as e:
				get_enhanced_messagebox(
					QMessageBox.Icon.Information,
					self.trans['settings.5.button'],
					self.trans['settings.5.hint.3'] + ': ' + str(repr(e)),
					self,
					self.data['enableDarkMode']
				).show()
			else:
				latest_version = r.json()['tag_name'][1:]
				if latest_version == __version__:
					get_enhanced_messagebox(
						QMessageBox.Icon.Information,
						self.trans['settings.5.button'],
						self.trans['settings.5.hint.1'],
						self,
						self.data['enableDarkMode']
					).show()
				else:
					get_enhanced_messagebox(
						QMessageBox.Icon.Information,
						self.trans['settings.5.button'],
						self.trans['settings.5.hint.2'] % latest_version,
						self,
						self.data['enableDarkMode']
					).show()

	def update_status(self):
		self.autoCheck = True
		for value, name in zip(self.check.values(), self.check.keys()):
			if name in self.checkboxes.keys():
				self.checkboxes[name].setChecked(value)

				if name == 'settings.1.option.1':
					for i in range(2):
						self.checkboxes[f'settings.1.option.{i + 2}'].setEnabled(value)
		self.autoCheck = False
