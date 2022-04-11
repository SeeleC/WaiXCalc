from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union

# WaiXCalc-core (WaiX_Calculator_core)
# Version 2.0.0
# By WaiZhong
# MIT LICENSE

symbol_lst = ['+', '-', '*', '//', ':', '^', '**']
symbol_lst_2 = ['/', '.']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '*': '*', '//': '/', ':': '/', '^': '**', '**': '**'}


def isformula(formula: list) -> bool:
	"""
	仅支持单层算式，如'1+3.5*8/9'
	不支持多层算式，如'1+(3.5*8.9)'
	"""
	start = 0
	symbol_in = False

	for i in formula:
		start += 1
		if start % 2 == 0:
			if i in symbol_lst:
				continue
		else:
			for j in i:
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
				if f[i] in symbol_lst[0:2]:
					if '*' in f or '//' in f:
						continue
				elif f[i] in symbol_lst[2:5] and '**' in f:
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

	fraction_compute = fc(formula)

	while True:
		result = c(f=formula)
		for j in range(len(result)):
			if type(result[j]) == list and len(result[j]) == 1:
				result[j] = result[j][0]
		formula = result[:]
		print(formula)

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
	formula_string = formula_string.replace(' ', '').replace('**', '^').replace('×', '*').replace('÷', ':').replace(
		'=', '').replace('//', ':')
	raw_formula = []
	start = 0

	for i in range(len(formula_string)):
		if formula_string[i] in symbols or i == len(formula_string) - 1:

			raw_formula.append(formula_string[start:i])
			raw_formula.append(formula_string[i])
			start = i + 1

	while '' in raw_formula:
		raw_formula.remove('')

	barcket_start = 0
	is_in_barckets = False
	formula = []

	for i in range(len(raw_formula)):
		if raw_formula[i][0] in bracket_lst[0]:
			barcket_start = i
			is_in_barckets = True
		elif raw_formula[i][-1] in bracket_lst[1]:
			formula.append([
				i.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace(
					'}', '').replace(':', '//').replace('^', '**')
				for i in raw_formula[barcket_start:i+1]
			])
			if formula[-1][1] == '-' and formula[-1][0] == '':
				formula[-1][0] = formula[-1][1] + formula[-1][2]
				del formula[-1][1:3]
				if len(formula[-1]) == 1:
					formula[-1] = formula[-1][0]

			is_in_barckets = False
		else:
			if not is_in_barckets:
				formula.append(raw_formula[i].replace(':', '//').replace('^', '**'))

	for i in range(len(formula)):
		while '' in formula[i] and type(formula[i]) == list:
			formula[i].remove('')

	if type(formula[-1]) != list and formula[-2] not in symbol_lst:
		formula[-2] += formula[-1]
		del formula[-1]
	return formula
