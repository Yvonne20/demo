from src import arrange_com, params

import pandas as pd
from datetime import datetime
from collections import defaultdict
import json

class OrderObj:
    def __init__(self, df, ship_id, cargo_dic, days_dic=None, max_route_days=None, n=50):
        self.cols = ['category', 'group', 'port', 'port_no', 'cargo', 'weight',
                     'demand', 'laycan_start', 'laycan_end', 'add_days']
        self.cols_with_no = ['no'] + self.cols
        self.ship_id = ship_id
        self.days_dic = days_dic
        self.cargo_dic = cargo_dic
        self.df = df
        self.new_df = None

        self.is_parse = False
        self.prior_set = None
        self.single_ls = None
        self.origin_ls = None
        self.input_struct = None
        self.income_dic = None
        self.need_ls = None
        self.group_dic = defaultdict(set)
        self.item_dic = dict()
        self.income_dic_for_routecheck = None
        self.group_dic_for_routecheck = defaultdict(set)
        self.item_dic_for_routecheck = dict()
        self.laycan_dic = None

        self.initTS = None
        self.initPort = None    # TODO
        self.N = n
        self.__max_route_days = max_route_days
        self.max_route_ts = self.get_max_route_ts()
        self.isPanama = None

        self.parse_order()

        self.order_dic = self.new_df.to_dict()
        self.group_ls = list(self.new_df.group.unique())
        self.max_income = self.compute_max_income()
        self.stay_dic = self.compute_stay_dic()
        self.cargo_items = self.get_cargo_item()

    def get_cargo_item(self):
        dic = {no: (self.order_dic['cargo'][no],
                    self.cargo_dic[self.order_dic['cargo'][no]]['group_name'],
                    self.order_dic['volume_s'][no])
               for no in self.order_dic['no']}
        return dic

    def compute_max_income(self):
        max_income = 0
        for group in self.group_ls:
            max_income += self.income_dic[group]['income']
        return max_income

    def compute_stay_dic(self):
        dic = {order_no: (params.days.stay + float(self.new_df.loc[order_no].add_days))
               for order_no in self.new_df.index}
        return dic

    def parse_order(self):

        self.income_dic = self.df[['income_group', 'income', 'need']].dropna(subset='income').set_index('income_group').transpose().to_dict()
        self.new_df = self.df.loc[:, self.cols].dropna(how='all')
        self.new_df.add_days.fillna(0, inplace=True)
        self.initPort = self.df.iloc[0]['initPos']
        self.initTS = datetime.strptime(self.df.iloc[0]['initDate'], '%Y/%m/%d').timestamp() + 28800

        self.isPanama = any(map(lambda x: x > 365,
                                {k: self.days_dic[self.initPort][k] for k in self.new_df.port.unique()}.values()))

        if 'no' not in self.new_df.columns:
            self.new_df.insert(0, 'no', range(len(self.new_df)))

        if self.isPanama:
            index = self.new_df.no.max() + 1
            group = self.new_df.group.max() + 1

            self.new_df.loc[index] = ({'no': index,
                                        'category': 'item',
                                        'group': group,
                                        'port': 'PANAMA',
                                        'cargo': '',
                                        'weight': 0,
                                        'demand': '',
                                        'laycan_start': None,
                                        'laycan_end': None,
                                        'add_days': float(self.df.iloc[0]['panama_days']) if self.df.iloc[0]['panama_days'] else 0,
                                        'start_ts': 0,
                                        'end_ts': 0,
                                        'weights': None,
                                        'density': None,
                                        'volume_s': None
                                     })
            self.income_dic[group] = {"income": 0, "need": 0, "panama": 1}
        self.new_df.add_days = self.new_df.add_days.apply(lambda row: row if row else 0)
        self.new_df['stay_days'] = pd.to_numeric(self.new_df.add_days) + params.days.stay
        self.income_dic = {int(k): self.income_dic[k] for k in filter(lambda x: x in self.new_df.group.to_list(),
                                                                      self.income_dic)}

        self.order2newdf()
        self.order2dic()

        if self.isPanama:
            GList = [ [], [], [] ]                  # g1, g2, panama
            for idx, row in self.new_df.iterrows():
                days = self.days_dic[self.initPort][row.port]
                if row.port == 'PANAMA':
                    GList[2].append(row.no)
                elif days < 365:
                    GList[0].append(row.no)
                else:
                    GList[1].append(row.no)
            if len(GList[2]) != 1:
                raise ValueError("BUG...")
            initG = self.new_df[self.new_df.no.isin(GList[0])]
            postG = self.new_df[self.new_df.no.isin(GList[1])]

            g1 = self.df2struct(initG)
            g2 = self.df2struct(postG)
            self.input_struct = [g1, GList[2][0], g2]     # [ g1, panama, g2 ]

        cols = self.cols_with_no + ['start_ts', 'end_ts']
        prior_df = self.new_df[self.new_df.category == 'priority'][cols]
        single_df = self.new_df[self.new_df.category == 'item'][cols]
        orig_df = self.new_df[self.new_df.category == 'original'][cols]

        self.prior_set = self.prior2set(prior_df)
        self.single_ls = single_df.no.to_list()
        self.origin_ls = self.orig2ls(orig_df)
        if not self.isPanama:
            struc = self.df2struct(self.new_df)
            self.input_struct = [struc, None, None]
        self.need_ls = list(filter(lambda x: self.income_dic[x]['need'] == 1, self.income_dic))  # Without OrigItem

        self.income_dic_for_routecheck = self.get_income_dic_for_routecheck()
        self.laycan_dic = self.newdf2laycan_dic()

        self.is_parse = True
        return

    def newdf2laycan_dic(self):
        dic = {int(no): {"start_ts": self.new_df[self.new_df.no==no].iloc[0].start_ts,
                         "end_ts": self.new_df[self.new_df.no==no].iloc[0].end_ts
                         } for no in self.new_df.no}
        dic["group_dic"] = self.group_dic
        dic["noneed_ls"] = [{i: self.group_dic[i]} for i in self.group_dic
                            if i not in self.need_ls and self.new_df[self.new_df.group==i].iloc[0].port != 'PANAMA']
        return dic

    def df2struct(self, df):
        cols = self.cols_with_no + ['start_ts', 'end_ts']
        prior_df = df[df.category == 'priority'][cols]
        single_df = df[df.category == 'item'][cols]
        orig_df = df[df.category == 'original'][cols]

        prior_set = self.prior2set(prior_df)
        single_ls = single_df.no.to_list()
        origin_ls = self.orig2ls(orig_df)

        prior_set_new = dict()
        for k in prior_set:
            item = prior_set[k]
            if len(item[0]) > 0 and len(item[1]) > 0:
                prior_set_new[k] = item
            else:
                for no in item[0] + item[1]:
                    single_ls.append(no)

        return {
            "original": origin_ls,
            "prior": prior_set_new,
            "single": single_ls
        }

    def prior2set(self, prior_df):
        if len(prior_df) == 0:
            return []
        prior_set = dict()
        for group in prior_df.group.unique():
            df = prior_df[prior_df.group == group]
            load_ls, discharg_ls = [], []
            for idx, row in df.iterrows():
                if row.demand.lower() == 'loading':
                    load_ls.append(row['no'])
                elif row.demand.lower() == 'discharging':
                    discharg_ls.append(row['no'])
                else:
                    raise ValueError("df Format is Wrong!!")
            prior_set[group] = ([load_ls, discharg_ls])
        return prior_set

    def orig2ls(self, orig_df):
        orig_df['start_ts'] = orig_df.laycan_start.apply(lambda v: self.date2TS(v, 0))
        orig_df['end_ts'] = orig_df.laycan_end.apply(lambda v: self.date2TS(v, 1))
        df = orig_df.sort_values(by='start_ts')
        return df.no.to_list()

    def map_startTS_by_dayDic(self, row):
        days = self.days_dic[self.initPort][row.port]
        if days < 365:
            return max(row.start_ts, self.initTS + days * 86400)
        return row.start_ts

    def order2newdf(self):

        self.new_df["start_ts"] = self.new_df.laycan_start.apply(lambda v: self.date2TS(v, 0))
        self.new_df["start_ts"] = self.new_df.apply(lambda row: self.map_startTS_by_dayDic(row), axis=1)
        self.new_df["end_ts"] = self.new_df.laycan_end.apply(lambda v: self.date2TS(v, 1))
        self.new_df["weights"] = self.new_df.apply(lambda row: self.signWeight(row), axis=1)
        self.new_df["cargo"] = self.new_df.cargo.apply(lambda row: row.lower())
        self.new_df["density"] = self.new_df.apply(lambda row: self.cargo_dic[row.cargo]['density'], axis=1)
        self.new_df["volume_s"] = self.new_df.weights / self.new_df.density
        self.new_df["port_no"] = self.new_df.port_no.fillna(0)
        self.new_df.port_no = self.new_df.port_no.astype(int)
        self.new_df.index = self.new_df.no

    def order2dic(self):
        for idx, row in self.new_df.iterrows():
            self.item_dic[row.no] = row.group
            self.group_dic[row.group].add(row.no)
            if row.group > 0:
                self.item_dic_for_routecheck[row.no] = row.group
                self.group_dic_for_routecheck[row.group].add(row.no)
            elif row.group < 0:
                self.item_dic_for_routecheck[row.no] = -1
                self.group_dic_for_routecheck[-1].add(row.no)
            else:
                raise ValueError("Bug...")

    def get_income_dic_for_routecheck(self):
        dic = {k: self.income_dic[k] for k in self.income_dic if k > 0}
        dic[-1] = {"income": 0, "need": 1}
        for k in self.income_dic:
            if k < 0:
                dic[-1]['income'] += self.income_dic[k]['income']
        return dic

    def show_df(self):
        if self.is_parse:
            print("_________ order : _________")
            print("- DF: ", self.new_df)
            print("- PRIOR_SET: ", self.prior_set)
            print("- ITEM_LS: ", self.single_ls)
            print("- ORIG_LS: ", self.origin_ls)
            print("- ORDER_DIC: ", self.order_dic)
            print("- INCOME_DIC: ", self.income_dic)
            print("- DAYS_DIC: ", self.days_dic)
            print("- INIT_TS: ", self.initTS, datetime.fromtimestamp(self.initTS))
            print("- INIT_POS: ", self.initPort)
            print("___________ order end ____________")
        else:
            print("OrderDic Has NOT Transform Dataframe...... Something Wrong !!")

    def date2TS(self, date, end):
        if type(date) == str:
            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                dt = datetime.strptime(date, "%Y/%m/%d")
            if end == 1:
                return int(dt.timestamp() + 86399)
            elif end == 0:
                return int(dt.timestamp())
            else:
                raise ValueError("end should be 0 or 1")
        else:
            return 0

    def signWeight(self, row):
        if row.demand.lower() == "loading":
            return row.weight
        elif row.demand.lower() == "discharging":
            return -1 * row.weight
        elif row.demand == '':
            return 0
        else:
            raise ValueError("string out of Range !")

    def get_max_route_ts(self):
        if self.__max_route_days:
            return self.initTS + float(self.__max_route_days) * 86400
        else:
            return 0

    def set_max_route_days(self, days):
        self.__max_route_days = days
        self.max_route_ts = self.get_max_route_ts()


class TableObj:
    def __init__(self, ship_id, ship_cfg_path, miles_path, days_path, exclude_path, cargo_cfg_path,
                 port_cfg_path, order_df):
        self.ship_id = ship_id
        self.ship_cfg_path = ship_cfg_path
        self.miles_path = miles_path
        self.days_path = days_path
        self.exclude_path = exclude_path
        self.cargo_cfg_path = cargo_cfg_path
        self.port_cfg_path = port_cfg_path
        self.order_df = order_df

        self.port_ls, self.cargo_ls = self.get_port_and_cargo_ls()

        self.ship_cfg = self.get_ship_cfg()
        self.mile_dic = self.get_mile_dic()
        self.days_dic = self.get_days_dic()
        self.cargo_dic = self.get_cargo_dic()
        self.exclude_dic = self.get_exclude_dic()
        self.draft_limit_dic = self.get_draft_limit_dic()
        self.arrange_com_obj = self.get_arrange_com_obj()

        self.fee_dic = self.get_fee_dic()

    def get_ship_cfg(self):
        with open(self.ship_cfg_path) as f:
            ship_cfg = json.load(f)[f'ship_{self.ship_id}']
        for col in ['com_limit', 'com_dic', 'com_near', 'load_factor']:
            ship_cfg[col] = {int(k): ship_cfg[col][k] for k in ship_cfg[col]}
        return ship_cfg

    def get_mile_dic(self):
        dic = pd.read_csv(self.miles_path, index_col=0).to_dict()

        return {port: dic[port] for port in self.port_ls}

    def get_days_dic(self):
        dic = pd.read_csv(self.days_path, index_col=0).to_dict()

        return {port: dic[port] for port in self.port_ls}

    def get_fee_dic(self):
        fee = params.fee(self.ship_id)
        port_fee_dic = {port: fee.get_port_fee(port) for port in self.port_ls}  # TODO: port_ls may be changed
        if self.order_df.is_panama.iloc[0] and not pd.isna(self.order_df.panama_fee.iloc[0]):
            port_fee_dic['PANAMA'] = float(self.order_df.panama_fee.iloc[0])
        return Fee(fee.OIL_RUN, fee.OIL_IDLE, fee.get_daily_fee(), port_fee_dic)

    def get_cargo_dic(self):
        with open(self.cargo_cfg_path) as f:
            cargo_dic = json.load(f)

        return {cargo: {'group_name': cargo_dic[cargo]['group_name'], 'density': cargo_dic[cargo]['density']}
                for cargo in self.cargo_ls}

    def get_exclude_dic(self):
        tot_df = self.get_exclude_df(self.exclude_path)
        group_set = set()
        for cargo in self.cargo_ls:
            group_set.add(self.cargo_dic[cargo]['group_name'])
        col = [e for e in group_set if e]
        df = tot_df.loc[col, col]
        return df.to_dict()

    @staticmethod
    def get_exclude_df(exclude_path):
        df = pd.read_csv(exclude_path, index_col=0)
        df.columns = [col.lower() for col in df.columns]
        df.index = [index.lower() for index in df.index]
        df.rename(columns={"organic anhydrins": "organic anhydrides",
                           "substitutes allyls": "substitute allyls"}, inplace=True)
        df.rename(index={"phenols, creosols": "phenols, cresols"}, inplace=True)

        cargo_group = ['olefins', 'paraffins', 'aromatic hydrocarb.mix.', 'misc. hydrocarb. mix.',
                       'esters', 'vinyl halides', 'halogenated hydrocarbons', 'nitriles', 'carbon disulfide',
                       'sulpalane', 'glycol ethers', 'ethers', 'nitrocompounds', 'misc. water solutions']
        reactive_group = ['non-oxidizing mineral acids', 'sulphuric acid', 'nitric acid',
                          'organic acids', 'caustics', 'ammonia', 'aliphatic amines',
                          'alkanolamines', 'aromatic amines', 'amides', 'organic anhydrides',
                          'isocyanates', 'vinyl acetate', 'acrylates', 'substitute allyls',
                          'alkylene oxides', 'epichlorohydrin', 'ketones', 'aldehydes',
                          'alcohols, glycols', 'phenols, cresols', 'caprolactam solution']

        # Fill Columns
        for col in cargo_group:
            df[col] = None
        for col in reactive_group:
            for col2 in cargo_group:
                df.loc[col, col2] = df.loc[col2, col]

        df.fillna(0, inplace=True)
        df.replace({'X': -1}, inplace=True)

        return df

    def get_port_and_cargo_ls(self):
        items_df = self.order_df.loc[:, ['group', 'port', 'cargo']].dropna(how='all')
        current_com_df = self.order_df.loc[:, ['com', 'cargo_name', 'pre3']]
        com_cargo_set = set()
        for cargo in current_com_df.cargo_name.dropna().unique():
            com_cargo_set.add(cargo)
        for s in current_com_df.pre3:
            if type(s) == str:
                pre3 = s.split(',')
                for cargo in pre3:
                    com_cargo_set.add(cargo)

        port_ls = list(items_df.port.apply(lambda row: row.upper()).unique())
        port_ls.append(self.order_df.iloc[0]['initPos'])
        cargo_ls = list(items_df.cargo.apply(lambda row: row.lower()).unique()) + list(com_cargo_set)

        if self.order_df.is_panama.iloc[0]:
            port_ls.append('PANAMA')
            cargo_ls.append('')

        return port_ls, cargo_ls

    def get_draft_limit_dic(self):
        with open(self.port_cfg_path) as f:
            port_dic = json.load(f)
        return {port: self.parse_draft(port_dic[port]['0']['draft']) for port in self.port_ls}

    @staticmethod
    def parse_draft(draft):
        if draft == -1:
            return None
        return draft

    def get_arrange_com_obj(self):
        current_com = self.parse_current_com()
        return arrange_com.ArrangeCom(current_com, self.ship_cfg, self.exclude_dic)

    def parse_current_com(self):
        df = self.order_df.loc[:, ['com', 'cargo_name', 'vol', 'pre3']].dropna(how='all')
        df.cargo_name = df.cargo_name.fillna('')
        df.vol = df.vol.fillna(0)
        df.pre3 = df.pre3.fillna('')
        df.vol = pd.to_numeric(df.vol)
        dic = df.transpose().to_dict()

        for com in dic:
            pre3 = dic[com]['pre3'].split(',')
            pre3 = [self.cargo_dic[cargo_name]['group_name']
                    for cargo_name in pre3 if cargo_name]
            if len(pre3) < 3:
                d = 3 - len(pre3)
                for i in range(d):
                    pre3.insert(0, None)
            dic[com]['pre3'] = pre3
            cargo_name = dic[com]['cargo_name']
            if cargo_name and not pd.isna(cargo_name):
                dic[com]['group_name'] = self.cargo_dic[cargo_name]['group_name']
            else:
                dic[com]['cargo_name'] = ''
                dic[com]['group_name'] = ''

        return dic


class Fee:
    def __init__(self, oil_run, oil_idle, daily_fee, port_fee_dic):
        self.OIL_RUN = oil_run
        self.OIL_IDLE = oil_idle
        self.DAILY_FEE = daily_fee
        self.PORT_FEE = port_fee_dic

