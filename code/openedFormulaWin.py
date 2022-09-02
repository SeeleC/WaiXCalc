from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QTextEdit, QMessageBox, QFileDialog, QApplication
	)
from PyQt5.QtGui import QIcon
from win32mica import ApplyMica, MICAMODE

from functions import calculate, get_trans, get_translated_messagebox, get_options
from settings import rFont, tFont


class OpenedFormulaWin(QWidget):
	def __init__(self, formulas):
		super().__init__()

		self.formulas = formulas
		self.results = []
		self.trans = get_trans()
		self.options = get_options()

		self.clipboard = QApplication.clipboard()
		
		for i in formulas:
			try:
				self.results.append(calculate(i))
			except (ZeroDivisionError, ValueError):
				self.results.append(self.trans['text.main.error'])
		self.init_ui()

	def init_ui(self):
		self.setFont(rFont)
		layout = QVBoxLayout()
		self.now_page = 1

		head = QHBoxLayout()

		self.last_page_btn = QPushButton('<<')
		self.last_page_btn.clicked.connect(self.last_page)
		self.last_page_btn.setShortcut('Right')
		self.last_page_btn.setEnabled(False)
		head.addWidget(self.last_page_btn)
		head.addStretch(1)

		self.title = QLabel(self.trans['text.open.page'] % (self.now_page, len(self.formulas)))
		head.addWidget(self.title)
		head.addStretch(1)

		self.next_page_btn = QPushButton('>>')
		self.next_page_btn.clicked.connect(self.next_page)
		self.next_page_btn.setShortcut('Left')
		if len(self.formulas) <= 1:
			self.next_page_btn.setEnabled(False)
		head.addWidget(self.next_page_btn)

		layout.addLayout(head)

		body = QGridLayout()

		self.formula_text = QTextEdit()
		self.formula_text.setText(''.join(self.formulas[0]))
		self.formula_text.setFont(tFont)
		self.formula_text.setReadOnly(True)
		body.addWidget(self.formula_text, 0, 0, 4, 4)

		equal = QLabel('=')
		equal.setFont(tFont)
		body.addWidget(equal, 0, 5)

		self.result_text = QTextEdit()
		self.result_text.setText(str(self.results[0]))
		self.result_text.setFont(tFont)
		self.result_text.setReadOnly(True)
		body.addWidget(self.result_text, 0, 6, 4, 4)

		layout.addLayout(body)

		base = QHBoxLayout()
		base.addStretch(1)

		copy_btn = QPushButton(self.trans['button.open.copyCurrent'])
		copy_btn.clicked.connect(self.copy)
		base.addWidget(copy_btn)

		copy_all_btn = QPushButton(self.trans['button.open.copyAll'])
		copy_all_btn.clicked.connect(self.copy_all)
		base.addWidget(copy_all_btn)

		save_result_btn = QPushButton(self.trans['button.open.export'])
		save_result_btn.clicked.connect(self.save_result)
		base.addWidget(save_result_btn)

		layout.addLayout(base)

		if self.options['settings.4.option']:
			self.setAttribute(Qt.WA_TranslucentBackground)
			if self.options['enableDarkMode']:
				ApplyMica(int(self.winId()), MICAMODE.DARK)
			else:
				ApplyMica(int(self.winId()), MICAMODE.LIGHT)

		self.setLayout(layout)
		self.setWindowIcon(QIcon('resource/images/icon.jpg'))
		self.setWindowTitle(self.trans['window.open.title'])
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

		self.title.setText(self.trans['text.open.page'] % (self.now_page, len(self.formulas)))

		self.formula_text.setReadOnly(False)
		self.result_text.setReadOnly(False)

		self.formula_text.setText(''.join(self.formulas[self.now_page - 1]))
		self.result_text.setText(str(self.results[self.now_page - 1]))

		self.formula_text.setReadOnly(True)
		self.result_text.setReadOnly(True)

	def copy(self):
		content = ''.join(self.formulas[self.now_page - 1]) + ' = ' + str(self.results[self.now_page - 1])
		self.clipboard.setText(content.replace(' ', ''))
		get_translated_messagebox(
			QMessageBox.Icon.Information,
			self.trans['window.hint.title'],
			self.trans['hint.open.copyCurrent'],
			self,
			self.options['enableDarkMode']
		).show()

	def copy_all(self):
		self.clipboard.setText(
			''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))])
		)
		get_translated_messagebox(
			QMessageBox.Icon.Information,
			self.trans['window.hint.title'],
			self.trans['hint.open.copyAll'],
			self,
			self.options['enableDarkMode']
		).show()

	def save_result(self):
		path = QFileDialog.getSaveFileName(self, '保存', 'result', '*.txt;;All Files(*)')
		if path != '':
			with open(path[0], 'w') as f:
				f.write(
					''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))])
				)
		get_translated_messagebox(
			QMessageBox.Icon.Information,
			self.trans['window.hint.title'],
			self.trans['hint.open.export'],
			self,
			self.options['enableDarkMode']
		).show()
