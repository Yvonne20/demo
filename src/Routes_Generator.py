import copy
import itertools as it


class RoutesGen:
    def __init__(self, laycan_dic, struc, abandon=True):
        self.laycan_dic = copy.deepcopy(laycan_dic)
        self.struc = struc
        self.abandon = abandon

    def gen_routes(self):
        g1, panama, g2 = copy.deepcopy(self.struc)
        is_panama = panama and (g2['original'] or g2['prior'] or g2['single'])

        rows_old = self.loop_rows(g1)
        for row in rows_old:
            if is_panama:
                for row2 in self.loop_rows(g2):
                    yield row + [panama] + row2
            else:
                yield row

        if self.abandon:
            g1_copy = g1.copy()
            g2_copy = copy.copy(g2)

            for selec in range(1, len(self.laycan_dic['noneed_ls']) + 1):
                abandon_ls = self.pick_abandon(selec)
                for drop in abandon_ls:
                    drop_ls = [v for item in drop for k in item for v in item[k]]
                    drop_k_ls = [k for item in drop for k in item]
                    isg2 = False
                    if is_panama:
                        g2_copy['prior'] = {k: g2['prior'][k] for k in g2['prior'] if k not in drop_k_ls}
                        g2_copy['single'] = [k for k in g2['single'] if k not in drop_ls]

                        if g2_copy['original'] or g2_copy['single'] or g2_copy['prior']:
                            isg2 = True

                    g1_copy['prior'] = {k: g1['prior'][k] for k in g1['prior'] if k not in drop_k_ls}
                    g1_copy['single'] = [k for k in g1['single'] if k not in drop_ls]

                    for row in self.loop_rows(g1_copy):
                        if isg2:
                            for row2 in self.loop_rows(g2_copy):
                                yield row + [panama] + row2
                        else:
                            yield row

    def loop_rows(self, dic):
        rows_old = [dic['original']]
        length = len(dic['original'])
        for ball in dic['single']:
            rows_old = self.yield_rows_by_laycan(ball, rows_old, length)
            length += 1
        for loads, discharges in dic['prior'].values():
            rows_old = self.yield_multi_rows(loads, discharges, rows_old, length)
            length += len(loads) + len(discharges)

        return rows_old

    def yield_multi_rows(self, loads, discharges, rows_old, length):
        for row in rows_old:
            prd_dic = {b: self.find_prd_idxes(row, b, length) for b in loads + discharges}
            for ball_start in loads:
                for ball_end in discharges:
                    start_startIdx, start_endIdx = self.find_prd_idxes(row, ball_start, length)
                    end_startIdx, end_endIdx = self.find_prd_idxes(row, ball_end, length)

                    resid_loads = loads.copy()
                    resid_discharges = discharges.copy()
                    resid_loads.remove(ball_start)
                    resid_discharges.remove(ball_end)

                    for i in range(start_startIdx, start_endIdx + 1):
                        for j in range(min(max(i+1, end_startIdx + 1), end_endIdx + 1), end_endIdx + 2):
                            rows_copy = [self.insert_row(self.insert_row(row, i, ball_start), j, ball_end)]
                            l = j
                            valid = True
                            for ball2 in resid_loads:
                                tmp_start, tmp_end = max(i+1, prd_dic[ball2][0] + 1), min(l, prd_dic[ball2][1]+1)
                                if tmp_start > tmp_end:
                                    valid = False
                                    break
                                rows_copy = self.inserted_between(rows_copy, tmp_start, tmp_end, ball2)
                                l += 1
                            if valid:
                                for ball2 in resid_discharges:
                                    tmp_start, tmp_end = max(i+1, prd_dic[ball2][0]+1), min(l, prd_dic[ball2][1]+1)
                                    if tmp_start > tmp_end:
                                        valid = False
                                        break
                                    rows_copy = self.inserted_between(rows_copy, tmp_start, tmp_end, ball2)
                                    l += 1
                                if valid:
                                    for row2 in rows_copy:
                                        yield row2

    def yield_rows_by_laycan(self, ball, rows_old, length):
        for row in rows_old:
            begin_i, end_i = self.find_prd_idxes(row, ball, length)
            for row2 in self.inserted_between([row], begin_i, end_i, ball):
                yield row2

    @staticmethod
    def insert_row(row, i, ball):
        row_copy = [v for v in row]
        return row_copy[:i] + [ball] + row_copy[i:]

    @staticmethod
    def inserted_between(rows, begin_i, end_i, ball):
        for row in rows:
            for i in range(0, end_i - begin_i + 1):
                yield row[:begin_i + i] + [ball] + row[begin_i + i:]

    def find_prd_idxes(self, row, ball, length):
        start = self.laycan_dic[ball]['start_ts']
        end = self.laycan_dic[ball]['end_ts']

        if not start and not end:
            return [0, length]
        else:
            if length == 0:
                return [0, 0]
            if end and end < self.laycan_dic[row[0]]['start_ts']:
                return [0, 0]
            if start and start > self.laycan_dic[row[-1]]['end_ts']:
                return [length, length]
            else:
                startIdx, endIdx = 0, length
                if start:
                    for idx in range(length - 1, -1, -1):
                        no = row[idx]
                        no_end = self.laycan_dic[no]['end_ts']
                        if no_end and start >= no_end:
                            startIdx = idx + 1
                            break
                if end:
                    for idx in range(1, length):
                        no = row[idx]
                        no_start = self.laycan_dic[no]['start_ts']
                        if no_start and end <= no_start:
                            endIdx = idx
                            break
                return startIdx, endIdx

    def pick_abandon(self, selec_n):
        return it.combinations(self.laycan_dic['noneed_ls'], selec_n)

