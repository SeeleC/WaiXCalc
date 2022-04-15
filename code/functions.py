from PyQt5.QtWidgets import QLabel
from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union
from json import load, dump

from settings import symbol_lst, symbol_lst_2, symbol_turn, num_weights, bracket_lst


def save(filename: str, data: dict) -> None:
	"""
	快速保存
	"""
	with open(filename, 'w+', encoding='utf-8') as f:
		dump(data, f)


def get_data() -> dict[Union[dict[str], str]]:
	"""
	获取data.json的内容，具有向下兼容性
	"""
	rdata = {
		'settings': {
			'_floatToFraction': False,
			'_fractionToFloat': False,
			'_enableRecordHistory': True,
			'language': 'en_us'
		},
		'isResult': False,
		'formula': ['0'],
		'history': [],
	}

	try:
		with open('data.json', 'r+', encoding='utf-8') as f:
			data = load(f)
	except FileNotFoundError:
		data = rdata
	else:
		try:
			data['settings'] = data['settings']
		except KeyError:
			data['settings'] = data.pop('options')

	def compatible(d=data, rd=rdata) -> dict[str, dict]:
		for i in rd.keys():
			try:
				d[i] = d[i]
			except KeyError:
				d[i] = rd[i]
			else:
				if type(d[i]) == dict and type(rd[i]) == dict:
					compatible(d[i], rd[i])
		return d

	if data != rdata:
		data = compatible()

	with open('data.json', 'w+', encoding='utf-8') as f:
		dump(data, f)
	return data


def get_trans() -> dict[str, dict]:
	"""
	获取翻译文件
	"""
	with open('data.json', 'r+', encoding='utf-8') as f:
		language = load(f)['settings']['language']

	with open(f'resource/lang/{language}.json', 'r+', encoding='utf-8') as f:
		return load(f)


def text_update(string: str, label: QLabel) -> None:
	"""
	防止意外的窗口拉伸
	"""
	label.setText(string)
	weight = 0
	for i in range(len(string)):
		if string[i] not in symbol_lst and string[i] not in bracket_lst[0] and string[i] not in bracket_lst[1]:
			weight += num_weights[string[i]]
			if weight >= 636:
				label.setText('...' + string[-i + 2:])
				break


# WaiXCalc-core (WaiX_Calculator_core)
# Version 2.0.0


def isformula(formula: list[str]) -> bool:
	"""
	仅支持单层算式，如'1+3.5*8/9'
	不支持多层算式，如'1+(3.5*8.9)'
	"""
	symbol_in = False

	for i in range(len(formula)):
		if (i+1) % 2 == 0:
			if formula[i] in symbol_lst:
				continue
		else:
			for j in formula[i]:
				if (not j.isdigit() and j in symbol_turn) or symbol_in:
					break
				elif j in symbol_lst_2:
					symbol_in = True
			else:
				symbol_in = False
				continue
		return False
	return True


def calculate(formula: list) -> Union[Fraction, float, int]:
	"""
	传入formula，从左到右计算，优先计算嵌套的列表内算式。
	为了兼容分数，所以 除号(/) 需要用 双斜杠(//) 来代替。
	"""
	def c(r: list[str] = formula[:], f: list = formula[:]) -> list:
		for i in range(len(f)):
			for s in f:
				if type(s) == list:
					lst_in_f = True
					break
			else:
				lst_in_f = False

			if f[i] in symbol_lst and not lst_in_f:
				if formula[i] in symbol_lst[0:2]:
					if '×' in formula or '÷' in formula:
						continue
				elif formula[i] in symbol_lst[2:4] and '^' in formula:
					continue
				if fraction_compute:
					r[i - 1] = eval(f'Fraction(f[i - 1]) {symbol_turn[f[i]]} Fraction(f[i + 1])')
				else:
					r[i - 1] = eval(f'Decimal(f[i - 1]) {symbol_turn[f[i]]} Decimal(f[i + 1])')
				del r[i:i + 2]
				break
			elif type(f[i]) == list:
				while len(r[i]) != 1:
					r[i] = c(r[i], f[i])
					for j in range(len(r[i])):
						if type(r[i][j]) == list and len(r[i][j]) == 1:
							r[i][j] = r[i][j][0]
					f[i] = r[i][:]
		return r

	def fc(f: list[str]):
		for i in f:
			if type(i) == list:
				return fc(i)
			if match('^[0-9]+/[0-9]+$', i):
				return True
			return False

	fraction_compute = fc(formula)

	while True:
		result = c(f=formula)
		for j in range(len(result)):
			if type(result[j]) == list and len(result[j]) == 1:
				result[j] = result[j][0]
		formula = result[:]

		if len(result) == 1:
			break

	try:
		if float(formula[0]) % 1 == 0:
			result = int(float(formula[0]))
		else:
			result = formula[0]
		return result
	except ValueError:
		return formula[0]


def get_formula(formula_string: str) -> list[str]:
	"""
	传入字符串，将字符串转化为列表，列表每个元素是一串数字或一个符号。
	"""
	symbols = ['+', '-', '*', ':', '^']
	fs = formula_string.replace(' ', '').replace('**', '^').replace('*', '×').replace(':', '÷').replace(
		'//', '÷')

	def split(s: str = fs) -> list[str]:
		f = []
		start = 0

		for i in range(len(s)):
			if i >= len(s):
				break

			if s[i] in symbols or i == len(s) - 1:
				if not s[i-1] == ' ':
					f.append(s[start:i])
				f.append(s[i])
				start = i + 1
			elif s[i] in bracket_lst[0]:
				idx = s.index(bracket_lst[1][bracket_lst[0].index(s[i])])
				f.append(split(s[i+1:idx]))
				s = s[:i] + ' ' + s[idx+1:]

		if f[-2] not in symbols and type(f[-1]) != list:
			f[-2] += f[-1]
			del f[-1]
		return f

	return split()
