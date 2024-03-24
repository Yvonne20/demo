from typing import NamedTuple
import json, os

import pandas as pd

OIL_PRICE = 700
RUN_OIL = 40
IDLE_OIL = 10
PORTFEE_default = 20000


class FeeClass:
    def __init__(self, ship_id, ship_cfg_path, port_fee_cfg_path, port_fee_default=PORTFEE_default,
                 run_oil=RUN_OIL, idle_oil=IDLE_OIL, oil_price=OIL_PRICE):
        # self.ship_id = ship_id
        self.ship_name = f'ship_{ship_id}'
        self.ship_cfg_path = ship_cfg_path
        self.port_fee_cfg_path = port_fee_cfg_path
        self.OIL_RUN = run_oil * oil_price
        self.OIL_IDLE = idle_oil * oil_price
        self.PORTFEE_default = port_fee_default

        self.ship_cfg = self.get_ship_cfg(ship_cfg_path)

    def get_daily_fee(self):
        return self.ship_cfg[self.ship_name]['daily_cost']

    def get_port_fee(self, port):
        port_fee_table = pd.read_csv(self.port_fee_cfg_path, encoding='utf-8').iloc[2:-1, :]
        port_fee_table = port_fee_table.applymap(lambda cell: self.parse_cell(cell))
        port_fee_table.set_index('port_name', inplace=True)
        for col in range(4, 15):
            col_name = str(col)
            port_fee_table[col_name] = pd.to_numeric(port_fee_table[col_name])
        port_fee_table = port_fee_table.to_dict()
        port_fee_no = self.ship_cfg[self.ship_name]['port_fee_no']
        fee_dic = port_fee_table[str(port_fee_no)]
        if port not in fee_dic or not fee_dic[port]:
            return self.PORTFEE_default              # TODO: Temporarily Using Default Values
        return fee_dic[port]

    @staticmethod
    def parse_cell(cell):
        if type(cell) == str:
            return cell.replace(',', '')
        return cell

    @staticmethod
    def get_ship_cfg(ship_cfg_path):
        with open(ship_cfg_path) as f:
            return json.load(f)

class Days(NamedTuple):
    stay: float = 1.


file_path = os.path.dirname(os.path.abspath(__file__))

days = Days()
ship_cfg = FeeClass.get_ship_cfg(f'{file_path}/../config/ship_config.json')
fee = lambda ship_id: FeeClass(ship_id,
                               ship_cfg_path=f'{file_path}/../config/ship_config.json',
                               port_fee_cfg_path=f'{file_path}/../config/port_fee_table.csv')

