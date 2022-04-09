from PyQt5.QtGui import QFont
from json import load, dump
from os import remove
from numpy import load as nload

try:
	data = nload('data.npy', allow_pickle=True, fix_imports=True).item()
	remove('data.npy')
except FileNotFoundError:
	try:
		with open('data.json', 'r+', encoding='utf-8') as f:
			data = load(f)
	except FileNotFoundError:
		data = {
			'settings': {
				'isResult': False,
				'isInBracket': False,
				'_floatToFraction': False,
				'_fractionToFloat': False,
				'_enableRecordHistory': True,
				'language': 'en_us'
			},
			'formula': ['0'],
			'history': [],
		}
		with open('data.json', 'w+', encoding='utf-8') as f:
			dump(data, f)
	else:
		try:
			data['settings'] = data['settings']
		except KeyError:
			data['settings'] = data.pop('options')
else:
	with open('data.json', 'w+', encoding='utf-8') as f:
		dump(data, f)
finally:
	try:
		data['settings']['language'] = data['settings']['language']
	except KeyError:
		data['settings']['language'] = 'en_us'
	finally:
		with open(f'resource/lang/{data["settings"]["language"]}.json', 'r+', encoding='utf-8') as f:
			trans = load(f)

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['+', '-', '*', ':', '^', '/', '.']
symbol_lst_3 = ['.', '/']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '//': '/', '^': '**', '**': '**'}
num_weights = {
	'1': 30.4, '2': 31.8, '3': 33.4, '4': 33.4, '5': 33.4, '6': 33.4, '7': 30.3, '8': 33.4, '9': 33.4, '0': 31.8,
	'.': 20, '/': 20
}

font = QFont()
font.setFamily('Microsoft Yahei UI')
font.setPointSize(8)
mwFont = QFont()
mwFont.setFamily('Microsoft Yahei UI')
mwFont.setPointSize(20)
ofwFont = QFont()
ofwFont.setFamily('Microsoft Yahei UI')
ofwFont.setPointSize(10)
