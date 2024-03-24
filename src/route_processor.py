import params

from collections import deque


def route2days(route, order_obj, table_obj):
    order_df = order_obj.new_df
    pre_port = order_obj.initPort
    ts = order_obj.initTS

    run_days, idle_ts = 0, 0
    for i in range(len(route)):
        no = route[i]
        port = order_df[order_df.no == no].iloc[0].port
        start_ts = order_df[order_df.no == no].iloc[0].start_ts
        run_day = table_obj.days_dic[pre_port][port]
        run_days += run_day
        ts += run_day * 86400
        if start_ts and start_ts > ts:
            wait_ts = start_ts - ts
            ts = start_ts
            idle_ts += wait_ts

        idle_ts += params.days.stay * 86400
        ts += params.days.stay * 86400
        pre_port = port
    idle_days = idle_ts / 86400
    return run_days, idle_days

def compute_profit(run_days, idle_days, port_nums, income):
    total_days = run_days + idle_days
    cost = run_days * params.fee.OIL_RUN + idle_days * params.fee.OIL_IDLE + params.fee.DAILY * total_days + \
           port_nums * params.fee.PORTFEE_default
    return income - cost

def route2profit(route, order_obj, table_obj, income):
    run_days, idle_days = route2days(route, order_obj, table_obj)
    return compute_profit(run_days, idle_days, len(route), income)

def sum_cost(run_days, idle_days, port_nums, fee):
    total_days = run_days + idle_days
    return run_days * fee.OIL_RUN + idle_days * fee.OIL_IDLE + total_days * fee.DAILY + port_nums * fee.PORTFEE_default

def sum_income(group_set, income_dic):
    sum_ = 0
    for no in group_set:
        sum_ += income_dic[no]['income']

    return sum_

def check_route_valid_by_rank(route, prior_set):
    if prior_set:
        order_s = set(route)
        for set_ in prior_set.values():
            for load in set_[0]:
                if load in order_s:
                    for discharge in set_[1]:
                        if discharge not in order_s:
                            return False
    return True

def check_need_valid(route_group_set, need_ls):
    need_set = {v for v in need_ls if v > 0}
    for group in filter(lambda x: x > 0, route_group_set):
        if group in need_set:
            need_set.remove(group)
    if need_set:
        return False
    return True

def route2check(route, item_dic, group_dic):
    group_len_dic = {-1: 0}
    for group in group_dic:
        if group > 0:
            group_len_dic[group] = len(group_dic[group])
        elif group < 0:
            group_len_dic[-1] = len(group_dic[group])
        else:
            raise ValueError("Bug...")

    route_check = deque()
    for item in route:
        group = item_dic[item]
        group_len_dic[group] -= 1
        if group_len_dic[-1] == 0 and group_len_dic[group] == 0:
            route_check.append(2)
        elif group_len_dic[group] == 0:
            route_check.append(1)
        else:
            route_check.append(-1)
    return route_check

def check_duplicate(best_target_ls):
    route_set = set()
    ls = []
    for index in range(len(best_target_ls)):
        route = best_target_ls[index][0]
        if tuple(route) not in route_set:
            ls.append(index)
            route_set.add(tuple(route))
    return [best_target_ls[idx] for idx in ls]


