from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from re import match
from typing import Union
from json import load, dump
from os import mkdir, listdir, remove

from settings import symbol_lst, symbol_lst_2, symbol_turn, num_widths, bracket_lst, default_options, default_data, font


def get_data() -> dict[Union[str, list, bool]]:
	"""
	获取data/cache.json的内容，具有一定的向下兼容性
	"""
	try:
		with open('data/data.json', 'r', encoding='utf-8') as f:
			data: dict = load(f)
	except FileNotFoundError:
		try:
			with open('data/cache.json', 'r', encoding='utf-8') as f:
				data = load(f)
		except FileNotFoundError:
			data = default_data
	else:
		remove('data/data.json')

	if data != default_data:
		data = mend_dict_item(data, default_data)

	save('data/cache.json', data)
	return data


def get_history() -> list[str]:
	try:
		with open('data/history.json', 'r', encoding='utf-8') as f:
			hdata = load(f)
	except FileNotFoundError:
		options = get_options()
		if 'history' in options.keys():
			hdata = options.pop('history')
			save('data/options.json', options)
		else:
			hdata = []

	save('data/history.json', hdata)
	return hdata


def get_menu_items(trans: dict):
	names = [
		[
			trans['option.fileMenu.1'],
			trans['option.fileMenu.2'],
			trans['option.fileMenu.3']
		],
		[
			trans['option.editMenu.1'],
			trans['option.editMenu.2'],
			trans['option.editMenu.3'],
			trans['option.editMenu.4']
		],
		[
			trans['option.helpMenu.1'],
			trans['option.helpMenu.2'],
			trans['option.helpMenu.3'],
		],
	]
	statustips = [
		[
			trans['statusTip.fileMenu.1'],
			trans['statusTip.fileMenu.2'],
			trans['statusTip.fileMenu.3'],
		],
		[
			trans['statusTip.editMenu.1'],
			trans['statusTip.editMenu.2'],
			trans['statusTip.editMenu.3'],
			trans['statusTip.editMenu.4'],
		],
		[
			trans['statusTip.helpMenu.1'],
			trans['statusTip.helpMenu.2'],
			trans['statusTip.helpMenu.3'],
		],
	]
	return names, statustips


def get_options() -> dict[Union[dict[str], str]]:
	"""
	获取data/options.json的内容，具有向下兼容性
	"""
	try:
		with open('data/options.json', 'r', encoding='utf-8') as f:
			data = load(f)
	except FileNotFoundError:
		try:
			listdir('data')
		except FileNotFoundError:
			mkdir('data')
		data = default_options
	else:
		if 'settings' in data.keys():
			settings = data.pop('settings')
			data = {**settings, **data}
		elif 'options' in data.keys():
			settings = data.pop('options')
			data = {**settings, **data}

	if data != default_options:
		data = mend_dict_item(data, default_options)

	save('data/options.json', data)
	return data


def get_trans() -> dict[str]:
	"""
	获取翻译文件
	"""
	with open('data/options.json', 'r', encoding='utf-8') as f:
		language = load(f)['language']

	with open(f'resource/lang/{language}.json', 'r', encoding='utf-8') as f:
		return load(f)


def get_trans_entry(trans: dict, text: str) -> dict:
	"""
	通过键名查找多个条目
	"""
	result = {}

	for i in trans.keys():
		for j in range(len(i)):
			if i[:j] == text:
				result = {**result, **{i: trans[i]}}

	return result


def get_trans_info() -> dict[str]:
	"""
	遍历lang文件夹、获取json文件信息
	"""
	data = {}
	for i in sorted(listdir('resource/lang')):
		i = i[:-5]
		if i != 'template':
			with open(f'resource/lang/{i}.json', 'r', encoding='utf-8') as f:
				res = load(f)
				data = {**data, **{res['language.name']: res['language.id']}}
	return data


def get_translated_messagebox(
		icon: Union[QMessageBox.Icon, QPixmap],
		title: str,
		text: str,
		parent: QWidget = None
	):
	if isinstance(icon, QMessageBox.Icon):
		box = QMessageBox(icon, title, text, QMessageBox.Ok, parent)
	else:
		box = QMessageBox(QMessageBox.Icon.NoIcon, title, text, QMessageBox.Ok, parent)
		box.setIconPixmap(icon)

	ok = box.button(QMessageBox.Ok)
	ok.setText(get_trans()['button.ok'])

	box.setFont(font)

	return box


def mend_dict_item(d, rd) -> dict[str, dict]:
	for i in rd.keys():
		try:
			d[i] = d[i]
		except KeyError:
			d[i] = rd[i]
	return d


def save(filename: str, data) -> None:
	"""
	快速保存
	"""
	with open(filename, 'w', encoding='utf-8') as f:
		dump(data, f)


def text_update(string: str, label: QLabel) -> None:
	"""
	防止意外的窗口拉伸
	"""
	label.setText(string)
	weight = 0
	for i in range(len(string)):
		if string[i] not in symbol_lst and string[i] not in bracket_lst[0] and string[i] not in bracket_lst[1]:
			weight += num_widths[string[i]]
			if weight >= 636:
				label.setText('...' + string[-i + 2:])
				break


# tree: core


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
				if j in symbol_turn or (symbol_in and not j.isdigit()):
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

				try:
					if fraction_compute:
						r[i - 1] = eval(f'Fraction(f[i - 1]) {symbol_turn[f[i]]} Fraction(f[i + 1])')
					else:
						r[i - 1] = eval(f'Decimal(f[i - 1]) {symbol_turn[f[i]]} Decimal(f[i + 1])')
				except InvalidOperation:
					raise SyntaxError('非法算式!')
				else:
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
			result = float(formula[0])
		return result
	except ValueError:
		return formula[0]


def get_formula(formula_string: str) -> list[str]:
	"""
	传入字符串，将字符串转化为列表，列表每个元素是一串数字或一个符号。
	"""
	fs = formula_string.replace(' ', '').replace('**', '^').replace('*', '×').replace(':', '÷').replace(
		'//', '÷')

	def split(s: str = fs) -> list[str]:
		f = []
		start = 0

		for i in range(len(s)):
			if i >= len(s):
				break

			if s[i] in symbol_lst or i == len(s) - 1:
				if not s[i-1] == ' ':
					f.append(s[start:i])
				f.append(s[i])
				start = i + 1
			elif s[i] in bracket_lst[0]:
				idx = s.index(bracket_lst[1][bracket_lst[0].index(s[i])])
				f.append(split(s[i+1:idx]))
				s = s[:i] + ' ' + s[idx+1:]

		if type(f[-1]) != list and f[-2] not in symbol_lst:
			f[-2] += f[-1]
			del f[-1]
		return f

	return split()
