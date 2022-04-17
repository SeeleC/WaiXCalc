from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from settings import font, symbol_lst, symbol_lst_2
from functions import text_update, get_formula, get_trans


class CreateFormulaWin(QWidget):
	def __init__(self, main):
		super().__init__()

		self.setWindowFlag(Qt.WindowCloseButtonHint)
		self.main = main
		self.trans = get_trans()

		self.edit = QLineEdit(self)
		self.edit.setFont(font)
		self.edit.textChanged.connect(self.textChanged)

		ok = QPushButton(self.trans['buttonOk'])
		ok.setShortcut('Return')
		ok.setFont(font)
		ok.clicked.connect(self.updateEdit)

		grid = QGridLayout()
		grid.addWidget(self.edit, 0, 0)
		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(ok)
		grid.addLayout(hbox, 1, 0)

		self.setLayout(grid)
		self.setWindowIcon(QIcon('resource/images/ico.JPG'))
		self.setWindowTitle(self.trans['windowTitles']['createFormulaWin'])
		self.setFixedWidth(400)

	def updateEdit(self):
		formula_string = self.edit.text()
		if formula_string == '':
			self.close()
		if len(formula_string) <= 1 and formula_string != '':
			QMessageBox.warning(self, self.trans['remindTexts']['title'], self.trans['remindTexts']['formulaTooShort'])
		else:
			if formula_string != '':
				try:
					self.main.formula = get_formula(formula_string)
					text_update(self.main.formula[-1], self.main.textEdit)
				except (ValueError, IndexError):
					self.close()
				else:
					if self.main.formula[-1] in symbol_lst or self.main.formula[-1] in symbol_lst_2:
						self.main.formula.append('0')

					if not self.main.formula[-1].isdigit() and type(eval(self.main.formula[-1])) != float:
						self.main.clear_edit()
						self.main.textEdit.setText('0')
					self.close()

	def keyPressEvent(self, e):
		if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
			self.updateEdit()

	def textChanged(self):
		if len(self.edit.text().strip()) >= 1:
			if not self.edit.text()[-1].isdigit() and self.edit.text()[-1] not in symbol_lst_2:
				if len(self.edit.text()) > 1:
					self.edit.setText(self.edit.text()[:-1])
				else:
					self.edit.clear()
