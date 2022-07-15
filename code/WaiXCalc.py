from PyQt5.QtWidgets import (
	QWidget, QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QDesktopWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCloseEvent, QKeyEvent
from PyQt5.QtCore import Qt
from sys import argv, exit
from pyperclip import paste, copy

from createFormulaWin import CreateFormulaWin
from historyWin import HistoryWin
from settingsWin import SettingsWin
from openedFormulaWin import OpenedFormulaWin
from helpWin import HelpWin
from functions import *
from settings import *

# WaiXCalc (WaiX Calculator)
# Version 1.8.0 (4.10.0)
# By WaiZhong
# MIT License
# Source https://github.com/WaiZhong/WaiXCalc
# Python 3.9.12
# PyQt 5.15.6

version = '1.8.0'


class WaiX(QMainWindow):
	def __init__(self):
		super().__init__()

		self.data: dict = get_data()
		self.trans: dict = get_trans()
		self.formula_data = get_formula_data()

		self.isResult: bool = self.data['isResult']
		self.formula: list = self.formula_data['formula']
		self.calc_formula: list = self.formula_data['calcFormula']
		self.b_idx: list[int] = self.formula_data['frontBracketIndex']
		self.calc_f_step: list = self.formula_data['calcFormulaStep']
		self.b_idx_step: list = self.formula_data['frontBracketIndexStep']

		font.setFamily(self.data['font'])
		mwFont.setFamily(self.data['font'])
		textFont.setFamily(self.data['font'])

		self.initUI()

		if self.calc_formula == ['0'] and self.formula != self.calc_formula:
			self.clear_edit()

	def initUI(self):
		vbox = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(vbox)
		self.setCentralWidget(widget)

		self.textEdit = QLabel()
		self.text_update()
		self.textEdit.setFont(mwFont)
		vbox.addWidget(self.textEdit)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu(self.trans['menubar.fileMenu.title'])
		editMenu = menubar.addMenu(self.trans['menubar.editMenu.title'])
		helpMenu = menubar.addMenu(self.trans['menubar.helpMenu.title'])

		self.menus = [fileMenu, editMenu, helpMenu]
		menuNames = [
			[
				self.trans['option.fileMenu.1'],
				self.trans['option.fileMenu.2'],
				self.trans['option.fileMenu.3']
			],
			[
				self.trans['option.editMenu.1'],
				self.trans['option.editMenu.2'],
				self.trans['option.editMenu.3'],
				self.trans['option.editMenu.4']
			],
			[
				self.trans['option.helpMenu.1'],
				self.trans['option.helpMenu.2'],
				self.trans['option.helpMenu.3'],
				self.trans['option.helpMenu.4']
			],
		]
		menuShortcuts = [
						['Ctrl+O', 'Ctrl+S', 'Ctrl+Q', ''],
						['Ctrl+X', 'Ctrl+C', 'Ctrl+V', 'Del'],
						['', 'Ctrl+H', 'Ctrl+F', 'Ctrl+A']
		]
		menuStatustips = [
			[
				self.trans['statusTip.fileMenu.1'],
				self.trans['statusTip.fileMenu.2'],
				self.trans['statusTip.fileMenu.3'],
			],
			[
				self.trans['statusTip.editMenu.1'],
				self.trans['statusTip.editMenu.2'],
				self.trans['statusTip.editMenu.3'],
				self.trans['statusTip.editMenu.4'],
			],
			[
				self.trans['statusTip.helpMenu.1'],
				self.trans['statusTip.helpMenu.2'],
				self.trans['statusTip.helpMenu.3'],
				self.trans['statusTip.helpMenu.4'],
			],
		]
		menufuncs = [
					[self.openNewFormulaWin, self.openSettingsWin, self.close],
					[self.cut, self.copy, self.paste, self.delete],
					[self.openHelpWin, self.openHistoryWin, self.whole_formula, self.about]
		]
		self.action_lst = []
		for menu, names, shortcuts, statustips, funcs in zip(
				self.menus, menuNames, menuShortcuts, menuStatustips, menufuncs
		):
			for name, shortcut, statusTip, func in zip(names, shortcuts, statustips, funcs):

				if name == '':
					continue
				elif name == self.trans['statusTip.fileMenu.3'] or name == self.trans['statusTip.fileMenu.4'] or\
					name == self.trans['statusTip.helpMenu.2'] or name == self.trans['statusTip.helpMenu.4']:
					menu.addSeparator()

				if name == self.trans['option.helpMenu.4']:
					action = QAction(QIcon('resource/images/image.JPG'), name, self)
				else:
					action = QAction(name, self)

				action.setShortcut(shortcut)
				action.setStatusTip(statusTip)
				action.triggered.connect(func)
				menu.addAction(action)
				self.action_lst.append(action)

		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(self.data['window_title'])
		self.resize(672, 0)
		self.setMaximumSize(self.width(), self.height())

		if self.data['qss_code']:
			self.setStyleSheet(self.data['qss_code'])

		self.statusBar()
		self.center()
		self.show()

	def about(self):
		QMessageBox.about(
			self,
			self.trans['window.about.title'],
			f'WaiXCalc\nBy Github@WaiZhong\nVersion {version}\n'
		)

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

				if self.data['settings']['settings.1.option.2']:
					result = Fraction(result)
				elif self.data['settings']['settings.1.option.3']:
					result = float(str(result).split('/')[0]) / float(str(result).split('/')[1])

				if self.data['settings']['settings.2.option']:
					history = get_history()
					history.append(''.join([i + ' ' for i in self.formula]) + '=' + ' ' + str(result))
					save('data/history.json', history)

				self.clear_edit()
				self.formula = [str(result)]
				self.calc_formula = [str(result)]
				self.text_update()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
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
		self.formula_data['formula'] = self.formula
		self.formula_data['calcFormula'] = self.calc_formula
		self.formula_data['frontBracketIndex'] = self.b_idx
		self.formula_data['calcFormulaStep'] = self.calc_f_step
		self.formula_data['frontBracketIndexStep'] = self.b_idx_step
		save('data/data.json', self.data)
		save('data/formula_data.json', self.formula_data)

	def copy(self):
		copy(''.join([i for i in self.formula]).strip())

	def cut(self):
		copy(''.join([i for i in self.formula]).strip())
		self.clear_edit()

	def delete(self):
		if len(self.formula) >= 2:
			self.formula = self.formula[:-1]
			self.calc_formula = self.calc_f_step[:-1]
		else:
			self.clear_edit()
		self.text_update()

	def font_update(self):
		self.data = get_data()

		font.setFamily(self.data['font'])
		mwFont.setFamily(self.data['font'])
		textFont.setFamily(self.data['font'])

		self.textEdit.setFont(mwFont)

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
			if self.data['settings']['settings.1.option.1']:
				if self.formula[-1] not in symbol_lst and '/' not in self.formula[-1] and self.formula[-1] != '0':
					self.formula_update(self.formula[-1] + '/')
					self.text_update()
				elif self.formula[-1][-1] == '/':
					self.formula_update(self.formula[-1][:-1])
					self.symbol('÷')
			else:
				self.symbol('÷')
		elif e.key() == Qt.Key_1 or e.key() == Qt.Key_Launch1:
			self.number('1')
		elif e.key() == Qt.Key_2 or e.key() == Qt.Key_Launch2:
			self.number('2')
		elif e.key() == Qt.Key_3 or e.key() == Qt.Key_Launch3:
			self.number('3')
		elif e.key() == Qt.Key_4 or e.key() == Qt.Key_Launch4:
			self.number('4')
		elif e.key() == Qt.Key_5 or e.key() == Qt.Key_Launch5:
			self.number('5')
		elif e.key() == Qt.Key_6 or e.key() == Qt.Key_Launch6:
			self.number('6')
		elif e.key() == Qt.Key_7 or e.key() == Qt.Key_Launch6:
			self.number('7')
		elif e.key() == Qt.Key_8 or e.key() == Qt.Key_Launch8:
			self.number('8')
		elif e.key() == Qt.Key_9 or e.key() == Qt.Key_Launch9:
			self.number('9')
		elif e.key() == Qt.Key_0 or e.key() == Qt.Key_Launch0:
			self.number('0')

	def language_update(self):
		self.trans = get_trans()
		menuNames = [
			[
				self.trans['option.fileMenu.1'],
				self.trans['option.fileMenu.2'],
				self.trans['option.fileMenu.3'],
			],
			[
				self.trans['option.editMenu.1'],
				self.trans['option.editMenu.2'],
				self.trans['option.editMenu.3'],
				self.trans['option.editMenu.4']
			],
			[
				self.trans['option.helpMenu.1'],
				self.trans['option.helpMenu.2'],
				self.trans['option.helpMenu.3'],
				self.trans['option.helpMenu.4']
			],
		]
		menuStatustips = [
			[
				self.trans['statusTip.fileMenu.1'],
				self.trans['statusTip.fileMenu.2'],
				self.trans['statusTip.fileMenu.3'],
			],
			[
				self.trans['statusTip.editMenu.1'],
				self.trans['statusTip.editMenu.2'],
				self.trans['statusTip.editMenu.3'],
				self.trans['statusTip.editMenu.4'],
			],
			[
				self.trans['statusTip.helpMenu.1'],
				self.trans['statusTip.helpMenu.2'],
				self.trans['statusTip.helpMenu.3'],
				self.trans['statusTip.helpMenu.4'],
			],
		]

		for idx, name in zip([0, 1, 2], ['file', 'edit', 'help']):
			self.menus[idx].setTitle(self.trans[f'menubar.{name}Menu.title'])

		idx = 0
		for names, statustips in zip(menuNames, menuStatustips):
			for name, statustip in zip(names, statustips):
				self.action_lst[idx].setText(name)
				self.action_lst[idx].setStatusTip(statustip)
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
		self.newWin = HelpWin()
		self.newWin.show()

	def openHistoryWin(self):
		history = get_history()

		if len(history) != 0:
			self.newWin = HistoryWin()
			self.newWin.show()
		else:
			QMessageBox.information(
				self,
				self.trans['hint.history.empty.title'],
				self.trans['hint.history.empty.content'],
				QMessageBox.Ok, QMessageBox.Ok
			)

	def openNewFormulaWin(self):
		file = QFileDialog.getOpenFileName(self, self.trans['window.selectFile.title'], '', '*.txt;;All Files(*)')
		try:
			with open(file[0], 'r') as f:
				f_formula = f.read()
				f_formulas = f_formula.split('\n')
				formulas = [get_formula(i) for i in f_formulas if isformula(get_formula(i))]
		except (FileNotFoundError, IndexError) as e:
			if type(e) == IndexError:
				QMessageBox.warning(
					self, self.trans['window.hint.title'], self.trans['hint.open.error']
				)
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
		self.data = get_data()

	def paste(self):
		data: str = paste()
		if isformula(get_formula(data)):
			if self.formula[-1] in symbol_lst or self.formula[-1] in bracket_lst[0]:
				self.formula += get_formula(data)
				self.calc_formula += get_formula(data)
			else:
				self.formula = get_formula(data)
				self.calc_formula = get_formula(data)
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
		self.data = get_data()
		self.setWindowTitle(self.data['window_title'])

	def whole_formula(self):
		p_formula = [i + ' ' for i in self.formula]
		QMessageBox.information(self, self.trans['window.whole.title'], ''.join(p_formula))


if __name__ == '__main__':
	app = QApplication(argv)
	ex = WaiX()
	exit(app.exec_())
