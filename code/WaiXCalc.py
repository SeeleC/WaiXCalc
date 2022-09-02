from PyQt5.QtWidgets import (
	QApplication, QMainWindow, QFileDialog, QAction, QDesktopWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent
from PyQt5.QtCore import Qt
from win32mica import ApplyMica, MICAMODE
from sys import argv, exit
from asyncio import run, create_task

from settingsWin import SettingsWin
from openedFormulaWin import OpenedFormulaWin
from historyWin import HistoryWin
from functions import *
from settings import *

# WaiXCalc (WaiX Calculator)
# By WaiZhong
# MIT License
# Source https://github.com/WaiZhong/WaiXCalc

# Python 3.9.12
# PyQt 5.15.6


class WaiX(QMainWindow):
	def __init__(self):
		super().__init__()

		self.options: dict = get_options()
		self.trans: dict = get_trans()
		self.data = get_data()
		self.history = get_history()

		self.isResult: bool = self.data['isResult']
		self.formula: list = self.data['formula']
		self.calc_formula: list = self.data['calcFormula']
		self.b_idx: list[int] = self.data['frontBracketIndex']
		self.calc_f_step: list = self.data['calcFormulaStep']
		self.b_idx_step: list = self.data['frontBracketIndexStep']

		self.clipboard = QApplication.clipboard()

		rFont.setFamily(self.options['font'])
		hFont.setFamily(self.options['font'])
		tFont.setFamily(self.options['font'])
		mFont.setFamily(self.options['font'])

		self.options['enableDarkMode'] = detect_dark_mode()
		save('data/options.json', self.options)

		self.init_ui()
		self.show()

		if self.calc_formula == ['0'] and self.formula != self.calc_formula:
			self.clear_edit()

	def init_ui(self):
		vbox = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(vbox)
		self.setCentralWidget(widget)

		self.textEdit = QLabel()
		self.text_update()
		self.textEdit.setFont(hFont)
		vbox.addWidget(self.textEdit)

		self.menubar = self.menuBar()
		self.menubar.setFont(mFont)
		fileMenu = self.menubar.addMenu(self.trans['menubar.fileMenu.title'])
		editMenu = self.menubar.addMenu(self.trans['menubar.editMenu.title'])
		helpMenu = self.menubar.addMenu(self.trans['menubar.helpMenu.title'])

		self.menus = [fileMenu, editMenu, helpMenu]
		names, statustips = get_menu_items(self.trans)
		functions = [
			[self.openNewFormulaWin, self.openSettingsWin, self.close],
			[self.cut, self.copy, self.paste, self.delete],
			[self.openHelpWin, self.openHistoryWin, self.whole_formula]
		]
		shortcuts = [
			['Ctrl+O', 'Ctrl+S', 'Ctrl+Q', ''],
			['Ctrl+X', 'Ctrl+C', 'Ctrl+V', 'Del'],
			['', 'Ctrl+H', 'Ctrl+F']
		]
		self.actions = []
		run(self.init_menubar(names, statustips, functions, shortcuts))

		self.setWindowIcon(QIcon('resource/images/icon.jpg'))
		self.setWindowTitle(self.options['window_title'])
		self.resize(672, 0)
		self.setMaximumSize(self.width(), self.height())

		if self.options['settings.4.option']:
			self.setAttribute(Qt.WA_TranslucentBackground)
			if self.options['enableDarkMode']:
				ApplyMica(int(self.winId()), MICAMODE.DARK)
			else:
				ApplyMica(int(self.winId()), MICAMODE.LIGHT)

		if self.data['latest_pos_x'] or self.data['latest_pos_y']:
			self.move(self.data['latest_pos_x'], self.data['latest_pos_y'])
		else:
			self.center()

		self.statusBar()

	async def init_menubar(self, names, status_tips, functions, shortcuts):
		task1 = create_task(
			self.init_menu(self.menus[0], names[0], status_tips[0], shortcuts[0], functions[0])
		)
		task2 = create_task(
			self.init_menu(self.menus[1], names[1], status_tips[1], shortcuts[1], functions[1])
		)
		task3 = create_task(
			self.init_menu(self.menus[2], names[2], status_tips[2], shortcuts[2], functions[2])
		)

		await task1
		await task2
		await task3

	async def init_menu(self, menu, names, status_tips, shortcuts, functions):
		for name, status_tip, shortcut, function in zip(names, status_tips, shortcuts, functions):
			if name == '':
				continue
			elif name == self.trans['option.fileMenu.2'] or name == self.trans['option.fileMenu.3'] or \
					name == self.trans['option.helpMenu.2']:
				menu.addSeparator()

			action = QAction(name, self)
			action.setShortcut(shortcut)
			action.setStatusTip(status_tip)
			action.triggered.connect(function)
			menu.addAction(action)
			self.actions.append(action)
		menu.setFont(mFont)

	def bracket(self, l_idx):
		if l_idx == 0 and (self.formula[-1] in symbol_lst or self.formula == ['0']):
			if self.formula == ['0']:
				self.formula_update('(')
			else:
				self.formula.append('(')
				self.calc_formula.append('(')
			self.b_idx.append(len(self.calc_formula)-1)
			self.b_idx.append(len(self.formula)-1)

		elif l_idx == 1 and self.formula[-1] not in symbol_lst and\
			self.formula[-1] not in bracket_lst[0]:
			self.calc_f_step.append(self.calc_formula[:])
			self.b_idx_step.append(self.b_idx[:])

			self.formula.append(')')
			self.calc_formula.append(')')

			self.calc_formula = self.calc_formula[:self.b_idx[-2]] + [self.calc_formula[self.b_idx[-2]+1:-1]]
			self.b_idx = self.b_idx[:-2]
		self.text_update()

	def calculate(self):
		if len(self.formula) > 2 and self.formula[-1] not in symbol_lst and\
			self.formula[-1][-1] not in symbol_lst_2 and self.formula[-1] not in bracket_lst[0]:

			while len(self.b_idx) != 0:
				self.bracket(1)

			try:
				result = calculate(self.calc_formula)
			except (ValueError, ZeroDivisionError):
				self.textEdit.setText(self.trans['text.main.error'])
			else:
				self.isResult = True

				if self.options['settings.1.option.2']:
					result = Fraction(result)
				elif self.options['settings.1.option.3']:
					result = float(str(result).split('/')[0]) / float(str(result).split('/')[1])

				if self.options['settings.2.option.1']:
					self.history.append(''.join([i + ' ' for i in self.formula]) + '= ' + str(result))

				self.clear_edit()
				self.formula = [str(result)]
				self.calc_formula = [str(result)]
				self.text_update()

	def center(self):
		qr = self.frameGeometry()
		QDesktopWidget().availableGeometry().center()
		qr.moveCenter(qr.topLeft())

	def clear_edit(self):
		self.formula = ['0']
		self.calc_formula = ['0']
		self.calc_f_step.clear()
		self.b_idx_step.clear()
		self.b_idx.clear()
		self.textEdit.setText(self.formula[-1])

	def closeEvent(self, a0: QCloseEvent) -> None:
		try:
			self.newWin.close()
		except AttributeError:
			pass

		self.data['isResult'] = self.isResult
		self.data['formula'] = self.formula
		self.data['calcFormula'] = self.calc_formula
		self.data['frontBracketIndex'] = self.b_idx
		self.data['calcFormulaStep'] = self.calc_f_step
		self.data['frontBracketIndexStep'] = self.b_idx_step

		self.options['latest_pos_x'] = self.pos().x()
		self.options['latest_pos_y'] = self.pos().y()

		save('data/options.json', self.options)
		save('data/cache.json', self.data)
		if self.options['settings.2.option.2']:
			save('data/history.json', self.history)

	def copy(self):
		self.clipboard.setText(''.join([i for i in self.formula]).strip())

	def cut(self):
		self.clipboard.setText(''.join([i for i in self.formula]).strip())
		self.clear_edit()

	def delete(self):
		if len(self.formula) >= 2:
			self.formula = self.formula[:-1]
			self.calc_formula = self.calc_f_step[:-1]
		else:
			self.clear_edit()
		self.text_update()

	def font_update(self):
		self.options = get_options()

		rFont.setFamily(self.options['font'])
		hFont.setFamily(self.options['font'])
		tFont.setFamily(self.options['font'])
		mFont.setFamily(self.options['font'])

		self.textEdit.setFont(hFont)
		self.menubar.setFont(mFont)

		for m in self.menus:
			m.setFont(mFont)

	def formula_update(self, content):
		self.isResult = False
		self.formula[-1] = content
		self.calc_formula[-1] = content

	def keyPressEvent(self, e: QKeyEvent):
		if e.key() == Qt.Key_Backspace:
			self.isResult = False
			if len(self.formula[-1]) == 2 and '-' in self.formula[-1]:
				if len(self.formula) == 1:
					self.clear_edit()
				else:
					self.formula_update('0')
					self.text_update()
			elif self.formula[-1] in bracket_lst[1]:
				self.formula = self.formula[:-1]
				self.calc_formula = self.calc_f_step.pop()
				self.b_idx = self.b_idx_step.pop()
				self.text_update()
			elif self.formula[-1][-1] not in symbol_lst and len(self.formula[-1]) >= 2:
				self.formula_update(self.formula[-1][:-1])
				self.text_update()
			elif len(self.formula[-1]) == 1 and len(self.formula) >= 2:
				self.formula = self.formula[:-1]
				self.calc_formula = self.calc_formula[:-1]
				self.text_update()
			elif (len(self.formula[-1]) == 1 and len(self.formula) == 1) or self.isResult:
				self.clear_edit()
		elif e.key() == Qt.Key_Equal or e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
			self.calculate()
		elif e.key() == Qt.Key_Plus:
			self.symbol('+')
		elif e.key() == Qt.Key_Minus:
			self.symbol('-')
		elif e.key() == Qt.Key_Asterisk:
			self.symbol('×')
		elif e.key() == Qt.Key_Colon:
			self.symbol('÷')
		elif e.key() == Qt.Key_ParenLeft or e.key() == Qt.Key_BracketLeft:
			self.bracket(0)
		elif e.key() == Qt.Key_ParenRight or e.key() == Qt.Key_BracketRight:
			self.bracket(1)
		elif e.key() == Qt.Key_plusminus:
			self.plusminus()
		elif e.key() == Qt.Key_C:
			self.clear_edit()
		elif e.key() == Qt.Key_Percent:
			if self.formula[-1] != '0':
				self.formula_update(str(Decimal(self.formula[-1]) / 100))
				self.text_update()
		elif e.key() == Qt.Key_Period:
			if self.formula[-1] not in symbol_lst and '.' not in self.formula[-1]:
				self.formula_update(self.formula[-1] + '.')
				self.text_update()
		elif e.key() == Qt.Key_Slash:
			if self.options['settings.1.option.1']:
				if self.formula[-1] not in symbol_lst and '/' not in self.formula[-1] and self.formula[-1] != '0':
					self.formula_update(self.formula[-1] + '/')
					self.text_update()
				elif self.formula[-1][-1] == '/':
					self.formula_update(self.formula[-1][:-1])
					self.symbol('÷')
			else:
				self.symbol('÷')
		elif e.key() == Qt.Key_1:
			self.number('1')
		elif e.key() == Qt.Key_2:
			self.number('2')
		elif e.key() == Qt.Key_3:
			self.number('3')
		elif e.key() == Qt.Key_4:
			self.number('4')
		elif e.key() == Qt.Key_5:
			self.number('5')
		elif e.key() == Qt.Key_6:
			self.number('6')
		elif e.key() == Qt.Key_7:
			self.number('7')
		elif e.key() == Qt.Key_8:
			self.number('8')
		elif e.key() == Qt.Key_9:
			self.number('9')
		elif e.key() == Qt.Key_0:
			self.number('0')

	def language_update(self):
		self.trans = get_trans()
		menu_names, menu_status_tips = get_menu_items(self.trans)

		for idx, name in zip([0, 1, 2], ['file', 'edit', 'help']):
			self.menus[idx].setTitle(self.trans[f'menubar.{name}Menu.title'])

		idx = 0
		for names, status_tips in zip(menu_names, menu_status_tips):
			for name, status_tip in zip(names, status_tips):
				self.actions[idx].setText(name)
				self.actions[idx].setStatusTip(status_tip)
				idx += 1

	def number(self, num: str):
		if self.formula[-1][-1] != '/' or num != '0':
			if not self.isResult and self.formula[-1] not in bracket_lst[1]:
				if self.formula[-1] in symbol_lst or self.formula[-1] in bracket_lst[0]:
					self.formula.append(num)
					self.calc_formula.append(num)
				else:
					if self.formula == ['0'] or self.formula[-1] == '0':
						self.formula_update(num)
					else:
						self.formula_update(self.formula[-1] + num)
			else:
				self.isResult = False
				self.formula_update(num)
			self.text_update()

	def openHelpWin(self):
		get_translated_messagebox(
			QMessageBox.Icon.NoIcon,
			self.trans['window.help.title'],
			self.trans['text.help.content'],
			self,
			self.options['enableDarkMode']
		).show()

	def openHistoryWin(self):
		if len(self.history) != 0:
			self.newWin = HistoryWin(self.history)
			self.newWin.show()
		else:
			get_translated_messagebox(
				QMessageBox.Icon.Information,
				self.trans['hint.history.title'],
				self.trans['hint.history.empty'],
				self,
				self.options['enableDarkMode']
			).show()

	def openNewFormulaWin(self):
		file = QFileDialog.getOpenFileName(self, self.trans['window.selectFile.title'], '', '*.txt;;All Files(*)')
		try:
			with open(file[0], 'r') as f:
				f_formula = f.read()
				f_formulas = f_formula.split('\n')
				formulas = [get_formula(i) for i in f_formulas if isformula(get_formula(i))]
		except (FileNotFoundError, IndexError) as e:
			if type(e) == IndexError:
				get_translated_messagebox(
					QMessageBox.Icon.Warning,
					self.trans['window.hint.title'],
					self.trans['hint.open.error'],
					self,
					self.options['enableDarkMode']
				).show()
		else:
			self.newWin = OpenedFormulaWin(formulas)
			self.newWin.show()

	def openSettingsWin(self):
		self.newWin = SettingsWin()
		self.newWin.language_signal.connect(self.language_update)
		self.newWin.options_signal.connect(self.options_update)
		self.newWin.font_signal.connect(self.font_update)
		self.newWin.title_signal.connect(self.title_update)
		self.newWin.show()

	def options_update(self):
		self.options = get_options()

	def paste(self):
		text: str = self.clipboard.text()
		if isformula(get_formula(text)):
			if self.formula[-1] in symbol_lst or self.formula[-1] in bracket_lst[0]:
				self.formula += get_formula(text)
				self.calc_formula += get_formula(text)
			else:
				self.formula = get_formula(text)
				self.calc_formula = get_formula(text)
			self.text_update()

	def plusminus(self):
		if self.formula[-1][0] != '-' and self.formula[-1] != '0' and self.formula[-1] not in symbol_lst and\
			self.formula[-1][-1] not in [i for _ in bracket_lst for i in _]:
			self.formula_update('-' + self.formula[-1])
		elif self.formula[-1][0] == '-' and self.formula[-1] != '-':
			self.formula_update(self.formula[-1].lstrip('-'))
		self.text_update()

	def symbol(self, symbol):
		self.isResult = False
		if self.formula[-1] not in symbol_lst and self.formula[-1] not in bracket_lst[0] and\
			self.formula[-1] not in symbol_lst_2:
			self.formula.append(symbol)
			self.calc_formula.append(symbol)
		else:
			self.formula_update(symbol)
		self.text_update()

	def text_update(self):
		text_update(self.formula[-1], self.textEdit)

	def title_update(self):
		self.options = get_options()
		self.setWindowTitle(self.options['window_title'])

	def whole_formula(self):
		f = [i + ' ' for i in self.formula]
		get_translated_messagebox(
			QMessageBox.Icon.NoIcon,
			self.trans['window.whole.title'],
			''.join(f),
			self,
			self.options['enableDarkMode']
		).show()


if __name__ == '__main__':
	app = QApplication(argv)
	ex = WaiX()
	exit(app.exec_())
