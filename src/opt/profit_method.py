from opt.opt_abstract import OptClass


class ProfitMethod(OptClass):
    def __init__(self, route_len, best_target_ls, max_target_ls_len):
        super().__init__(route_len, best_target_ls, max_target_ls_len)

    def compute_target(self):
        if self.get_cost_dq:
            income = self.sum_income()
            target = income - sum(self.get_cost_dq)
            return target
        return None

    def compute_and_get_real_target(self):
        if self.get_real_profit:
            return self.get_real_profit

    def is_opt(self, value):
        return self.compare(value, self.best_target)

    @staticmethod
    def compare(target, compare_target):
        return target > compare_target

    @property
    def target_index(self):
        return 6

    @property
    def target_max_best(self):
        return True

    def abandable(self):
        return True

    @staticmethod
    def button_condition(target, best_target):
        return (best_target - target) / best_target > 10

