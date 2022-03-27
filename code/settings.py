import os

from PyQt5.QtGui import QFont
from json import load, dump
from os import remove
from numpy import load as nload

try:
	data = nload('data.npy', allow_pickle=True, fix_imports=True).item()
	os.remove('data.npy')
except FileNotFoundError:
	try:
		with open('data.json', 'r+', encoding='utf-8') as f:
			data = load(f)
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
		with open('data.json', 'w+', encoding='utf-8') as f:
			dump(data, f)
else:
	with open('data.json', 'w+', encoding='utf-8') as f:
		dump(data, f)

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['+', '-', '*', ':', '^', '/', '.']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '^': '**'}
num_weights = {
	'1': 24.4, '2': 31.8, '3': 33.4, '4': 33.4, '5': 33.4, '6': 33.4, '7': 30.2, '8': 33.4, '9': 33.4, '0': 31.8,
	'.': 20, '/': 20
}
font = QFont()
font.setFamily('Microsoft Yahei UI')
font.setPointSize(8)
