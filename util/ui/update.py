import dash
from dash.dependencies import Input, Output, State
import time, sys, json
import pandas as pd
from collections import defaultdict

sys.path.append('./../../')
sys.path.append('./../../src')
sys.path.append('./../../config')
from view import *
from src import Navigate, Ship, params
from src.opt import opt_interface
from util import order
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 500)

app = dash.Dash(__name__)
app.layout = html.Div(VIEW)
server = app.server

@app.callback(
    [Output('container_prior', 'children'),
     Output('Store_prior', 'data'),
     Output('prior_delete_num', 'value'),
     Output('prior_group_0', 'value'),
     Output('prior_port_0', 'value'),
     Output('prior_port_no_0', 'value'),
     Output('prior_cargo_0', 'value'),
     Output('prior_weight_0', 'value'),
     Output('prior_demand_0', 'value'),
     Output('prior_start_0', 'date'),
     Output('prior_end_0', 'date'),
     Output('prior_add_days_0', 'value'),
     Output('prior_unit_income_0', 'value')],
    [Input('prior_set', 'n_clicks'),
     Input('delete_prior', 'n_clicks')],
    [State('Store_prior', 'data'),
     State('prior_delete_num', 'value'),
     State('prior_group_0', 'value'),
     State('prior_port_0', 'value'),
     State('prior_port_no_0', 'value'),
     State('prior_cargo_0', 'value'),
     State('prior_weight_0', 'value'),
     State('prior_demand_0', 'value'),
     State('prior_start_0', 'date'),
     State('prior_end_0', 'date'),
     State('prior_add_days_0', 'value'),
     State('prior_unit_income_0', 'value'),
     State('container_prior', 'children'),
     State('prior_abandon', 'value')]
)
def prior_to_Store(n_clicks1, n_clicks2, data, delete_num, group, port, port_no, cargo, weight,
                   demand, start, end, add_days, unit_income, children, abandon):
    print("PRIOR STORE..................................................")
    print(f"click1={n_clicks1}, click2={n_clicks2}, delete_num={delete_num}")
    children_out = []

    if data:
        data_json = json.loads(data)
    else:
        data_json = {}

    income = float(unit_income) * float(weight) if unit_income else None
    is_abandon = True if 'abandon' in abandon else False
    new_data = {"group": group, "port": port, "port_no": port_no, "cargo": cargo, "weight": weight, "demand": demand,
                "start": start, "end": end, "add_days": add_days, "income": income, "abandon": is_abandon}
    table_out = []

    if n_clicks1 and not delete_num:
        if group and port and cargo and weight and demand:
            data_json[n_clicks1] = new_data
            data = json.dumps(data_json)

            for k in data_json:
                table_out.append({'No.':k, 'group':data_json[k]['group'], 'port':data_json[k]['port'], 'port_no':data_json[k]['port_no'],
                                  'cargo':data_json[k]['cargo'],
                                  'weight':data_json[k]['weight'], 'demand':data_json[k]['demand'],
                                  'start':data_json[k]['start'], 'end':data_json[k]['end'], 'add_days': data_json[k]['add_days'], 'income':data_json[k]['income'],
                                  'can abandon': data_json[k]['abandon']})
            children_out = show_table(table_out)
        else:
            print("Prior Input Not Full....")
            return children, data, delete_num, group, port, cargo, weight, demand, start, end, income

    if n_clicks2 and delete_num:
        if data and str(delete_num) in data_json:
            del data_json[str(delete_num)]
            data = json.dumps(data_json)

            for k in data_json:
                table_out.append({'No.': k, 'group': data_json[k]['group'], 'port': data_json[k]['port'],
                                  'cargo': data_json[k]['cargo'],
                                  'weight': data_json[k]['weight'], 'demand': data_json[k]['demand'],
                                  'start': data_json[k]['start'], 'end': data_json[k]['end'], 'add_days': data_json[k]['add_days'], 'income':data_json[k]['income'],
                                  'can abandon': data_json[k]['abandon']})
            children_out = show_table(table_out)
        else:
            print("Key not in the JSON ", delete_num)
            return children, data, None, None, None, None, None, None, None, None, None, None, None

    return children_out, data, None, None, None, None, None, None, None, None, None, None, None

@app.callback(
    [Output('container_item', 'children'),
     Output('Store_item', 'data'),
     Output('item_delete_num', 'value'),
     Output('item_port_0', 'value'),
     Output('item_port_no_0', 'value'),
     Output('item_cargo_0', 'value'),
     Output('item_weight_0', 'value'),
     Output('item_demand_0', 'value'),
     Output('item_start_0', 'date'),
     Output('item_end_0', 'date'),
     Output('item_add_days_0', 'value'),
     Output('item_unit_income_0', 'value')],
    [Input('item_set', 'n_clicks'),
     Input('delete_item', 'n_clicks')],
    [State('Store_item', 'data'),
     State('item_delete_num', 'value'),
     State('item_port_0', 'value'),
     State('item_port_no_0', 'value'),
     State('item_cargo_0', 'value'),
     State('item_weight_0', 'value'),
     State('item_demand_0', 'value'),
     State('item_start_0', 'date'),
     State('item_end_0', 'date'),
     State('item_add_days_0', 'value'),
     State('item_unit_income_0', 'value'),
     State('container_item', 'children'),
     State('item_abandon', 'value')]
)
def item_to_Store(n_clicks1, n_clicks2, data, delete_num, port, port_no, cargo, weight,
                  demand, start, end, add_days, unit_income, children, abandon):
    print("ITEM STORE..................................................")
    print(f"click1={n_clicks1}, click2={n_clicks2}, delete_num={delete_num}")
    children_out = []

    if data:
        data_json = json.loads(data)
    else:
        data_json = {}

    income = float(unit_income) * float(weight) if unit_income else None
    is_abandon = True if 'abandon' in abandon else False
    new_data = {"port": port, "port_no": port_no, "cargo": cargo, "weight": weight, "demand": demand,
                "start": start, "end": end, "add_days": add_days, "income": income, "abandon": is_abandon}
    table_out = []

    if n_clicks1 and not delete_num:
        if port and cargo and weight and demand and unit_income:

            data_json[n_clicks1] = new_data
            data = json.dumps(data_json)

            for k in data_json:
                table_out.append({'No.': k, 'port': data_json[k]['port'], 'port_no': data_json[k]['port_no'],
                                  'cargo': data_json[k]['cargo'],
                                  'weight': data_json[k]['weight'], 'demand': data_json[k]['demand'],
                                  'start': data_json[k]['start'], 'end': data_json[k]['end'], 'add_days': data_json[k]['add_days'],
                                  'income': data_json[k]['income'],
                                  'can abandon': data_json[k]['abandon']})
            children_out = show_table(table_out)
        else:
            return children, data, delete_num, port, port_no, cargo, weight, demand, start, end, add_days, unit_income

    if n_clicks2 and delete_num:
        for k in data_json:
            print(k, type(k))
        if data and str(delete_num) in data_json:
            del data_json[str(delete_num)]
            data = json.dumps(data_json)

            for k in data_json:
                table_out.append({'No.': k, 'port': data_json[k]['port'], 'port_no': data_json[k]['port_no'],
                                  'cargo': data_json[k]['cargo'],
                                  'weight': data_json[k]['weight'], 'demand': data_json[k]['demand'],
                                  'start': data_json[k]['start'], 'end': data_json[k]['end'], 'add_days': data_json[k]['add_days'],
                                  'income': data_json[k]['income'],
                                  'can abandon': data_json[k]['abandon']})
            children_out = show_table(table_out)
        else:
            print("Key not in the JSON ", delete_num)
            return children, data, None, None, None, None, None, None, None, None, None, None

    return children_out, data, None, None, None, None, None, None, None, None, None, None

@app.callback(
    [Output('container_orig', 'children'),
     Output('Store_orig', 'data'),
     Output('orig_delete_num', 'value'),
     Output('orig_port_0', 'value'),
     Output('orig_port_no_0', 'value'),
     Output('orig_cargo_0', 'value'),
     Output('orig_weight_0', 'value'),
     Output('orig_demand_0', 'value'),
     Output('orig_date_0', 'date'),
     Output('orig_add_days_0', 'value'),
     Output('orig_unit_income_0', 'value')],
    [Input('orig_set', 'n_clicks'),
     Input('delete_orig', 'n_clicks')],
    [State('Store_orig', 'data'),
     State('orig_delete_num', 'value'),
     State('orig_port_0', 'value'),
     State('orig_port_no_0', 'value'),
     State('orig_cargo_0', 'value'),
     State('orig_weight_0', 'value'),
     State('orig_demand_0', 'value'),
     State('orig_date_0', 'date'),
     State('orig_add_days_0', 'value'),
     State('orig_unit_income_0', 'value'),
     State('container_orig', 'children')]
)
def orig_to_Store(n_clicks1, n_clicks2, data, delete_num, port, port_no, cargo, weight, demand, date, add_days, unit_income, children):
    print("ORIGIN STORE..................................................")
    print(f"click1={n_clicks1}, click2={n_clicks2}, delete_num={delete_num}")
    children_out = []

    if data:
        data_json = json.loads(data)
    else:
        data_json = {}

    income = float(unit_income) * float(weight) if unit_income else None
    new_data = {"port": port, "port_no": port_no, "cargo": cargo, "weight": weight, "demand": demand,
                "date":date, "add_days": add_days, "income":income}
    table_out = []

    if n_clicks1 and not delete_num:
        if port and cargo and weight and demand and date and unit_income:

            data_json[n_clicks1] = new_data
            data = json.dumps(data_json)

            for k in data_json:
                table_out.append({'No.': k, 'port': data_json[k]['port'], 'port_no': data_json[k]['port_no'],
                                  'cargo': data_json[k]['cargo'],
                                  'weight': data_json[k]['weight'], 'demand': data_json[k]['demand'],
                                  'start': data_json[k]['date'], 'end': data_json[k]['date'], 'add_days': data_json[k]['add_days'],
                                  'income': data_json[k]['income']})
            children_out = show_table(table_out)
        else:
            return children, data, delete_num, port, port_no, cargo, weight, demand, date, add_days, unit_income

    if n_clicks2 and delete_num:
        for k in data_json:
            print(k, type(k))
        if data and str(delete_num) in data_json:
            del data_json[str(delete_num)]
            data = json.dumps(data_json)

            for k in data_json:
                children_out.append(html.Div(f"{k}: {json.dumps(data_json[k])}"))
                table_out.append({'No.': k, 'port': data_json[k]['port'], 'port_no': data_json[k]['port_no'],
                                  'cargo': data_json[k]['cargo'],
                                  'weight': data_json[k]['weight'], 'demand': data_json[k]['demand'],
                                  'start': data_json[k]['date'], 'add_days': data_json[k]['add_days'], 'end': data_json[k]['date'],
                                  'income': data_json[k]['income']})
            children_out = show_table(table_out)
        else:
            print("Key not in the JSON ", delete_num)
            return children, data, None, None, None, None, None, None, None, None, None

    return children_out, data, None, None, None, None, None, None, None, None, None

@app.callback(
    Output('Store_com', 'data'),
    [Input('com_save', 'n_clicks')],
    [State(f'com_unit', 'value')] +
    [State(f'cargo_name_{com_int}', 'value') for com_int in range(16)] +
    [State(f'cargo_amount_{com_int}', 'value') for com_int in range(16)] +
    [State(f'cargo_pre3_{com_int}', 'value') for com_int in range(16)]
)
def com_save(n_clicks, cargo_unit, *args):  # TODO: 16 Should Be Dynamic
    print("COM SAVE ..........................", n_clicks, cargo_unit)
    dic = {com_int: dict() for com_int in range(16)}
    for i, data_name in enumerate(['cargo_name', 'cargo_amount', 'cargo_pre3']):
        for com_int in range(16):
            dic[com_int][f'{data_name}'] = args[i*16+com_int]
    return dic

@app.callback(
    [Output('Store_limit', 'data'),
     Output('ship_message', 'children')],
    [Input('ship_id', 'value'),
     Input('ship_limit_weight', 'value'),
     Input('max_route_days', 'value'),
     Input('opt_method', 'value'),
     Input('is_panama', 'value'),
     Input('panama_fee', 'value'),
     Input('panama_days', 'value')]
)
def limit_save(ship_id, ship_limit_load_weight, max_route_days, opt_method, is_panama, panama_fee, panama_days):
    print("Limit Information Save ...")
    if ship_limit_load_weight:
        load_weight = ship_limit_load_weight
    else:
        load_weight = params.ship_cfg[f'ship_{ship_id}']['ship_weight_limit']
    return {
        'ship_id': ship_id,
        'limit_load_weight': load_weight,
        'max_route_days': max_route_days,
        'opt_method': opt_method,
        'is_panama': is_panama,
        'panama_fee': panama_fee,
        'panama_days': panama_days
    }, f"     - SHIP_{ship_id}'s Max Loading Weight is '{load_weight}' MT"

@app.callback(
    Output('container_markdown', 'children'),
    [Input('Optimize', 'n_clicks')],
    [State('container_prior', 'children'),  # TODO: change to Store_prior
     State('container_item', 'children'),
     State('container_orig', 'children'),
     State('initPort', 'value'),
     State('initDate', 'date'),
     State('com_valid', 'value'),
     State('Store_com', 'data'),
     State('Store_limit', 'data')]
)
def optimize(n_clicks, child_prior, child_item, child_orig, initPort, initDate, com_valid_ls, com_data, limit_data):
    df_columns = ['category', 'group', 'port', 'port_no', 'cargo', 'weight', 'demand', 'laycan_start', 'laycan_end', 'add_days']
    df = []
    income_dic = dict()
    need_dic = defaultdict(lambda: 0)
    if n_clicks and initPort and initDate:
        prior = parse_table(child_prior)
        item = parse_table(child_item)
        orig = parse_table(child_orig)
        idx_maxgroup = 0
        for k in prior:
            df.append(['priority', prior[k]['group'], prior[k]['port'], prior[k]['port_no'], prior[k]['cargo'],
                       prior[k]['weight'], prior[k]['demand'],
                       prior[k]['start'], prior[k]['end'], prior[k]['add_days']])
            try:
                group = prior[k]['group']
                if group not in income_dic:
                    income_dic[group] = 0
                if int(prior[k]['income']) > income_dic[group]:
                    income_dic[group] = int(prior[k]['income'])
                    need_dic[group] = 1 if not prior[k]['can abandon'] else 0
            except:
                pass
            if prior[k]['group'] > idx_maxgroup:
                idx_maxgroup = prior[k]['group']
        index = idx_maxgroup + 1
        for k in item:
            df.append(['item', index, item[k]['port'], item[k]['port_no'], item[k]['cargo'], item[k]['weight'], item[k]['demand'],
                       item[k]['start'], item[k]['end'], item[k]['add_days']])
            income_dic[index] = item[k]['income']
            need_dic[index] = 1 if not item[k]['can abandon'] else 0
            index += 1
        index = -1
        for k in orig:
            df.append(['original', index, orig[k]['port'], orig[k]['port_no'], orig[k]['cargo'], orig[k]['weight'], orig[k]['demand'],
                       orig[k]['start'], orig[k]['end'], orig[k]['add_days']])
            income_dic[index] = orig[k]['income']
            index -= 1

        if len(df) < 16:
            for i in range(16 - len(df)):
                df.append([None for i in range(len(df[0]))])
        df_len = max(16, len(income_dic), len(df))
        print("dfLEN=", df_len, len(df))

        df = pd.DataFrame(df, columns=df_columns)
        df['income_group'] = list(income_dic.keys()) + [None for i in range(df_len - len(income_dic))]
        df['income'] = list(income_dic.values()) + [None for i in range(df_len - len(income_dic))]
        df['need'] = [need_dic[i] for i in income_dic] + [None for i in range(df_len - len(income_dic))]
        df['income'] = pd.to_numeric(df.income)
        df['weight'] = pd.to_numeric(df.weight)

        df['initPos'] = [initPort] + [None for i in range(df_len - 1)]
        df['initDate'] = [pd.to_datetime(initDate).strftime('%Y/%m/%d')] + [None for i in range(df_len - 1)]
        df['is_panama'] = [1 if limit_data['is_panama'] else 0] + [None for i in range(df_len - 1)]
        df['panama_days'] = [limit_data['panama_days']] + [None for i in range(df_len - 1)]
        df['panama_fee'] = [limit_data['panama_fee']] + [None for i in range(df_len - 1)]

        ship_cfg = params.ship_cfg
        ship_id = limit_data['ship_id']  # TODO: Only Compatible for ship of (com_nums=16) Now (due to com_data input)
        SHIP = Ship.ShipDynamic(ship_id, ship_cfg=ship_cfg)
        SHIP.set_limit_load_weight(int(limit_data['limit_load_weight']))
        print("limitWeight = ", SHIP.weightLimit)
        com_valid = True if 'com_valid' in com_valid_ls else False
        # com_valid = com_valid and check_com_not_empty(com_data)

        com_cargo_name = []
        com_volume = []
        com_pre3 = []
        for com in SHIP.get_ship_com:
            cargo_name = com_data[str(com)]['cargo_name']
            if not cargo_name:
                cargo_name = ''
            com_cargo_name.append(cargo_name)
            if cargo_name:
                com_volume.append(com_data[str(com)]['cargo_amount'])
            else:
                com_volume.append(0)
            pre3 = com_data[str(com)]['cargo_pre3']
            if not pre3:
                com_pre3.append('')
            else:
                com_pre3.append(','.join(pre3))

        resid_row = df_len - len(SHIP.get_ship_com)
        resid_row = resid_row if resid_row > 0 else 0
        df['com'] = list(SHIP.get_ship_com.keys()) + [None for i in range(resid_row)]
        df['cargo_name'] = com_cargo_name + ['' for i in range(resid_row)]
        df['vol'] = com_volume + [0 for i in range(resid_row)]
        df['pre3'] = com_pre3 + ['' for i in range(resid_row)]

        exclude_path = "../../config/17_COMPATIBILITY_CHART.csv"
        mile_path = "../../config/port_distance2.csv"
        days_path = "../../config/port_days2.csv"
        cargo_cfg_path = "../../config/cargo_config.json"
        port_cfg_path = "../../config/port_config.json"

        table_obj = order.TableObj(limit_data['ship_id'], mile_path, days_path, exclude_path, cargo_cfg_path,
                                   port_cfg_path, df)
        order_obj = order.OrderObj(df,
                                   limit_data['ship_id'],
                                   table_obj.cargo_dic,
                                   limit_data['max_route_days'],
                                   n=10)
        order_obj.show_df()

        start = time.time()
        print("com valid = ", com_valid, check_com_not_empty(com_data))
        print("current_com = ", table_obj.current_com_dic)

        profitLs = Navigate.gen_route(order_obj,
                                      table_obj,
                                      SHIP,
                                      table_obj.current_com_dic,
                                      is_arrange=com_valid,
                                      opt_method=opt_interface.OptMethod[limit_data['opt_method']])
        duration = time.time() - start
        print("TIME ELAPSED : ", duration)
        if len(profitLs):
            return optLs2div(profitLs, order_obj.new_df, duration)
        return "NO RESULTS"

    elif n_clicks:
        return "PLEASE INPUT INITIAL PORT ! "
    return dcc.Markdown("\n\n\n\nInformation Shows Here ...")


def check_com_not_empty(com_data):
    for com in com_data:
        for item in com_data[com]:
            if com_data[com][item]:
                return True
    return False

def optLs2div(opt_ls, order_df, duration):
    tables = optLs2table(opt_ls, order_df)

    output = html.Div([f"Time Elapsed : {duration: .1f} sec"] + [
                html.Div([
                    html.P(f'\n\n### {index+1} ###    < {datetime.now()} >'),
                    dash_table.DataTable(data=table, style_table={'width': '70%'}),
                    dcc.Markdown(f"* DISTANCE = {opt_ls[index][3]}\n\n* DAYS = {opt_ls[index][4] / 86400: .2f} days\n\n"
                                 f"* COST = {opt_ls[index][5]:.0f}\n\n* PROFIT = {opt_ls[index][6]:.0f}"),
                ]) for index, table in enumerate(tables)
            ])
    return output

def optLs2table(opt_ls, order_df):
    tables = []
    for index in range(len(opt_ls)):
        bestOrder = opt_ls[index]
        table = []
        for i in range(bestOrder[7]):
            portNo = bestOrder[0][i]
            port_no = order_df.loc[portNo].port_no
            port = order_df.loc[portNo].port
            date_ = datetime.fromtimestamp(bestOrder[1][i])
            if order_df.loc[portNo].end_ts != 0:
                start = date.fromtimestamp(order_df.loc[portNo].start_ts)
                end = date.fromtimestamp(order_df.loc[portNo].end_ts-1)
            else:
                start, end = None, None
            wait = bestOrder[2][i] / 86400
            stay = float(order_df.loc[portNo].add_days) + params.days.stay

            table.append({'No.': i+1,
                           'PORT': port,
                           'PORT#': port_no,
                           'DATETIME': date_,
                           'CARGO': order_df.loc[portNo].cargo,
                           'DEMAND': order_df.loc[portNo].demand,
                           'START': start,
                           'END': end,
                           'WAIT': round(wait, 2),
                           'STAY': stay})
        tables.append(table)
    return tables


def parse_child(child, start_index=0):
    data_dic = dict()

    for i in range(len(child)):
        data_str = child[i]['props']['children']
        if len(data_str) > 0:
            for s_i in range(len(data_str)):
                if data_str[s_i] == '{':
                    break
        data_out = json.loads(data_str[s_i:])
        data_dic[start_index+i] = data_out
    return data_dic

def parse_table(child_table, start_index=0):
    data_dic = dict()
    if child_table:
        table = child_table['props']['data']

        for i in range(len(table)):
            data = table[i]
            data_dic[start_index+i] = data
    return data_dic

def parse_order_dic(order_dic):
    dic = defaultdict(dict)

    index = 0
    for cat, cat_title in zip(['prior', 'item', 'orig'], ['priority', 'item', 'original']):
        for k in order_dic[cat]:
            dic[cat_title][index] = (order_dic[cat][k])
            index += 1


if __name__ == '__main__':
    app.run_server()
