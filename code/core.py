from decimal import Decimal  # used
from fractions import Fraction
from typing import Union

from config import op_disp, op_m, op_turn, op_brac, op_calc


def verify_formula(formula: list[str]) -> bool:
    """
    验证列表中的算式（get_formula()的结果）是否是calculate()可进行计算的
    require rewrite
    """
    for i in range(len(formula)):
        if (i+1) % 2 == 0 and formula[i] in op_disp:
            continue
        elif verify_monomial(formula[i]):
            continue
        return False
    return True


def verify_frac(frac: str) -> bool:
    """
    验证字符串是否是分数(Fraction)
    """
    lst = frac.split('/')
    if len(lst) == 2 and lst[0].isdigit() and lst[1].isdigit():  # and verify_monomial(frac)
        return True
    return False


def verify_monomial(monomial: str) -> bool:
    """
    验证字符串是否是整数、小数或分数 require rewrite
    """
    symbol_frequency = {'.': 0, '/': 0}

    if not monomial or monomial[-1] in op_m:
        return False

    for i in monomial:
        if i.isdigit() or i in op_m:
            if i in op_turn or i in op_brac:
                return False
            elif i in op_m:
                if i == '/' and not verify_frac(monomial):
                    return False
                elif symbol_frequency['.'] > 2 or symbol_frequency['/'] > 1:
                    return False
                symbol_frequency[i] += 1
        else:
            return False

    return True


def calculate(formula: list) -> Union[Fraction, float, int]:
    turn_frac = False
    for j in range(len(formula)):
        if formula[j] in op_turn.keys():
            formula[j] = op_turn[formula[j]]
        elif verify_frac(formula[j]):
            turn_frac = True
            break

    for i in range(len(formula)):
        if formula[i] in [*op_calc, *op_brac]:
            continue
        else:
            if not turn_frac:
                formula[i] = f'Decimal("{formula[i]}")'
            else:
                formula[i] = f'Fraction("{formula[i]}")'

    return eval(''.join(formula))


def get_formula(string: str) -> list[str]:
    """
    传入字符串，将字符串转化为算式，每个元素是一串数字或一个符号。
    可以用()作嵌套。
    :param string:
    :return list[str]:
    """
    def length(lst: list):
        value = 0
        for _ in lst:
            if isinstance(_, list):
                value += length(_)+2
            else:
                value += len(_)
        return value

    f = []
    s = string.replace('**', '^').replace('//', ':')
    for i in range(len(s)):
        if i > len(s)-1:
            break
        if f and not isinstance(f[-1], list):
            if s[i] == '(':
                inner = get_formula(s[i+1:])
                f = [*f, inner]
                s = s[:i] + s[i+length(inner)+1:]
            elif s[i] == ')':
                return f
            elif f[-1] in op_disp or s[i] in op_disp:
                f = [*f, s[i]]
            else:
                if not isinstance(f[-1], list):
                    f = [*f[:-1], f[-1] + s[i]]
                else:
                    f = [*f, s[i]]
        else:
            f = [*f, s[i]]
    return f
