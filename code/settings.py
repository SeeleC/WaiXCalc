from PyQt5.QtGui import QFont

symbol_lst = ['+', '-', '×', '÷', '^']
symbol_lst_2 = ['.', '/']
bracket_lst = [['(', '[', '{'], [')', ']', '}']]
symbol_turn = {'+': '+', '-': '-', '×': '*', '÷': '/', '//': '/', '^': '**', '**': '**'}
num_widthes = {
	'1': 30.4, '2': 31.8, '3': 33.4, '4': 33.4, '5': 33.4, '6': 33.4, '7': 30.3, '8': 33.4, '9': 33.4, '0': 31.8,
	'.': 20, '/': 20, 'E': 30.5
}  # number weight / 640

font = QFont()
font.setFamily('Microsoft Yahei UI')
font.setPointSize(8)

mwFont = QFont()
mwFont.setFamily('Microsoft Yahei UI')
mwFont.setPointSize(24)

textFont = QFont()
textFont.setFamily('Microsoft Yahei UI')
textFont.setPointSize(10)

# tipFont = QFont()
# tipFont.setFamily('Microsoft Yahei UI')
# tipFont.setPointSize(4)
