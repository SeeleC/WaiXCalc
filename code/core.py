from decimal import Decimal, InvalidOperation
from fractions import Fraction
from re import match
from typing import Union

from config import symbol_lst, symbol_lst_2, symbol_turn, bracket_lst


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


def calculate(formula: list) -> Union[Fraction, float, int]:
    """
    传入formula，从左到右计算，优先计算嵌套的列表内算式。
    为了兼容分数，所以 除号(/) 需要用 双斜杠(//) 来代替。
    :param formula:
    :return:
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
