from PyQt5.QtGui import QFont

__version__ = '1.9.3'

# operator
op_disp = ['+', '-', '×', '÷', ':', '//', '^']
op_calc = ['+', '-', '*', '/', '**']
op_brac = ['(', ')']
op_m = ['.', '/']
op_turn = {'×': '*', '÷': '/', ':': '/', '//': '/', '^': '**'}

default_options = {
	'settings.1.option.1': False,
	'settings.1.option.2': False,
	'settings.1.option.3': False,
	'settings.2.option.1': True,
	'settings.2.option.2': True,
	'settings.4.option': False,
	'settings.4.selector.1': 'Segoe UI',
	'settings.4.selector.2': '',
	'language': 'en_us',
	'window_title': 'WaiXCalc',
}

default_data = {
	'formula': ['0'],
	'isResult': False,
	'latest_pos_x': 0,
	'latest_pos_y': 0,
	'latest_width': 0,
	'enableDarkMode': False
}

rFont = QFont()
# font.setPointSize(8)

hFont = QFont()
hFont.setPointSize(24)

tFont = QFont()
tFont.setPointSize(10)

nFont = QFont()
nFont.setPointSize(12)

# tipFont = QFont()
# tipFont.setPointSize(4)
