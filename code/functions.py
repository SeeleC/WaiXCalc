from PyQt5.QtWidgets import QLabel
from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union

from settings import symbol_lst, symbol_lst_2, symbol_turn, num_weights


def examineInt(num: Union[int, float]):
	if float(num) % 1 == 0:
		num = int(float(num))
	return num


def textUpdate(string: str, label: QLabel):
	label.setText(string)
	weight = 0
	for i in range(len(string)):
		if string[i] not in symbol_lst:
			weight += num_weights[string[i]]
			if weight >= 636:
				label.setText('...' + string[-i+2:])
				break


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


def compute(formula: list) -> int:
	"""
	传入formula，从左到右计算，优先计算嵌套的列表内算式。
	"""
	def c(num1, num2, symbol: str, bl: bool) -> Union[int, float]:
		if bl:
			r = eval(f'Fraction(num1) {symbol_turn[symbol]} Fraction(num2)')
		else:
			r = eval(f'Decimal(num1) {symbol_turn[symbol]} Decimal(num2)')
		return r

	for i in formula:
		if type(i) == list:
			for j in i:
				if match('^[0-9]+/[0-9]+$', j):
					fraction_compute = True
					break
				else:
					fraction_compute = False
		else:
			if match('^[0-9]+/[0-9]+$', i):
				fraction_compute = True
				break
			else:
				fraction_compute = False

	for i in range(len(formula)):
		if type(formula[i]) == list:
			formula_2 = formula[i][:]
			for j in range(len(formula[i])):
				if formula[i][j] in symbol_lst:
					formula_2[0] = str(c(formula_2[0], formula_2[2], formula[i][j], fraction_compute))
					del formula_2[1:3]
			formula[i] = formula_2[:][0]

	result = formula[0]
	start = 0

	for i in range(len(formula)):
		if formula[i] in symbol_lst:
			start += 2
			result = c(result, formula[start], formula[i], fraction_compute)

	try:
		return examineInt(result)
	except ValueError:
		return result


def get_formula(formula_string: str) -> list[str]:
	"""
	传入字符串，将字符串转化为列表，列表每个元素是一串数字或一个符号。
	"""
	front_barckets = ['(', '[', '{']
	back_barckets = [')', ']', '}']
	formula_string = formula_string.replace(' ', '').replace('**', '^').replace('*', '×').replace(':', '÷').replace(
		'//', '÷')
	raw_formula = []
	start = 0

	for i in range(len(formula_string)):
		if formula_string[i] in symbol_lst or i == len(formula_string) - 1:
			raw_formula.append(formula_string[start:i])
			raw_formula.append(formula_string[i])
			start = i + 1

	while '' in raw_formula:
		raw_formula.remove('')

	barcket_start = 0
	is_in_barckets = False
	formula = []

	for i in range(len(raw_formula)):
		if raw_formula[i][0] in front_barckets:
			barcket_start = i
			is_in_barckets = True
		elif raw_formula[i][-1] in back_barckets:
			formula.append([
				i.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace('{', '').replace(
					'}', '')
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
				formula.append(raw_formula[i])

	for i in range(len(formula)):
		while '' in formula[i] and type(formula[i]) == list:
			formula[i].remove('')

	if type(formula[-1]) != list and formula[-2] not in symbol_lst:
		formula[-2] += formula[-1]
		del formula[-1]
	return formula
