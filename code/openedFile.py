from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QTextEdit, QMessageBox, QFileDialog, QApplication,
	QAction
)
from PyQt5.QtGui import QIcon
from win32mica import ApplyMica, MICAMODE

from detector import Detector
from subWindow import SubWindow
from functions import get_trans, get_enhanced_messagebox, get_options, get_data, load_theme
from config import rFont, tFont
from core import calculate


class OpenedFile(SubWindow):
	def __init__(self, formulas):
		super().__init__()

		self.formulas = formulas
		self.results = []
		self.trans = get_trans()
		self.options = get_options()
		self.data = get_data()

		self.clipboard = QApplication.clipboard()

		self.detector = Detector(self)
		self.detector.colorModeChanged.connect(self.detect_dark_mode)
		self.detector.start()
		
		for i in formulas:
			try:
				self.results.append(calculate(i[:]))
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
		equal.setAlignment(Qt.AlignHCenter)
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
		copy_btn.clicked.connect(self.clicked)
		base.addWidget(copy_btn)

		copy_all_btn = QPushButton(self.trans['button.open.copyAll'])
		copy_all_btn.clicked.connect(self.clicked)
		base.addWidget(copy_all_btn)

		save_result_btn = QPushButton(self.trans['button.open.export'])
		save_result_btn.clicked.connect(self.clicked)
		base.addWidget(save_result_btn)

		layout.addLayout(base)

		load_theme(self)

		close_action = QAction(self)
		close_action.setShortcuts(['Return', 'Escape'])
		close_action.triggered.connect(self.close)
		self.addAction(close_action)

		self.setLayout(layout)
		self.setWindowIcon(QIcon('resources/images/icon.jpg'))
		self.setWindowTitle(self.trans['window.open.name'])
		self.resize(600, 400)
		self.setMaximumSize(self.width(), self.height())

	def apply_mica(self):
		self.setAttribute(Qt.WA_TranslucentBackground)
		if self.data['enableDarkMode'] or self.options['settings.4.selector.2'] == 'colorMode.dark':
			ApplyMica(int(self.winId()), MICAMODE.DARK)
		else:
			ApplyMica(int(self.winId()), MICAMODE.LIGHT)

	def clicked(self):
		sender = self.sender()
		if sender.text() == self.trans['button.open.copyCurrent']:
			self.copy(
				''.join(self.formulas[self.now_page - 1]) + ' = ' + str(self.results[self.now_page - 1]),
				'current'
			)
		elif sender.text() == self.trans['button.open.copyAll']:
			self.copy(
				''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))]),
				'all'
			)
		elif sender.text() == self.trans['button.open.export']:
			self.export()

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

	def copy(self, content: str, range: str):
		self.clipboard.setText(content.replace(' ', ''))
		get_enhanced_messagebox(
			QMessageBox.Icon.Information,
			self.trans['window.hint.name'],
			self.trans[f'hint.open.copy{range.title()}'],
			self,
			self.data['enableDarkMode']
		).show()

	def export(self):
		path = QFileDialog.getSaveFileName(self, '保存', 'result', '*.txt;;All Files(*)')
		if path[0]:
			with open(path[0], 'w') as f:
				f.write(
					''.join([''.join(self.formulas[i]) + ' = ' + str(self.results[i]) + '\n' for i in range(len(self.formulas))])
				)
			get_enhanced_messagebox(
				QMessageBox.Icon.Information,
				self.trans['window.hint.name'],
				self.trans['hint.open.export'],
				self,
				self.data['enableDarkMode']
			).show()
