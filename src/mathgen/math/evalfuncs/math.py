# type: ignore

import math

from ..precise_num import PN
from .capture import use_as_global


@use_as_global("is_prime")
def _is_prime(*args: PN):
    for x in args:
        if not x.is_integer:
            return False
        if abs(x.num) < 2:
            return False
        if abs(x.num) == 2:
            continue
        if x.num % 2 == 0:
            return False
        for i in range(3, abs(x.num), 2):
            if x.num % i == 0:
                return False
    return True


@use_as_global("gcd")
def _gcd(*args: PN | int):
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        a, b = args
        if isinstance(a, int):
            a = PN(a)
        if isinstance(b, int):
            b = PN(b)
        return PN(math.gcd(a.num, b.num), math.lcm(a.den, b.den))
    return _gcd(args[0], _gcd(*args[1:]))


@use_as_global("lcm")
def _lcm(*args: PN):
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        a, b = args
        return PN(math.lcm(a.num, b.num), math.gcd(a.den, b.den))
    return _lcm(args[0], _lcm(*args[1:]))

@use_as_global("a2r")
def _a2r(arabic_number: PN):
    if not arabic_number.is_integer:
        raise ValueError("a2r: expected integer")
    if arabic_number.num < 1:
        raise ValueError("a2r: expected positive integer")
    if arabic_number.num > 3999:
        raise ValueError("a2r: expected integer less than 4000")
    
    values = [("M", "D", "C", 100), ("C", "L", "X", 10), ("X", "V", "I", 1)]
    num = arabic_number.num

    result = []
    def reduce(chars, val):
        nonlocal num
        result.append(chars * (num // val))
        num %= val
    
    for (ten, five, one, base) in values:
        reduce(ten, 10 * base)
        reduce(one + ten, 9 * base)
        reduce(five, 5 * base)
        reduce(one + five, 4 * base)
        reduce(one, base)
    
    return "".join(result)

@use_as_global("convert_base")
def _convert_base(num: PN | str, *args: PN):
    if len(args) == 0:
        raise ValueError("convert_base: missing 'to' target base")
    if len(args) > 2:
        raise ValueError("convert_base: too many arguments")
    
    if any(not x.is_integer for x in (num, *args)):
        raise ValueError("convert_base: expected integer arguments")
    
    is_neg = False
    if isinstance(num, str) and num[0] == "-":
        is_neg = True
        num = num[1:]
    elif num < 0:
        is_neg = True
        num = -num

    from_base = PN(10)
    to_base = args[-1]
    if len(args) == 2:
        from_base = args[0]
    
    if from_base != 10 and not isinstance(num, str):
        raise ValueError("convert_base: expected string input for non-decimal base")
    
    num = str(num)
    num_10 = int(num, from_base.num)

    digits = []
    while num_10:
        num_10, digit = divmod(num_10, to_base.num)
        digits.append(str(digit))
    
    ret = "".join(reversed(digits))
    if ret == "":
        return "0"
    return is_neg * "-" + ret

