from PyQt5.QtWidgets import (
	QWidget, QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QDesktopWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCloseEvent
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
# Version 1.6.1 (4.8.1)
# By WaiZhong
# MIT License
waix = 'WaiXCalc'
version = '1.6.1'


class WaiX(QMainWindow):
	def __init__(self):
		super().__init__()

		self.data = get_data()
		self.trans = get_trans()
		self.formula = self.data['formula']
		self.isResult = self.data['settings']['isResult']
		self.isInBracket = self.data['settings']['isInBracket']

		self.initUI()

	def initUI(self):

		vbox = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(vbox)
		self.setCentralWidget(widget)

		self.textEdit = QLabel()
		self.textUpdate()
		self.textEdit.setFont(mwFont)
		vbox.addWidget(self.textEdit)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu(self.trans['menu']['menubar1']['name'])
		editMenu = menubar.addMenu(self.trans['menu']['menubar2']['name'])
		helpMenu = menubar.addMenu(self.trans['menu']['menubar3']['name'])

		self.menus = [fileMenu, editMenu, helpMenu]
		menuNames = [
					self.trans['menu']['menubar1']['options'].values(),
					self.trans['menu']['menubar2']['options'].values(),
					self.trans['menu']['menubar3']['options'].values()
		]
		menuShortcuts = [
						['Ctrl+N', 'Ctrl+O', 'Ctrl+S', 'Ctrl+Q'],
						['Ctrl+X', 'Ctrl+C', 'Ctrl+V', 'Del'],
						['', 'Ctrl+H', 'Ctrl+F', 'Ctrl+A']
		]
		menuStatustips = [
						self.trans['menu']['menubar1']['statustip'].values(),
						self.trans['menu']['menubar2']['statustip'].values(),
						self.trans['menu']['menubar3']['statustip'].values()
		]
		menufuncs = [
					[self.openFormulaWin, self.openNewFormulaWin, self.openSettingsWin, self.close],
					[self.cut, self.copy, self.paste, self.delete],
					[self.openHelpWin, self.openHistoryWin, self.wholeFormula, self.about]
		]
		self.action_lst = []
		for menu, names, shortcuts, statustips, funcs in zip(
				self.menus, menuNames, menuShortcuts, menuStatustips, menufuncs
		):
			for name, shortcut, statusTip, func in zip(names, shortcuts, statustips, funcs):

				if name == '':
					continue
				elif name == self.trans['menu']['menubar1']['options']['option3'] or\
					name == self.trans['menu']['menubar1']['options']['option4'] or\
					name == self.trans['menu']['menubar3']['options']['option2'] or\
					name == self.trans['menu']['menubar3']['options']['option4']:
					menu.addSeparator()

				if name == self.trans['menu']['menubar3']['options']['option4']:
					action = QAction(QIcon('resource/images/image.JPG'), name, self)
				else:
					action = QAction(name, self)

				action.setShortcut(shortcut)
				action.setStatusTip(statusTip)
				action.triggered.connect(func)
				menu.addAction(action)
				self.action_lst.append(action)

		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(waix)
		self.resize(672, 0)
		self.setMaximumSize(self.width(), self.height())

		self.statusBar()
		self.center()
		self.show()

	def compute(self):
		self.data = get_data()

		if len(self.formula) > 2:
			if self.isInBracket:
				self.formula.append(')')
				self.isInBracket = False

			try:
				result = calculate(get_formula(''.join(self.formula)))
			except (ValueError, ZeroDivisionError):
				self.textEdit.setText(self.trans['calculateError'])
			else:
				self.isResult = True

				if self.data['settings']['_floatToFraction'] and type(result) == Decimal:
					result = Fraction(result)
				elif self.data['settings']['_fractionToFloat'] and type(result) == Fraction:
					result = float(str(result).split('/')[0]) / float(str(result).split('/')[1])

				if self.data['settings']['_enableRecordHistory']:
					self.data['history'].append(''.join([i + ' ' for i in self.formula]) + '=' + ' ' + str(result))
					save('data.json', self.data)
				self.formula = [str(result)]
				self.textUpdate()

	def clearEdit(self):
		self.isResult = False
		self.formula = ['0']
		self.textEdit.setText(self.formula[-1])

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(qr.topLeft())

	def plusminus(self):
		if self.formula[-1][0] != '-' and self.formula[-1] != '0' and self.formula[-1] not in symbol_lst:
			self.formula[-1] = '-' + self.formula[-1]
		elif self.formula[-1][0] == '-' and self.formula[-1] != '-':
			self.formula[-1] = self.formula[-1].strip('-')
		self.textUpdate()

	def number(self, num: str):
		if self.formula[-1][-1] != '/' or num != '0':
			if not self.isResult:
				if self.formula[-1] in symbol_lst \
						or self.formula[-1] in bracket_lst[0] or self.formula[-1] in bracket_lst[1]:
					self.formula.append(num)
				else:
					if self.formula == ['0'] or self.formula[-1] == '0':
						self.formula[-1] = num
					else:
						self.formula[-1] = self.formula[-1] + num
			else:
				self.isResult = False
				self.formula[-1] = num
			self.textUpdate()

	def symbol(self, symbol):
		self.isResult = False
		if self.formula[-1] not in symbol_lst:
			self.formula.append(symbol)
			self.textUpdate()
			if len(self.formula[-1]) >= 2:
				if self.formula[-2][-1] == '.':
					self.formula[-2] = self.formula[-2] + '0'
				elif self.formula[-2][-1] == '/':
					self.formula[-2] = self.formula[-2] + '1'
		else:
			self.formula[-1] = symbol
			self.textEdit.setText(self.formula[-1])

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Backspace:
			self.isResult = False
			if len(self.formula[-1]) == 2 and '-' in self.formula[-1]:
				self.formula[-1] = ''
				self.textUpdate()
				if len(self.formula) == 1:
					self.clearEdit()
				else:
					self.formula[-1] = '0'
					self.textUpdate()
			elif self.formula != '0' and self.formula[-1][-1] not in symbol_lst and len(self.formula[-1]) >= 2:
				self.formula[-1] = self.formula[-1][:-1]
				self.textUpdate()
			elif self.formula[-1] in symbol_lst:
				self.formula = self.formula[:-1]
				self.textUpdate()
			elif len(self.formula[-1]) == 1 and len(self.formula) >= 2:
				self.formula = self.formula[:-1]
				self.textUpdate()
			elif len(self.formula[-1]) == 1 and len(self.formula) == 1:
				self.clearEdit()
			elif self.isResult:
				self.clearEdit()
		elif e.key() == Qt.Key_Equal or e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
			self.compute()
		elif e.key() == Qt.Key_Plus:
			self.symbol('+')
		elif e.key() == Qt.Key_Minus:
			self.symbol('-')
		elif e.key() == Qt.Key_Asterisk:
			self.symbol('×')
		elif e.key() == Qt.Key_Colon:
			self.symbol('÷')
		elif e.key() == Qt.Key_BracketLeft:
			self.bracket('(')
		elif e.key() == Qt.Key_BracketRight:
			self.bracket(')')
		elif e.key() == Qt.Key_plusminus:
			self.plusminus()
		elif e.key() == Qt.Key_C:
			self.clearEdit()
		elif e.key() == Qt.Key_Percent:
			if self.formula[-1] != '0':
				try:
					self.formula[-1] = str(int(self.formula[-1]) / 100)
				except ValueError:
					self.formula[-1] = str(Decimal(self.formula[-1]) / 100)
				self.textUpdate()
		elif e.key() == Qt.Key_Period:
			if self.formula[-1] not in symbol_lst and '.' not in self.formula[-1]:
				self.formula[-1] = self.formula[-1] + '.'
				self.textUpdate()
		elif e.key() == Qt.Key_Slash:
			if self.formula[-1] not in symbol_lst and '/' not in self.formula[-1] and self.formula[-1] != '0':
				self.formula[-1] = self.formula[-1] + '/'
				self.textUpdate()
			elif self.formula[-1][-1] == '/':
				self.formula[-1] = self.formula[-1][:-1]
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

	def openFormulaWin(self):
		self.newWin = CreateFormulaWin(ex)
		self.newWin.show()

	def openNewFormulaWin(self):
		file = QFileDialog.getOpenFileName(self, self.trans['windowTitles']['selectFileWin'], '', '*.txt;;All Files(*)')
		try:
			with open(file[0], 'r') as f:
				f_formula = f.read()
				f_formulas = f_formula.split('\n')
				formulas = [get_formula(i) for i in f_formulas if isformula(get_formula(i))]
		except (FileNotFoundError, IndexError) as e:
			if type(e) == IndexError:
				QMessageBox.warning(
					self, self.trans['remindTexts']['title'], self.trans['remindTexts']['openedFormula']['remind4']
				)
		else:
			self.newWin = OpenedFormulaWin(formulas)
			self.newWin.show()

	def openSettingsWin(self):
		self.newWin = SettingsWin()
		self.newWin.signal.connect(self.updateLang)
		self.newWin.show()

	def openHistoryWin(self):
		self.data = get_data()

		if len(self.data['history']) != 0:
			self.newWin = HistoryWin()
			self.newWin.show()
		else:
			QMessageBox.information(
				self,
				self.trans['remindTexts']['historyEmpty']['title'],
				self.trans['remindTexts']['historyEmpty']['content'],
				QMessageBox.Ok, QMessageBox.Ok
			)

	def openHelpWin(self):
		self.newWin = HelpWin()
		self.newWin.show()

	def updateLang(self):
		self.data = get_data()
		self.trans = get_trans()
		menuNames = [
			self.trans['menu']['menubar1']['options'].values(),
			self.trans['menu']['menubar2']['options'].values(),
			self.trans['menu']['menubar3']['options'].values()
		]
		menuStatustips = [
			self.trans['menu']['menubar1']['statustip'].values(),
			self.trans['menu']['menubar2']['statustip'].values(),
			self.trans['menu']['menubar3']['statustip'].values()
		]

		for i in range(len(self.menus)):
			self.menus[i].setTitle(self.trans['menu'][f'menubar{i+1}']['name'])

		idx = 0
		for names, statustips in zip(menuNames, menuStatustips):
			for name, statustip in zip(names, statustips):
				self.action_lst[idx].setText(name)
				self.action_lst[idx].setStatusTip(statustip)
				idx += 1

	def cut(self):
		copy(''.join([i for i in self.formula]).strip())
		self.clearEdit()

	def copy(self):
		copy(''.join([i for i in self.formula]).strip())

	def paste(self):
		data: str = paste()
		if isformula(get_formula(data)):
			self.formula = get_formula(data)
			self.textUpdate()

	def delete(self):
		if len(self.formula) >= 2:
			self.formula = self.formula[:-1]
		else:
			self.clearEdit()
		self.textUpdate()

	def wholeFormula(self):
		p_formula = [i + ' ' for i in self.formula]
		QMessageBox.information(self, self.trans['windowTitles']['wholeFormulaBox'], ''.join(p_formula))

	def about(self):
		QMessageBox.about(
			self,
			self.trans['windowTitles']['aboutBox'],
			f'{waix}\nBy Github@WaiZhong\nVersion {version}\n'
		)
	
	def textUpdate(self):
		text_update(self.formula[-1], self.textEdit)

	def closeEvent(self, a0: QCloseEvent) -> None:
		try:
			self.newWin.close()
		except AttributeError:
			pass
		self.data['formula'] = self.formula
		self.data['settings']['isResult'] = self.isResult
		self.data['settings']['isInBracket'] = self.isInBracket
		save('data.json', self.data)


if __name__ == '__main__':
	app = QApplication(argv)
	ex = WaiX()
	exit(app.exec_())
