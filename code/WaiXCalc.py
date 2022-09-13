from decimal import Decimal
from fractions import Fraction
from re import match
from typing import Union

# WaiXCalc-Core
# By WaiZhong
# MIT LICENSE
# Source https://github.com/WaiZhong/WaiXCalc/tree/core

symbol_lst = ['+', '-', '*', '//', ':', '^', '**']
symbol_lst_2 = ['/', '.']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '*': '*', '//': '/', ':': '/', '^': '**', '**': '**'}


def verify_formula(formula: list[str]) -> bool:
	"""
	验证列表中的算式（get_formula()的结果）是否是calculate()可进行计算的
	:param formula:
	:return bool:
	"""
	for i in range(len(formula)):
		if (i+1) % 2 == 0 and formula[i] in symbol_lst:
			continue
		elif verify_int(formula[i]):
			continue
		return False
	return True


def verify_int(integer: str):
	"""
	验证字符串是否是整数、小数或分数
	:param integer:
	:return bool:
	"""
	symbol_frequency = {'.': 0, '/': 0}

	if integer[-1] in symbol_lst_2:
		return False

	for i in integer:
		if i in symbol_turn or i in [j for _ in bracket_lst for j in _]:
			return False
		elif i in symbol_lst_2:
			symbol_frequency[i] += 1
			if symbol_frequency['.'] > 2 or symbol_frequency['/'] > 1:
				return False

	return True


def calculate(formula: list) -> Union[Fraction, Decimal, int]:
	"""
	传入formula，从左到右计算，优先计算嵌套的列表内算式。
	为了兼容分数，所以 除号(/) 需要用 双斜杠(//) 来代替。
	:param formula: list[str]
	:return: Union[Fraction, Decimal, int]
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
			if match('^\d+/\d+$', i):
				break
		else:
			return False
		return True

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


def get_formula(formula_string: str) -> Union[list[str], list[list[str]]]:
	"""
	传入字符串，将字符串转化为列表，列表每个元素是一串数字或一个符号。
	仅允许以 括号`()` / 中括号`[]` / 大括号`{}` 作嵌套、同一嵌套内不能重复使用、不限制使用顺序。
	:param formula_string: str
	:return: list[str, list[str]]
	"""
	symbols = ['+', '-', '*', ':', '^']
	fs = formula_string.replace(' ', '').replace('**', '^').replace('×', '*').replace('÷', ':').replace(
		'=', '').replace('//', ':')  # formula string=fs

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
