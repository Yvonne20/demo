from itertools import islice

from opt.opt_abstract import OptClass


class DaysMethod(OptClass):
    def __init__(self, route_len, best_target_ls, max_target_ls_len):
        super().__init__(route_len, best_target_ls, max_target_ls_len)

    def compute_target(self):
        target = (max(self.get_datets_dq) - self.get_datets_dq[0]) / 86400
        return target

    def compute_and_get_real_target(self):
        if self.get_real_profit:
            return sum(islice(self.get_datets_dq, self.get_real_len))

    def is_opt(self, value):
        return self.compare(value, self.best_target)

    @staticmethod
    def compare(target, compare_target):
        return target < compare_target

    @property
    def target_index(self):
        return 4

    @property
    def target_max_best(self):
        return False

    def abandable(self):
        return False

    @staticmethod
    def button_condition(target, best_target):
        return target > 2 * best_target
