from dash import dcc
from dash import html
from dash import dash_table

import sys
sys.path.append('./../../src')
sys.path.append('./../')


cargo_ls = ['px', 'benzene', 'cumene', 'toluene', 'lab', 'bab', 'nitric']
port_ls = ['MAILIAO', 'KAOHSIUNG', 'ULSAN', 'HOUSTON', 'PHILADELPHIA', 'BATON ROUGE', 'KALAMA', 'PUERTO QUETZAL']
demand_ls = ["Loading", "discharging"]
com_ls = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]
ship_ls = [31, 32, 33, 34, 35, 36]
opt_method_ls = [{'label': label, 'value': value} for label, value in zip(['最大收益', '最少天數'], ['MAX_PROFIT', 'MIN_DAYS'])]

def inline_style(width, float_, **kwargs):
    dic_ = {"display": "inline-block", "width": width, "float": float_}
    for k in kwargs:
        dic_[k] = kwargs[k]
    return dic_

prior_row = lambda id: [
    html.Div([dcc.Dropdown(id=f"prior_group_{id}", placeholder='*組號', options=[i for i in range(1, 11)], style=inline_style(100, 'left'))]),
    html.Div([dcc.Dropdown(id=f"prior_port_{id}", placeholder='*PORT', options=port_ls, style=inline_style(150, 'left'))]),
    html.Div([dcc.Dropdown(id=f"prior_port_no_{id}", placeholder='port_no', options=[i for i in range(10)], style=inline_style(80, 'left'))]),
    html.Div([dcc.Dropdown(id=f"prior_cargo_{id}", placeholder='*CARGO', options=cargo_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.Input(id=f"prior_weight_{id}", placeholder="*weight(MT)", type="int", style=inline_style(80, 'left', height='30px'))]),
    html.Div([dcc.Dropdown(id=f"prior_demand_{id}", placeholder='*動作', options=demand_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.DatePickerSingle(id=f"prior_start_{id}", placeholder='裝期開始', style=inline_style(None, 'left'))]),
    html.Div([dcc.DatePickerSingle(id=f"prior_end_{id}", placeholder='裝期結束', style=inline_style(None, 'left'))]),
    html.Div([dcc.Input(id=f'prior_unit_income_{id}', placeholder='單位收入($/MT)', style=inline_style(100, 'left', height='30px'))]),
    html.Div([dcc.Input(id=f'prior_add_days_{id}', placeholder='add days', type='int', style=inline_style(100, 'left', height='30px'))]),
    html.Div([html.Button("ADD", id='prior_set', n_clicks=0, style=inline_style(100, 'left', height=40))]),
    html.Div(dcc.Checklist(options=[{'label': "可棄單", 'value': 'abandon'}], value=['abandon'], id='prior_abandon', style={"margin":"20px"})),
    html.Br()
]

item_row = lambda id: [
    html.Div([dcc.Dropdown(id=f"item_port_{id}", placeholder='*PORT', options=port_ls, style=inline_style(150, 'left'))]),
    html.Div([dcc.Dropdown(id=f"item_port_no_{id}", placeholder='port_no', options=[i for i in range(10)],
                           style=inline_style(80, 'left'))]),
    html.Div([dcc.Dropdown(id=f"item_cargo_{id}", placeholder='*CARGO', options=cargo_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.Input(id=f"item_weight_{id}", placeholder="*weight(MT)", type="int", style=inline_style(100, 'left', height='30px'))]),
    html.Div([dcc.Dropdown(id=f"item_demand_{id}", placeholder='*動作', options=demand_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.DatePickerSingle(id=f"item_start_{id}", placeholder='裝期開始', style=inline_style(None, 'left'))]),
    html.Div([dcc.DatePickerSingle(id=f"item_end_{id}", placeholder='裝期結束', style=inline_style(None, 'left', height=43))]),
    html.Div([dcc.Input(id=f'item_unit_income_{id}', placeholder='*單位收入($/MT)', type='int', style=inline_style(100, 'left', height='30px'))]),
    html.Div([dcc.Input(id=f'item_add_days_{id}', placeholder='add days', type='int', style=inline_style(100, 'left', height='30px'))]),
    html.Div([html.Button("ADD", id='item_set', n_clicks=0, style=inline_style(100, 'left', height=40))]),
    html.Div(dcc.Checklist(options=[{'label': "可棄單", 'value': 'abandon'}], value=['abandon'], id='item_abandon', style={"margin":"20px"})),
    html.Br()
]

origin_row = lambda id: [
    html.Div([dcc.Dropdown(id=f"orig_port_{id}", placeholder='*PORT', options=port_ls, style=inline_style(150, 'left'))]),
    html.Div([dcc.Dropdown(id=f"orig_port_no_{id}", placeholder='port_no', options=[i for i in range(10)],
                           style=inline_style(80, 'left'))]),
    html.Div([dcc.Dropdown(id=f"orig_cargo_{id}", placeholder='*CARGO', options=cargo_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.Input(id=f"orig_weight_{id}", placeholder="*weight(MT)", type="int", style=inline_style(100, 'left', height='30px'))]),
    html.Div([dcc.Dropdown(id=f"orig_demand_{id}", placeholder='*動作', options=demand_ls, style=inline_style(120, 'left'))]),
    html.Div([dcc.DatePickerSingle(id=f"orig_date_{id}", placeholder='*排定日期', style=inline_style(None, 'left'))]),
    html.Div([dcc.Input(id=f'orig_unit_income_{id}', placeholder='*單位收入($/MT)', type='int', style=inline_style(100, 'left', height='30px'))]),
    html.Div([dcc.Input(id=f'orig_add_days_{id}', placeholder='add days', type='int', style=inline_style(100, 'left', height='30px'))]),
    html.Div([html.Button("ADD", id='orig_set', n_clicks=0, style=inline_style(100, None, height=40))]),
    html.Br()
]

show_table = lambda data: dash_table.DataTable(data=data, style_table={'width':'50%'})
optimize_table = lambda data: dash_table.DataTable(data=data, style_table={'width':'50%'})
