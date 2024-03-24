from abc import ABC, abstractmethod
from collections import deque


class OptClass(ABC):

    def __init__(self, route_len, best_target_ls, max_target_ls_len):
        self.__income_dic = dict()
        self.__cost_dq = deque([0 for i in range(route_len)])
        self.__datets_dq = deque([0 for i in range(route_len)])
        self.__best_target_ls = best_target_ls
        self.__max_target_ls_len = max_target_ls_len

        self.__route_len = route_len
        self.__best_target = None
        self.__real_profit = None
        self.__real_len = None

    @abstractmethod
    def compute_target(self):
        pass

    @abstractmethod
    def is_opt(self, value):
        pass

    @staticmethod
    @abstractmethod
    def compare(target, compare_target):
        """ True if target is better than compare_target, else False """
        pass

    @property
    @abstractmethod
    def target_max_best(self):
        """ True if target Maximum is Best, else False """
        pass

    @abstractmethod
    def abandable(self):
        """ True if routing item allow to be abandon, else False """
        pass

    @staticmethod
    @abstractmethod
    def button_condition(target, best_target):
        """ The Condition of Minimum target """
        pass

    @property
    @abstractmethod
    def target_index(self):
        pass

    @abstractmethod
    def compute_and_get_real_target(self):
        pass

    def set_best_target(self, best_value):
        self.__best_target = best_value

    def set_real_profit(self, real_profit, length):
        self.__real_profit = real_profit
        self.__real_len = length

    def set_target(self, value):  # return best or better than
        if self.is_opt(value):
            self.set_best_target(value)
            return True
        elif self.__best_target_ls and self.compare(value, self.__best_target_ls[-1][self.target_index]):
            return True
        return False

    def set_route_len(self, route_len):
        self.__route_len = route_len

    def reset(self):
        self.__income_dic.clear()
        self.__cost_dq = deque([0 for i in range(self.__route_len)])
        self.__datets_dq = deque([0 for i in range(self.__route_len)])
        self.__real_profit = None

        if self.__best_target_ls:
            self.set_best_target(self.__best_target_ls[0][self.target_index])
        else:
            self.set_best_target(-99999999)

    def sum_income(self):
        total_income = 0
        for income in self.get_income_dic.values():
            total_income += income

        return total_income

    def is_in(self, real_profit):
        if len(self.__best_target_ls) < self.__max_target_ls_len:
            return 1
        elif self.compare(real_profit, self.__best_target_ls[-1][self.target_index]):
            return 2
        return 0

    def add_to_target_ls(self, row, mode):
        if mode == 1:
            self.__best_target_ls.append(row)
        elif mode == 2:
            self.__best_target_ls.append(row)
            self.__best_target_ls.sort(key=lambda x: x[self.target_index], reverse=self.target_max_best)
            self.__best_target_ls.pop()
        else:
            raise NotImplementedError

    def add_to_best_target_ls(self, row, real_profit):
        if len(self.__best_target_ls) < self.__max_target_ls_len:
            self.__best_target_ls.append(row)
            return True
        elif self.compare(real_profit, self.__best_target_ls[-1][self.target_index]):
            self.__best_target_ls.append(row)
            self.__best_target_ls.sort(key=lambda x: x[self.target_index], reverse=self.target_max_best)
            self.__best_target_ls.pop()
            return True
        return False

    @property
    def best_target(self):
        return self.__best_target

    @property
    def get_real_profit(self):
        return self.__real_profit

    @property
    def get_real_len(self):
        return self.__real_len

    @property
    def get_income_dic(self):
        return self.__income_dic

    @property
    def get_cost_dq(self):
        return self.__cost_dq

    @property
    def get_datets_dq(self):
        return self.__datets_dq

    @property
    def get_route_len(self):
        return self.__route_len

