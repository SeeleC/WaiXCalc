from PyQt5.QtGui import QFont

__version__ = '1.8.3'

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['.', '/']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '//': '/', '^': '**', '**': '**'}
num_widths = {
	'1': 30.4, '2': 31.8, '3': 33.4, '4': 33.4, '5': 33.4, '6': 33.4, '7': 30.3, '8': 33.4, '9': 33.4, '0': 31.8,
	'.': 20, '/': 20, 'E': 30.5
}  # number weight / 640

default_options = {
	'settings.1.option.1': True,
	'settings.1.option.2': False,
	'settings.1.option.3': False,
	'settings.2.option': True,
	'settings.4.option': False,
	'language': 'en_us',
	'font': 'Segoe UI',
	'window_title': 'WaiXCalc',
	'latest_pos_x': 0,
	'latest_pos_y': 0,
}

default_data = {
	'formula': ['0'],
	'calcFormula': ['0'],
	'calcFormulaStep': [],
	'frontBracketIndex': [],
	'frontBracketIndexStep': [],
	'isResult': False,
	'history': [],
}

font = QFont()
font.setPointSize(8)

hFont = QFont()
hFont.setPointSize(24)

tFont = QFont()
tFont.setPointSize(10)

mFont = QFont()
mFont.setPointSize(9)

# tipFont = QFont()
# tipFont.setPointSize(4)
