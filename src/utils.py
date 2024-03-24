import itertools
import pandas as pd
from datetime import datetime
import math

def cntComb(lsLen, num):
    cnt = 0
    for result in itertools.combinations(range(lsLen), num):
        cnt += 1
    return cnt

def cntCombSeq(lsLen, num):
    n = lsLen
    result = 1
    while n >= 2:
        result *= cntComb(n, num)
        n -= 2
    return result

def flattenLs(ls):
    outLs = []
    for row in ls:
        for e in row:
            outLs.append(e)
    return outLs

def gen_pos(lsLen, pos, shift):
    start = max(pos - shift, 0)
    end = min(pos + shift, lsLen-1)
    return range(start, end+1)

def gen_ablePos(lsLen, pos, shift, boolLs):
    ableLs = gen_pos(lsLen, pos, shift)
    return [idx for idx in ableLs if not boolLs[idx]]

def check_prior_valid(prior_set, route):
    for set_ in prior_set:
        prior = False
        for num in route:
            if num in set_[1] and not prior:
                return False
            elif num == set_[0]:
                prior = True
    return True

def bestLs2info(best_ls, order_df, ship_com=None):
    info_dic = dict()

    rank = 0
    for best in best_ls:
        dic = {"opt_schedule": dict()}
        for i in range(best[7]):
            order_no = best[0][i]
            port = order_df.loc[order_no].port
            port_no = order_df.loc[order_no].port_no
            date_ = datetime.fromtimestamp(best[1][i])
            if order_df.loc[order_no].end_ts != 0:
                start = datetime.fromtimestamp(order_df.loc[order_no].start_ts).strftime("%Y-%m-%d")
                end = datetime.fromtimestamp(order_df.loc[order_no].end_ts).strftime("%Y-%m-%d")
            else:
                start, end = '', ''
            cargo = order_df.loc[order_no].cargo
            append_str = f'({order_df.loc[order_no].weights})' if order_df.loc[order_no].weights else ''
            demand = f'{order_df.loc[order_no].demand}{append_str}'
            wait = best[2][i] / 86400
            stay = order_df.loc[order_no].stay_days
            plan = parse_plan(best[9][i], ship_com, order_df.loc[order_no].density)

            dic["opt_schedule"][i] = {"order_no": order_no,
                                      "port": port,
                                      "port_no": port_no,
                                      "arrive": date_.strftime("%Y-%m-%d %H:%M"),
                                      "start": start,
                                      "end": end,
                                      "cargo": cargo,
                                      "demand": demand,
                                      "wait": wait,
                                      "stay": stay,
                                      "com": plan}
        dic["distance"] = best[3]
        dic["total_days"] = best[4] / 86400
        dic["cost"] = best[5]
        dic["profit"] = best[6]
        dic["TCE"] = round(dic["profit"] / dic["total_days"], 0)
        dic["len"] = best[7]
        info_dic[rank] = dic

        rank += 1
    return info_dic

def parse_plan(plan, ship_com, density):
    if not plan:
        return ''
    ls = []
    for act in plan:
        if act[1]:
            ls.append(f'{ship_com[act[0]]}:{round(act[2] * density, 1)}')
    return tuple(ls)

def show_info_dic(info_dic):
    for rank in info_dic:
        dic = info_dic[rank]
        ls = []
        for i in range(info_dic[rank]["len"]):
            ls.append(dic["opt_schedule"][i].values())
        print("\n### RANK ###", rank)
        print(pd.DataFrame(ls, columns=['order_no', 'port', 'port_no', 'arrive', 'laycan_start',
                                        'laycan_end', 'cargo', 'demand', 'wait', 'stay', 'com']))
        for key in dic:
            if key != "opt_schedule" and key != "len":
                print(key, ":", dic[key])

class CountRoutes:
    def __init__(self, orig=None, single=None, prior=None, panama_struc=None):

        self.orig = orig.copy() if orig else []
        self.single = single.copy() if single else []
        self.prior2 = dict()
        self.panama_struc = panama_struc.copy() if panama_struc else []
        if prior:
            for k in prior:
                item = prior[k]
                if len(item[0]) == 0 or len(item[1]) == 0:
                    for row in item[0] + item[1]:
                        self.single.append(row)
                else:
                    self.prior2[k] = item

    def arrange_single(self, orig_len, single_len):
        s = orig_len + 1
        result = 1
        while s < orig_len + single_len + 1:
            result *= s
            s += 1
        return result

    def arrange_prior(self, orig_len, load_len, discharging_len):
        prior_len = load_len + discharging_len
        return self.arrange_single(orig_len, prior_len)        \
                * (load_len * discharging_len)                 \
                * (math.factorial(load_len+discharging_len-2)) \
                / math.factorial(prior_len)

    def count(self):
        return self.count_base(self.orig, self.single, self.prior2)

    def count_base(self, orig, single, prior):
        result = 1
        if len(single):
            result *= self.arrange_single(len(orig), len(single))
        if prior:
            orig_len = len(orig)+len(single)
            for load, discharg in prior.values():
                result *= self.arrange_prior(orig_len, len(load), len(discharg))
                orig_len += (len(load) + len(discharg))
        return result

    def count_panama(self):
        if not self.panama_struc:
            raise ValueError("PLEASE INPUT panama_struc")
        group1, panama, group2 = self.panama_struc
        result = 1
        result *= self.count_base(group1['original'], group1['single'], group1['prior'])
        result *= self.count_base(group2['original'], group2['single'], group2['prior'])
        return result

