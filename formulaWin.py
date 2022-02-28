from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, symbol_lst, symbol_lst_2
from functions import textUpdate, getFormula


class FormulaWin(QWidget):
	def __init__(self, main):
		super().__init__()

		self.setWindowFlag(Qt.WindowCloseButtonHint)
		self.main = main

		self.edit = QLineEdit(self)
		self.edit.setFont(font)
		self.edit.textChanged.connect(self.textChanged)

		okBtn = QPushButton('确定')
		okBtn.setShortcut('Enter')
		okBtn.setFont(font)
		okBtn.clicked.connect(self.updateEdit)

		grid = QGridLayout()
		grid.addWidget(self.edit, 0, 0)
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(okBtn)
		grid.addLayout(hbox, 1, 0)

		self.setLayout(grid)
		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.setWindowTitle('新建完整算式')
		self.setFixedWidth(400)

	def updateEdit(self):
		formula_string = self.edit.text()
		if formula_string == '':
			self.close()
		if len(formula_string) <= 1:
			QMessageBox.warning(self, '提示', '算式过短！')
		else:
			try:
				self.main.formula = getFormula(formula_string)
				textUpdate(self.main.formula[-1], self.main.textEdit)
			except ValueError:
				pass
			else:
				if self.main.formula[-1] not in symbol_lst and not self.main.formula[-1].isdigit() and\
					type(eval(self.main.formula[-1])) != float:
					self.main.clearEdit()
					textUpdate(self.main.formula[-1], self.main.textEdit)
				self.close()

	def keyPressEvent(self, e):
		match e.key():
			case Qt.Key_Return | Qt.Key_Enter:
				self.updateEdit()

	def textChanged(self):
		if len(self.edit.text().strip()) >= 1:
			if not self.edit.text()[-1].isdigit() and self.edit.text()[-1] not in symbol_lst_2:
				if len(self.edit.text()) > 1:
					self.edit.setText(self.edit.text()[:-1])
				else:
					self.edit.clear()
