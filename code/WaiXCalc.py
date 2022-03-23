from PyQt5.QtWidgets import (
	QWidget, QApplication, QMainWindow, QFileDialog, QAction, QMessageBox, QDesktopWidget, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import Qt
from sys import argv, exit
from pyperclip import paste, copy

from formulaWin import FormulaWin
from historyWin import HistoryWin
from settingsWin import SettingsWin
from OpenedFormulaWin import OpenedFormulaWin
from helpWin import HelpWin
from functions import *
from settings import *

# Name <WaiX Calculator>
# Version 1.4.0 (4.6.0)
# By WaiZhong
waix = 'WaiX Calculator'
version = '1.4.0'


class WaiX(QMainWindow):
	def __init__(self):
		super().__init__()
		self.formula = data['formula']
		self.isResult = False
		self.initUI()

	def initUI(self):
		self.textFont = QFont()
		self.textFont.setFamily('微软雅黑')
		self.textFont.setPointSize(20)

		vbox = QVBoxLayout()
		widget = QWidget()
		widget.setLayout(vbox)
		self.setCentralWidget(widget)

		self.textEdit = QLabel()
		textUpdate(self.formula[-1], self.textEdit)
		self.textEdit.setFont(self.textFont)
		vbox.addWidget(self.textEdit)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('文件(&F)')
		editMenu = menubar.addMenu('编辑(&E)')
		historyMenu = menubar.addMenu('历史(&H)')
		helpMenu = menubar.addMenu('帮助(&S)')

		menus = [fileMenu, editMenu, historyMenu, helpMenu]
		menuNames = [
					['新建..(&N)', '打开..(&O)', '设置..(&S)', '退出(&X)'],
					['剪切(&T)', '复制(&C)', '粘贴(&P)', '删除(&D)'],
					['历史记录(&H)', '清空历史..', ''],
					['帮助(&H)', '完整算式(&W)', '关于(&A)', '']
		]
		menuShortcuts = [
						['Ctrl+N', 'Ctrl+O', 'Ctrl+S', 'Ctrl+Q'],
						['Ctrl+X', 'Ctrl+C', 'Ctrl+V', 'Del'],
						['Ctrl+H', 'Ctrl+Shift+D'],
						['', 'Ctrl+F', 'Ctrl+A']
		]
		menuStatusTips = [
						['新建完整算式', '打开包含算式的文本文件', '编辑应用设置', '退出WaiX Calculator'],
						['剪切到剪贴板', '复制到剪贴板', '从剪贴板粘贴', '删除当前计算步骤'],
						['计算的历史记录', '清空历史记录'],
						['显示帮助内容', '查看当前的完整算式', '关于WaiX Calculator']
		]
		menuFuncs = [
					[self.openFormulaWin, self.openNewFormulaWin, self.openSettingsWin, self.close],
					[self.cut, self.copy, self.paste, self.delete],
					[self.openHistoryWin, self.clear_history],
					[self.openHelpWin, self.wholeFormula, self.about]
		]
		for menu, names, shortcuts, statustips, funcs in zip(menus, menuNames, menuShortcuts, menuStatusTips, menuFuncs):
			for name, shortcut, statusTip, func in zip(names, shortcuts, statustips, funcs):
				if name == '':
					continue
				elif name == '清空历史..' or name == '退出' or name == '设置..' or name == '完整算式':
					menu.addSeparator()
				if name == '关于':
					action = QAction(QIcon('images\\image.JPG'), name, self)
				else:
					action = QAction(name, self)
				action.setShortcut(shortcut)
				action.setStatusTip(statusTip)
				action.triggered.connect(func)
				menu.addAction(action)

		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.setWindowTitle(waix)
		self.resize(672, 0)
		self.setMaximumSize(self.width(), self.height())

		self.statusBar()
		self.center()
		self.show()

	def compute(self):
		if len(self.formula) > 2:
			try:
				result = compute(self.formula)
			except (ValueError, ZeroDivisionError):
				self.textEdit.setText('错误')
			else:
				self.isResult = True

				if data['options']['_floatToFraction'] and type(result) == Decimal:
					result = Fraction(result)
				elif data['options']['_fractionToFloat'] and type(result) == Fraction:
					result = float(str(result).split('/')[0]) / float(str(result).split('/')[1])

				data['history'].append(''.join([i + ' ' for i in self.formula]) + '=' + ' ' + str(result))
				save('data.npy', data, allow_pickle=True, fix_imports=True)
				self.formula = [str(result)]
				textUpdate(str(result), self.textEdit)

	def clearEdit(self):
		self.isResult = False
		self.formula = ['0']
		self.textEdit.setText(self.formula[-1])

	def clear_history(self):
		if QMessageBox.question(self, '提示', '确定要清空历史吗', QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel) \
			== QMessageBox.Ok:
			data['history'] = []
			save('data.npy', data, allow_pickle=True, fix_imports=True)
			QMessageBox.information(self, '提示', '已清空历史记录', QMessageBox.Ok, QMessageBox.Ok)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(qr.topLeft())

	def plusminus(self):
		if self.formula[-1][0] != '-' and self.formula[-1] != '0' and self.formula[-1] not in symbol_lst:
			self.formula[-1] = '-' + self.formula[-1]
		elif self.formula[-1][0] == '-' and self.formula[-1] != '-':
			self.formula[-1] = self.formula[-1].strip('-')
		textUpdate(self.formula[-1], self.textEdit)

	def addNum(self, num: str):
		if self.formula[-1][-1] != '/' or num != '0':
			if not self.isResult:
				if self.formula[-1] in symbol_lst:
					self.formula.append(num)
				else:
					if self.formula == ['0'] or self.formula[-1] == '0':
						self.formula[-1] = num
					else:
						self.formula[-1] = self.formula[-1] + num
			else:
				self.isResult = False
				self.formula[-1] = num
			textUpdate(self.formula[-1], self.textEdit)

	def symbol(self, symbol):
		self.isResult = False
		if self.formula[-1] not in symbol_lst:
			self.formula.append(symbol)
			textUpdate(self.formula[-1], self.textEdit)
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
			if len(self.formula[-1]) <= 2 and '-' in self.formula[-1]:
				self.formula[-1] = ''
				textUpdate(self.formula[-1], self.textEdit)
				if len(self.formula) == 1:
					self.clearEdit()
				else:
					self.formula[-1] = '0'
					textUpdate(self.formula[-1], self.textEdit)
			elif self.formula != '0' and self.formula[-1][-1] not in symbol_lst and len(self.formula[-1]) >= 2:
				self.formula[-1] = self.formula[-1][:-1]
				textUpdate(self.formula[-1], self.textEdit)
			elif self.formula[-1] in symbol_lst:
				self.formula = self.formula[:-1]
				textUpdate(self.formula[-1], self.textEdit)
			elif len(self.formula[-1]) == 1 and len(self.formula) >= 2:
				self.formula = self.formula[:-1]
				textUpdate(self.formula[-1], self.textEdit)
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
				textUpdate(self.formula[-1], self.textEdit)
		elif e.key() == Qt.Key_Period:
			if self.formula[-1] not in symbol_lst and '.' not in self.formula[-1]:
				self.formula[-1] = self.formula[-1] + '.'
				textUpdate(self.formula[-1], self.textEdit)
		elif e.key() == Qt.Key_Slash:
			if self.formula[-1] not in symbol_lst and '/' not in self.formula[-1] and self.formula[-1] != '0':
				self.formula[-1] = self.formula[-1] + '/'
				textUpdate(self.formula[-1], self.textEdit)
			elif self.formula[-1][-1] == '/':
				self.formula[-1] = self.formula[-1][:-1]
				self.symbol('÷')
		elif e.key() == Qt.Key_1 or e.key() == Qt.Key_Launch1:
			self.addNum('1')
		elif e.key() == Qt.Key_2 or e.key() == Qt.Key_Launch2:
			self.addNum('2')
		elif e.key() == Qt.Key_3 or e.key() == Qt.Key_Launch3:
			self.addNum('3')
		elif e.key() == Qt.Key_4 or e.key() == Qt.Key_Launch4:
			self.addNum('4')
		elif e.key() == Qt.Key_5 or e.key() == Qt.Key_Launch5:
			self.addNum('5')
		elif e.key() == Qt.Key_6 or e.key() == Qt.Key_Launch6:
			self.addNum('6')
		elif e.key() == Qt.Key_7 or e.key() == Qt.Key_Launch6:
			self.addNum('7')
		elif e.key() == Qt.Key_8 or e.key() == Qt.Key_Launch8:
			self.addNum('8')
		elif e.key() == Qt.Key_9 or e.key() == Qt.Key_Launch9:
			self.addNum('9')
		elif e.key() == Qt.Key_0 or e.key() == Qt.Key_Launch0:
			self.addNum('0')

	def openFormulaWin(self):
		self.newWin = FormulaWin(ex)
		self.newWin.show()

	def openNewFormulaWin(self):
		file = QFileDialog.getOpenFileName(self, '文件', '', '*.txt;;All Files(*)')
		try:
			with open(file[0], 'r') as f:
				f_formula = f.read()
				f_formulas = f_formula.split('\n')
				formulas = [get_formula(i) for i in f_formulas if isformula(get_formula(i))]
		except (FileNotFoundError, IndexError) as e:
			if type(e) == IndexError:
				QMessageBox.warning(self, '提示', '错误')
		else:
			self.newWin = OpenedFormulaWin(formulas)
			self.newWin.show()

	def openSettingsWin(self):
		self.newWin = SettingsWin()
		self.newWin.show()

	def openHistoryWin(self):
		if len(data['history']) != 0:
			self.newWin = HistoryWin()
			self.newWin.show()
		else:
			QMessageBox.warning(self, '历史', '历史为空', QMessageBox.Ok, QMessageBox.Ok)

	def openHelpWin(self):
		self.newWin = HelpWin()
		self.newWin.show()

	def cut(self):
		copy(''.join([i for i in self.formula]).strip())
		self.clearEdit()

	def copy(self):
		copy(''.join([i for i in self.formula]).strip())

	def paste(self):
		data: str = paste()
		if isformula(get_formula(data)):
			self.formula = get_formula(data)
			textUpdate(self.formula[-1], self.textEdit)

	def delete(self):
		if len(self.formula) >= 2:
			self.formula = self.formula[:-1]
		else:
			self.clearEdit()
		textUpdate(self.formula[-1], self.textEdit)

	def wholeFormula(self):
		p_formula = [i + '' for i in self.formula]
		QMessageBox.information(self, '完整算式', ''.join(p_formula))

	def about(self):
		QMessageBox.about(
			self,
			'关于', f'{waix}\n'
			'By WaiZhong\n'
			'Github https://github.com/WaiZhong/WaiXCalc/\n'
			f'Version {version}\n'
		)

	def closeEvent(self, a0: QCloseEvent) -> None:
		try:
			self.newWin.close()
		except AttributeError:
			pass
		data['formula'] = self.formula
		save('data.npy', data, allow_pickle=True, fix_imports=True)


if __name__ == '__main__':
	app = QApplication(argv)
	ex = WaiX()
	exit(app.exec_())
