from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union

symbol_lst = ['+', '-', '*', '//', '^', '**']
symbol_lst_2 = ['/', '.']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '*': '*', '//': '/', '^': '**', '**': '**'}


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
				if not j.isdigit() or j in symbol_turn or symbol_in:
					break
				elif j in symbol_lst_2:
					symbol_in = True
			else:
				symbol_in = False
				continue
		return False
	return True


def compute(formula: list) -> Union[Fraction, float, int]:
	"""
	传入formula，从左到右计算，优先计算嵌套的列表内算式。
	"""
	def c(num1, num2, symbol: str) -> Union[Fraction, Decimal]:
		if fraction_compute:
			r = eval(f'Fraction(num1) {symbol_turn[symbol]} Fraction(num2)')
		else:
			r = eval(f'Decimal(num1) {symbol_turn[symbol]} Decimal(num2)')
		return r

	fraction_compute = False
	start = 0

	for i in formula:
		if match('^[0-9]+/[0-9]+$', i):
			fraction_compute = True
			break

	pass

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
		elif formula_string[i] in bracket_lst[0]:
			raw_formula.append(formula_string[i])
			start = i+1

	while '' in raw_formula:
		raw_formula.remove('')

	'''barcket_start = 0
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
		del formula[-1]'''
	return raw_formula
