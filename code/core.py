from decimal import Decimal, InvalidOperation  # used
from fractions import Fraction  # used

from config import op_disp, op_turn, op_brac, op_calc


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


def get_formula(string: str) -> list[str]:
    """
    传入字符串，将字符串转化为算式，每个元素是一串数字或一个符号。
    可以用()作嵌套。
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
