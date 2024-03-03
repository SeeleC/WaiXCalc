from PyQt5.QtCore import QTextStream, QFile, Qt, QUrl
from PyQt5.QtGui import QPixmap, QFontMetrics, QDesktopServices
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget
from typing import Union
from json import load, dump
from os import mkdir, listdir, remove, path
from winreg import ConnectRegistry, HKEY_CURRENT_USER, OpenKey, EnumValue
from win32mica import ApplyMica, MICAMODE

from config import default_options, default_data, rFont


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

	with open(f'resources/lang/{language}.json', 'r', encoding='utf-8') as f:
		return load(f)


def get_trans_info() -> dict[str]:
	"""
	遍历lang文件夹、获取json文件信息
	"""
	data = {}
	for i in sorted(listdir('resources/lang')):
		i = i[:-5]
		if i != 'template':
			with open(f'resources/lang/{i}.json', 'r', encoding='utf-8') as f:
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
			widget.setStyleSheet(get_style('resources/qss/dark_with_mica.qss'))
		else:
			widget.setStyleSheet(get_style('resources/qss/light_with_mica.qss'))
		apply_mica(widget, widget.data['enableDarkMode'] or widget.options['settings.4.selector.2'] == 'colorMode.dark')
	else:
		if widget.data['enableDarkMode']:
			widget.setStyleSheet(get_style('resources/qss/dark_without_mica.qss'))
		else:
			widget.setStyleSheet(get_style('resources/qss/light_without_mica.qss'))


def mend_dict_item(d, rd) -> dict[str, dict]:
	for i in rd.keys():
		try:
			d[i] = d[i]
		except KeyError:
			d[i] = rd[i]
	return d


def open_url(url: str):
	QDesktopServices.openUrl(QUrl(url))


def save(filename: str, data) -> None:
	"""
	快速保存
	"""
	with open(filename, 'w', encoding='utf-8') as f:
		dump(data, f, indent=1)


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
