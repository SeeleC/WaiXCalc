from PyQt5.QtGui import QFont
from numpy import save, load, array

try:
	data = load('data.npy', allow_pickle=True, fix_imports=True).item()
except FileNotFoundError:
	data = {
		'options': {
			'isResult': False,
			'_floatToFraction': False,
			'_fractionToFloat': False
		},
		'formula': ['0'],
		'history': [],
	}
	save('data.npy', data, allow_pickle=True, fix_imports=True)

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['+', '-', '*', ':', '^', '/', '.']
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '^': '**'}
num_weights = {
	'1': 24.4, '2': 31.8, '3': 33.4, '4': 33.4, '5': 33.4, '6': 33.4, '7': 30.2, '8': 33.4, '9': 33.4, '0': 31.8,
	'.': 20, '/': 20
}
font = QFont()
font.setFamily('微软雅黑')
font.setPointSize(8)
