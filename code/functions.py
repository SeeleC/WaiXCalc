from PyQt5.QtWidgets import QLabel
from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union

from settings import symbol_lst, symbol_lst_3, symbol_turn, num_weights, bracket_lst, dump


def save(filename: str, data: dict) -> None:
	"""
	快速保存
	"""
	with open(filename, 'w+', encoding='utf-8') as f:
		dump(data, f)


def textUpdate(string: str, label: QLabel) -> None:
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


# core


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
				if (not j.isdigit() or j in symbol_turn.keys()) and j not in symbol_lst_3:
					break
				elif symbol_in and not j.isdigit():
					break
				elif j in symbol_lst_3:
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

	def c(num1, num2, symbol: str) -> Union[Fraction, float, int]:
		if fraction_compute:
			r = eval(f'Fraction(num1) {symbol_turn[symbol]} Fraction(num2)')
		else:
			r = eval(f'Decimal(num1) {symbol_turn[symbol]} Decimal(num2)')
		return r

	fraction_compute = False
	result = formula[:]

	for i in formula:
		if type(i) == list:
			for j in i:
				if match('^[0-9]+/[0-9]+$', j):
					fraction_compute = True
					break
		else:
			if match('^[0-9]+/[0-9]+$', i):
				fraction_compute = True
				break

	while True:
		for i in range(len(formula)):
			for s in formula:
				if type(s) == list:
					lst_in_f = True
					break
			else:
				lst_in_f = False
			if formula[i] in symbol_lst and not lst_in_f:
				if formula[i] in symbol_lst[0:2]:
					if '×' in formula or '÷' in formula:
						continue
				elif formula[i] in symbol_lst[2:4] and '^' in formula:
					continue
				result[i - 1] = c(formula[i - 1], formula[i + 1], formula[i])
				del result[i:i + 2]
				break
			elif type(formula[i]) == list:
				subformula = formula[i][:]
				subresult = subformula[:]
				while True:
					for j in range(len(subformula)):
						if subformula[j] in symbol_lst:
							if subformula[j] in symbol_lst[0:2]:
								if '×' in subformula or '÷' in subformula:
									continue
							elif subformula[j] in symbol_lst[2:4] and '^' in subformula:
								continue
							subresult[j - 1] = c(subformula[j - 1], subformula[j + 1], subformula[j])
							del subresult[j:j + 2]
							break
					subformula = subresult[:]
					if len(subresult) == 1:
						break
				result[i] = subresult[0]
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
	formula_string = formula_string.replace(' ', '').replace('**', '^').replace('*', '×').replace(':', '÷').replace(
		'//', '÷')
	raw_formula = []
	start = 0

	for i in range(len(formula_string)):
		if formula_string[i] in symbol_lst or i == len(formula_string) - 1:
			raw_formula.append(formula_string[start:i])
			raw_formula.append(formula_string[i])
			start = i + 1
		elif formula_string[i] in bracket_lst[0]:
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
					'}', '')
				for i in raw_formula[barcket_start:i + 1]
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
