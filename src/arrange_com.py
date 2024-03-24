import copy
from collections import defaultdict
from functools import reduce, partial


pos_zero = 0.01
neg_zero = -0.01


class ArrangeCom:
    def __init__(self, current_com, ship_cfg, exclude_tb):
        self.com_limit = ship_cfg['com_limit']
        self.com_near = ship_cfg['com_near']
        self.current_com_orig = current_com
        self.current_com = copy.deepcopy(self.current_com_orig)
        self.com_struc = None                   # Empty / Full / Half
        self.exclude_tb = exclude_tb
        self.com_limit_vol = reduce(lambda a, b: a + b, self.com_limit.values())
        self.com_len = len(self.current_com)
        self.plan = []
        self.reset()

    def loading_half(self, cargo_name, cargo_group, vol, plan, is_plan=True):
        com = self.find_resid_com(cargo_name)
        if com > -1:
            residVol = self.com_limit[com] - self.current_com[com]['vol']
            if residVol >= vol:
                self.loading(com, cargo_name, cargo_group, vol)
                if is_plan:
                    plan.append((com, cargo_name, vol))
                if residVol - vol < pos_zero:
                    self.update_com_struc(com, 2, 1)
                return 0
            else:
                self.loading(com, cargo_name, cargo_group, residVol)
                if is_plan:
                    plan.append((com, cargo_name, residVol))
                self.update_com_struc(com, 2, 1)
            return vol - residVol
        else:
            return vol

    def loading(self, com, cargo_name, cargo_group, vol):  # Ensure Loading Volume is Legality
        if not self.current_com[com]['cargo_name']:
            self.current_com[com]['cargo_name'] = cargo_name
            self.current_com[com]['group_name'] = cargo_group
        self.current_com[com]['vol'] += vol

        if self.current_com[com]['vol'] > self.com_limit[com] + 0.0001:
            raise ValueError("ArrangeCom loading ERROR...")

    def discharging_recursive(self, cargo_name, vol, plan, is_plan=True):
        if not cargo_name:
            return True

        for com_group in [2, 1]:
            for com in self.com_struc[com_group]:
                if self.current_com[com]['cargo_name'] == cargo_name:
                    updateVol = self.current_com[com]['vol'] + vol
                    if updateVol > neg_zero:
                        if updateVol > pos_zero:
                            self.discharging(com, vol)
                            if is_plan:
                                plan.append((com, cargo_name, vol))
                        else:
                            dis_vol = -self.current_com[com]['vol']
                            self.discharging(com, dis_vol)
                            if is_plan:
                                plan.append((com, cargo_name, dis_vol))
                            self.update_com_struc(com, com_group, 0)
                            self.current_com[com]['pre3'].append(self.current_com[com]['group_name'])
                            self.current_com[com]['pre3'].pop(0)
                        return True
                    else:
                        dis_vol = -self.current_com[com]['vol']
                        self.discharging(com, dis_vol)
                        if is_plan:
                            plan.append((com, cargo_name, dis_vol))
                        self.update_com_struc(com, com_group, 0)
                        self.current_com[com]['pre3'].append(self.current_com[com]['group_name'])
                        self.current_com[com]['pre3'].pop(0)
                        if self.discharging_recursive(cargo_name, updateVol, plan):
                            return True
        return False

    def discharging(self, com, vol):
        self.current_com[com]['vol'] += vol
        if self.current_com[com]['vol'] < pos_zero:
            self.current_com[com]['cargo_name'] = ''
            self.current_com[com]['group_name'] = ''
            self.current_com[com]['vol'] = 0

    def current_com_to_struc(self):
        com_struc = [[], [], []]
        for com in self.current_com:
            cargo_name = self.current_com[com]['cargo_name']
            if not cargo_name:
                com_struc[0].append(com)
            elif self.com_limit[com] - self.current_com[com]['vol'] < pos_zero:
                com_struc[1].append(com)
            else:
                com_struc[2].append(com)
        return com_struc

    def update_com_struc(self, com, from_, to_):
        self.com_struc[from_].remove(com)
        self.com_struc[to_].append(com)

    def find_resid_com(self, cargo_name):
        for com in self.com_struc[2]:
            if self.current_com[com]['cargo_name'] == cargo_name:
                return com
        return -1

    def is_near_exclude(self, com, group_name):
        for com_near in self.com_near[com]:
            if self.current_com[com_near]['cargo_name'] and \
               self.exclude_tb[group_name][self.current_com[com_near]['group_name']] == -1:
                return True
        return False

    def sort_by_near(self, cargo_group):
        first_ls = set()
        for com in self.com_struc[1] + self.com_struc[2]:
            if self.current_com[com]['group_name'] == cargo_group:
                near_ls = self.com_near[com]
                for c in near_ls:
                    if c not in first_ls and c in self.com_struc[0]:
                        first_ls.add(c)
                        yield c
        for com in self.com_struc[0]:
            if com not in first_ls:
                yield com

    def is_pre3_exclude(self, com, group_name):
        for pre3_group in self.current_com[com]['pre3']:
            if pre3_group and self.exclude_tb[group_name][pre3_group] == -1:
                return True
        return False

    def reset(self):
        for com in self.current_com_orig:
            self.current_com[com]['cargo_name'] = self.current_com_orig[com]['cargo_name']
            self.current_com[com]['group_name'] = self.current_com_orig[com]['group_name']
            self.current_com[com]['vol'] = self.current_com_orig[com]['vol']
            self.current_com[com]['pre3'] = self.current_com_orig[com]['pre3'].copy()
        self.com_struc = self.current_com_to_struc()

    def print_current_com(self):
        vol_tot = 0
        limit_tot = 0
        dic = defaultdict(int)
        for com in self.current_com:
            print("| ", com, self.current_com[com])
            dic[self.current_com[com]['cargo_name']] += self.current_com[com]['vol']
            vol_tot += self.current_com[com]['vol']
            limit_tot += self.com_limit[com]
        print(f"Cargo INFO: {dic}, Total Vol={vol_tot}, Compartment Vol Limit={limit_tot}")

    def arrange_tot(self, cargo_ls):
        if not self.check_cargo_ls_valid(cargo_ls):
            return False

        valid = self.buffer(cargo_ls)
        self.reset()
        return valid

    def get_current_com_copy(self):
        return copy.deepcopy(self.current_com)

    def check_cargo_ls_valid(self, cargo_ls):
        vol_dic = self.get_orig_cargo_vol()
        current_vol = reduce(lambda a, b: a + b, vol_dic.values())

        for item in cargo_ls:
            cargo_name = item[0]
            vol = item[2]
            updateVol = vol_dic[cargo_name] + vol
            current_vol += vol
            if updateVol < neg_zero or current_vol > self.com_limit_vol:
                return False
            vol_dic[cargo_name] = updateVol
        return True

    def loading_semi(self, com, cargo_name, cargo_group, vol, plan, is_plan=True):
        com_resid_vol = self.com_limit[com] - self.current_com[com]['vol']
        if vol < com_resid_vol:
            self.loading(com, cargo_name, cargo_group, vol)
            if is_plan:
                plan.append((com, cargo_name, vol))
            self.update_com_struc(com, 0, 2)
            return 0
        else:
            self.loading(com, cargo_name, cargo_group, com_resid_vol)
            if is_plan:
                plan.append((com, cargo_name, com_resid_vol))
            self.update_com_struc(com, 0, 1)
            return vol - com_resid_vol

    def loading_semi_recursive(self, cargo_name, cargo_group, vol, empty_ls, plan, is_plan=True):
        resid_vol = vol
        for com in empty_ls.copy():
            if self.is_pre3_exclude(com, cargo_group) or self.is_near_exclude(com, cargo_group):
                continue
            resid_vol = self.loading_semi(com, cargo_name, cargo_group, resid_vol, plan, is_plan)
            empty_ls.remove(com)
            if resid_vol < pos_zero:
                return True
        return False

    def get_orig_cargo_vol(self):
        dic = defaultdict(int)
        for com in self.current_com_orig:
            if self.current_com_orig[com]['vol'] > 0:
                dic[self.current_com_orig[com]['cargo_name']] += self.current_com_orig[com]['vol']
        return dic

    def get_plan(self):
        return copy.deepcopy(self.plan)

    @staticmethod
    def copy_com_struc(com_struc):
        return [item.copy() for item in com_struc]

    def gen_cargos_avail_com_ls(self, cargo_ls):
        avail_com_ls = []
        for cargo, cargo_group, vol in cargo_ls:
            if vol <= pos_zero or not cargo:
                avail_com_ls.append([])
            else:
                avail_com_ls.append(list(filter(lambda com: not self.is_pre3_exclude(com, cargo_group),
                                                self.com_struc[0])))
        return avail_com_ls

    def buffer(self, cargo_ls):
        self.avail_com_ls = self.gen_cargos_avail_com_ls(cargo_ls)
        ns = [len(ls) for ls in self.avail_com_ls if len(ls) > 0]
        repeat_ls = self.get_repeat_ls(cargo_ls)

        used = set()
        dic = defaultdict(set)
        self.count = 0
        return self.loop(self.avail_com_ls, ns, partial(self.arrange, cargo_ls), used, dic, repeat_ls)

    def arrange(self, cargo_ls, ls):
        values = iter(ls)
        selec_ls = []
        for i in range(len(self.avail_com_ls)):
            if self.avail_com_ls[i]:
                selec_ls.append(self.avail_com_ls[i][next(values)])
        self.reset()
        self.plan.clear()
        selec_gen = iter(selec_ls)
        empty_ls = self.com_struc[0].copy()
        for v in selec_ls:
            if v in empty_ls:
                empty_ls.remove(v)
        valid = True
        vol_dic = self.get_orig_cargo_vol()
        current_vol = reduce(lambda a, b: a + b, vol_dic.values())

        for i in range(len(cargo_ls)):

            tmp_plan = []
            cargo_name, cargo_group, vol = cargo_ls[i]
            if not cargo_name:
                self.plan.append([('', '', '')])
                continue
            updateVol = vol_dic[cargo_name] + vol
            current_vol += vol
            if updateVol < neg_zero or current_vol > self.com_limit_vol:
                valid = False
                break
            vol_dic[cargo_name] = updateVol

            if vol > 0:
                com = next(selec_gen)
                if self.current_com[com]['cargo_name'] and \
                        (self.current_com[com]['cargo_name'] != cargo_name or
                        self.com_limit[com] - self.current_com[com]['vol'] < neg_zero):
                    valid = False
                    break
                com_resid = self.find_resid_com(cargo_name)
                resid_vol = self.loading_half(cargo_name, cargo_group, vol, tmp_plan)

                is_com_no_repeat = -1 < com_resid != com
                if resid_vol < pos_zero and (resid_vol >= pos_zero and is_com_no_repeat):
                    empty_ls.append(com)

                if resid_vol > pos_zero:
                    if self.com_limit[com] - self.current_com[com]['vol'] > pos_zero:
                        if com_resid == -1 or is_com_no_repeat:
                            if self.is_pre3_exclude(com, cargo_group) or self.is_near_exclude(com, cargo_group):
                                valid = False
                                break
                            resid_vol = self.loading_semi(com, cargo_name, cargo_group, resid_vol, tmp_plan)

                    if resid_vol > pos_zero and not self.loading_semi_recursive(cargo_name, cargo_group, resid_vol,
                                                                                empty_ls, tmp_plan):
                        valid = False
                        break
            else:
                if not self.discharging_recursive(cargo_name, vol, tmp_plan):
                    valid = False
                    break
            self.plan.append(tmp_plan)

        if valid:
            return True

        self.count += 1
        if self.count > 10000:
            return False

    def loop(self, avail_com_ls, ns, f, used, dic, repeat_ls):
        def fn(i, idxs):
            return f([i] + idxs)

        if len(ns) > 0:
            for i in range(ns[0]):
                used2 = used.copy()
                dic2 = defaultdict(set)
                for k in dic:
                    dic2[k] = dic[k].copy()

                idx, valid, cargo, cargo_group = self.get_next(repeat_ls)
                if self.is_near_exclude(avail_com_ls[idx][i], cargo_group):
                    continue
                if i not in used2 or (valid is False and i in dic2[cargo]):
                    used2.add(i)
                    dic2[cargo].add(i)
                    return self.loop(avail_com_ls[idx+1:], ns[1:], partial(fn, i), used2, dic2, repeat_ls[idx+1:])
        else:
            return f([])

    def get_next(self, repeat_ls):
        idx = 0
        for valid, cargo, cargo_group, vol in repeat_ls:
            if vol > pos_zero:
                return idx, valid, cargo, cargo_group
            idx += 1

    def get_repeat_ls(self, cargo_ls):
        used = set()
        ls = []
        for item in cargo_ls:
            cargo = item[0]
            cargo_group = item[1]
            vol = item[2]
            if cargo and cargo not in used:
                ls.append((True, cargo, cargo_group, vol))
                used.add(cargo)
            else:
                ls.append((False, cargo, cargo_group, vol))
        return ls


