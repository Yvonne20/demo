from enum import Enum

from opt.days_method import DaysMethod
from opt.profit_method import ProfitMethod


class OptMethod(Enum):
    MAX_PROFIT = 1
    MIN_DAYS = 2


def opt_fac(method):
    if method.value == OptMethod.MAX_PROFIT.value:
        return ProfitMethod
    elif method.value == OptMethod.MIN_DAYS.value:
        return DaysMethod
