from decimal import Decimal, InvalidOperation  # used
from fractions import Fraction  # used

from config import op_disp, op_turn, op_brac, op_calc, op_m


def verify_frac(frac: str) -> bool:
    """
    验证字符串是否是分数(Fraction)
    """
    lst = frac.split('/')
    if len(lst) == 2 and verify_monomial(frac):
        return True
    return False


def verify_monomial(monomial: str) -> bool:
    """
    验证字符串是否是不包含乘号或除号的单项式
    """
    lst_frac = monomial.split('/')
    if len(lst_frac) > 2:
        return False

    for i in lst_frac:
        if len(i.split('.')) > 2:
            return False
        for j in i:
            if j in [*op_brac, *op_disp, *op_calc]:
                return False
    return True


def calculate(formula: list) -> str:
    turn_frac = False
    for j in range(len(formula)):
        if formula[j] in op_turn.keys():
            formula[j] = op_turn[formula[j]]
        elif verify_frac(formula[j]):
            turn_frac = True

    for i in range(len(formula)):
        if formula[i] in [*op_calc, *op_brac]:
            continue
        else:
            if not turn_frac:
                formula[i] = f'Decimal("{formula[i]}")'
            else:
                formula[i] = f'Fraction("{formula[i]}")'

    return eval(''.join(formula))


def get_formula(s: str, frac: bool = False) -> list:
    """
    传入字符串，将字符串转化为算式，每个元素是单项式或运算符。
    """
    f = []
    op = [*op_disp, *op_calc, *op_brac]  # operator

    for i in range(len(s)):
        if len(f) == 0:
            f.append(s[i])
        elif s[i] in ['*', '/'] and s[i] == f[-1]:
            f[-1] += s[i]
        elif frac and s[i] == '/' and s[i] not in f[-1]:
            f[-1] += s[i]
        elif f[-1] in op or s[i] in op:
            f.append(s[i])
        else:
            f[-1] += s[i]

    return f
