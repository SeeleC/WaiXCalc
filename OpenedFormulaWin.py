from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QTextEdit, QMessageBox, QFileDialog
	)
from PyQt5.QtGui import QIcon

from functions import compute
from settings import font
from pyperclip import copy


class OpenedFormulaWin(QWidget):
	def __init__(self, formulas):
		super().__init__()

		self.formulas = formulas
		self.results = [compute(i) for i in formulas]
		self.initUI()

	def initUI(self):
		layout = QVBoxLayout()
		self.now_page = 1

		head = QHBoxLayout()

		self.last_page_btn = QPushButton('⟨⟨')
		self.last_page_btn.clicked.connect(self.last_page)
		self.last_page_btn.setFont(font)
		self.last_page_btn.setShortcut('Right')
		self.last_page_btn.setEnabled(False)
		head.addWidget(self.last_page_btn)
		head.addStretch(1)

		self.title = QLabel('算式: ' + str(self.now_page) + ' / ' + str(len(self.formulas)))
		self.title.setFont(font)
		head.addWidget(self.title)
		head.addStretch(1)

		self.next_page_btn = QPushButton('⟩⟩')
		self.next_page_btn.clicked.connect(self.next_page)
		self.next_page_btn.setFont(font)
		self.next_page_btn.setShortcut('Left')
		if len(self.formulas) <= 1:
			self.next_page_btn.setEnabled(False)
		head.addWidget(self.next_page_btn)

		layout.addLayout(head)

		body = QGridLayout()

		self.formula_text = QTextEdit()
		self.formula_text.setText(''.join(self.formulas[0]))
		self.formula_text.setFont(font)
		self.formula_text.setReadOnly(True)
		body.addWidget(self.formula_text, 0, 0, 4, 4)

		equal = QLabel('=')
		equal.setFont(font)
		body.addWidget(equal, 0, 5)

		self.result_text = QTextEdit()
		self.result_text.setText(str(compute(self.formulas[0])))
		self.result_text.setFont(font)
		self.result_text.setReadOnly(True)
		body.addWidget(self.result_text, 0, 6, 4, 4)

		layout.addLayout(body)

		base = QHBoxLayout()
		base.addStretch(1)

		copy_btn = QPushButton('复制当前')
		copy_btn.clicked.connect(self.copy)
		copy_btn.setFont(font)
		base.addWidget(copy_btn)

		copy_all_btn = QPushButton('复制全部')
		copy_all_btn.clicked.connect(self.copy_all)
		copy_all_btn.setFont(font)
		base.addWidget(copy_all_btn)

		save_result_btn = QPushButton('导出到..')
		save_result_btn.clicked.connect(self.save_result)
		save_result_btn.setFont(font)
		base.addWidget(save_result_btn)

		layout.addLayout(base)

		self.setLayout(layout)
		self.setWindowIcon(QIcon('images\\ico.JPG'))
		self.setWindowTitle('打开')
		self.resize(600, 400)
		self.setMaximumSize(self.width(), self.height())

	def next_page(self):
		self.now_page += 1

		self.update_text()

	def last_page(self):
		self.now_page -= 1

		self.update_text()

	def update_text(self):
		if self.now_page > 1:
			self.last_page_btn.setEnabled(True)
		else:
			self.last_page_btn.setEnabled(False)

		if self.now_page == len(self.formulas):
			self.next_page_btn.setEnabled(False)
		else:
			self.next_page_btn.setEnabled(True)

		self.title.setText('算式: ' + str(self.now_page) + ' / ' + str(len(self.formulas)))

		self.formula_text.setReadOnly(False)
		self.result_text.setReadOnly(False)

		self.formula_text.setText(''.join(self.formulas[self.now_page - 1]))
		self.result_text.setText(str(compute(self.formulas[self.now_page - 1])))

	def copy(self):
		content = ''.join(self.formulas[self.now_page - 1]) + ' = ' + str(self.results[self.now_page - 1])
		copy(content.replace(' ', ''))
		QMessageBox.information(self, '提示', '已复制!')

	def copy_all(self):
		copy(''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))]))
		QMessageBox.information(self, '提示', '已复制!')

	def save_result(self):
		path = QFileDialog.getSaveFileName(self, '保存', 'result', '*.txt;;All Files(*)')
		with open(path[0], 'w') as f:
			f.write(
				''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))])
			)
		QMessageBox.information(self, '提示', '已导出!')
