from PyQt5.QtCore import QTextStream, QFile, Qt
from PyQt5.QtGui import QPixmap, QFontMetrics
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from re import match
from typing import Union
from json import load, dump
from os import mkdir, listdir, remove, path
from winreg import ConnectRegistry, HKEY_CURRENT_USER, OpenKey, EnumValue
from win32mica import ApplyMica, MICAMODE

from settings import (
	symbol_lst, symbol_lst_2, symbol_turn, num_widths, bracket_lst, default_options, default_data, rFont
)


def apply_mica(widget: QWidget, dark_mode):
	widget.setAttribute(Qt.WA_TranslucentBackground)
	if dark_mode:
		ApplyMica(int(widget.winId()), MICAMODE.DARK)
	else:
		ApplyMica(int(widget.winId()), MICAMODE.LIGHT)


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
			return load(f)
	except FileNotFoundError:
		pass
	return []


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

		if 'settings.2.option' in data.keys():
			data['settings.2.option.1'] = data.pop('settings.2.option')
		if 'font' in data.keys():
			data['settings.4.selector.1'] = data.pop('font')

	if data != default_options:
		data = mend_dict_item(data, default_options)

	save('data/options.json', data)
	return data


def get_reversed_list(lst: list):
	lst2 = lst[::-1]
	return lst2


def get_style(filename: str) -> str:
	qss_file = QFile(path.abspath(filename))
	qss_file.open(QFile.ReadOnly | QFile.Text)
	text_stream = QTextStream(qss_file)
	return text_stream.readAll()


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


def get_enhanced_messagebox(
		icon: Union[QMessageBox.Icon, QPixmap],
		title: str,
		text: str,
		parent: QWidget = None,
		dark_mode: bool = False
	):
	if isinstance(icon, QMessageBox.Icon):
		box = QMessageBox(icon, title, text, QMessageBox.Ok, parent)
	else:
		box = QMessageBox(QMessageBox.Icon.NoIcon, title, text, QMessageBox.Ok, parent)
		box.setIconPixmap(icon)

	ok = box.button(QMessageBox.Ok)
	ok.setText(get_trans()['button.ok'])
	ok.setFont(rFont)

	box.setFont(rFont)
	if get_options()['settings.4.option'] and dark_mode:
		apply_mica(box, dark_mode)

	return box


def is_dark_mode():
	registry = ConnectRegistry(None, HKEY_CURRENT_USER)
	reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
	try:
		reg_key = OpenKey(registry, reg_keypath)
	except FileNotFoundError:
		return False

	for i in range(1024):
		try:
			value_name, value, _ = EnumValue(reg_key, i)
			if value_name == 'AppsUseLightTheme':
				return value == 0
		except OSError:
			break
	return False


def load_theme(widget: QWidget):
	if widget.options['settings.4.option']:
		if widget.data['enableDarkMode']:
			widget.setStyleSheet(get_style('resource/qss/dark_with_mica.qss'))
		else:
			widget.setStyleSheet(get_style('resource/qss/light_with_mica.qss'))
		apply_mica(widget, widget.data['enableDarkMode'] or widget.options['settings.4.selector.2'] == 'colorMode.dark')
	else:
		if widget.data['enableDarkMode']:
			widget.setStyleSheet(get_style('resource/qss/dark_without_mica.qss'))
		else:
			widget.setStyleSheet(get_style('resource/qss/light_without_mica.qss'))


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


def switch_color_mode(widget: QWidget):
	if widget.options['settings.4.selector.2'] == 'colorMode.auto':
		widget.data['enableDarkMode'] = is_dark_mode()
	elif widget.options['settings.4.selector.2'] == 'colorMode.light':
		widget.data['enableDarkMode'] = False
	elif widget.options['settings.4.selector.2'] == 'colorMode.dark':
		widget.data['enableDarkMode'] = True
	save('data/cache.json', widget.data)
	load_theme(widget)


def text_update(string: str, label: QLabel) -> None:
	"""
	防止意外的窗口拉伸
	"""
	metrics = QFontMetrics(label.font())
	if metrics.width(string) > label.width():
		label.setText(QFontMetrics(label.font()).elidedText(string, Qt.ElideLeft, label.width()))
	else:
		label.setText(string)


# tree: core


def verify_formula(formula: list[str]) -> bool:
	"""
	仅支持单层算式，如'1+3.5*8/9'
	不支持多层算式，如'1+(3.5*8.9)'
	"""
	for i in range(len(formula)):
		if (i+1) % 2 == 0 and formula[i] in symbol_lst:
			continue
		elif verify_int(formula[i]):
			continue
		return False
	return True


def verify_int(integer: str):
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
