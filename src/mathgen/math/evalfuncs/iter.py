# type: ignore

from typing import Iterable

from ..precise_num import PN
from .capture import start_stop_step_args, use_as_global


@use_as_global("range")
def _range(*args):
    start, stop, step = start_stop_step_args(args)
    is_less = start < stop
    while is_less and start < stop or not is_less and start > stop:
        yield start
        start += step

@use_as_global("sum")
def _sum(it: Iterable[PN], start: PN = PN(0)):
    return sum(it, start)