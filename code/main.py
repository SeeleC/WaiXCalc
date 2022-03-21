from decimal import Decimal
from fractions import Fraction

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['+', '-', '*', ':', '^', '/', '.']
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '^': '**'}


def examineInt(num):
	if float(num) % 1 == 0:
		num = int(float(num))
	return num


def isFormula(formula: list) -> bool:
	start = 0
	for i in formula:
		start += 1
		if start % 2 == 0:
			if i in symbol_lst or i in symbol_lst_2:
				continue
		else:
			for j in i:
				if not j.isdigit() and j not in symbol_lst_2:
					break
			else:
				continue
		return False
	return True


def compute(formula: list) -> int:
	start = 0
	for i in range(len(formula)):
		if '(' in formula[i]:
			formula[i] = formula[i].replace('(', '')
			formula[i] = formula[i].replace(')', '')
		elif formula[i][-1] == '.' or formula[i][-1] == '/':
			formula[i] = formula[i][:-1]
	result = formula[0]
	if '/' in ''.join(formula):
		fraction_compute = True
	else:
		fraction_compute = False
	for j in formula:
		if j in symbol_lst:
			start += 2
			if not fraction_compute:
				result = eval(f'Decimal(result) {symbol_turn[j]} Decimal(formula[start])')
			else:
				result = eval(f'Fraction(result) {symbol_turn[j]} Fraction(formula[start])')
	try:
		return examineInt(result)
	except ValueError:
		return result


def get_formula(formula_string: str) -> list:
	symbols = ['+', '-', '×', '÷', '^']
	formula_string = formula_string.replace(' ', '').replace('**', '^').replace('*', '×').replace(':', '÷').replace(
		'//', '÷')
	formula = []
	start = 0

	if '=' in formula_string:
		idx = formula_string.index('=')
		formula_string = formula_string[:idx]

	for i in range(len(formula_string)):
		if formula_string[i] in symbols or i == len(formula_string) - 1:
			formula.append(formula_string[start:i])
			start = i + 1
			formula.append(formula_string[i])

	if '(-' not in ''.join(formula):
		formula[-2] += formula[-1]
		del formula[-1]
	else:
		index_1 = 0
		for j in range(len(formula)):
			try:
				if '(' in formula[j]:
					index_1 = j
				elif ')' in formula[j]:
					index_2 = j
					formula[index_1] = ''.join(formula[index_1:index_2 + 1])
					index_1 += 1
					for nope in formula[index_1:index_2 + 1]:
						index = formula.index(nope, index_1, index_2 + 1)
						del formula[index]
					index_1 += 1
			except IndexError:
				pass

	while '' in formula:
		formula.remove('')
	return formula
