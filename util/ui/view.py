from dash import dcc
from dash import html, dash_table
from view_base import *
from datetime import datetime, date


VIEW = html.Div([
    html.Div([
        html.P("1. 既定項目: (不會被棄單)"),
        html.Div(origin_row(0)),
        html.Div(id='container_orig', children=[]),
        html.Div([dcc.Input(id='orig_delete_num', placeholder='No.', type='str', style=inline_style(100, 'left')),
                  html.Button('DELETE', id='delete_orig')]),
        dcc.Store(id='Store_orig', data='{}'),
        html.Br()
    ]),
    html.Div([
        html.P("2. 載卸貨項目: (支援多載多卸，使用組號做區別。一個組號只要填一次收入。)"),
        html.Div(prior_row(0)),
        html.Div(id='container_prior', children=[]),
        html.Div([dcc.Input(id='prior_delete_num', placeholder='No.', type='str', style=inline_style(100, 'left')),
                  html.Button('DELETE', id='delete_prior')]),
        dcc.Store(id='Store_prior', data='{}'),
        html.Br()
    ]),
    html.Div([
        html.P("3. 單項:"),
        html.Div(item_row(0)),
        html.Div(id='container_item', children=[]),
        html.Div([dcc.Input(id='item_delete_num', placeholder='No.', type='str', style=inline_style(100, 'left')),
                  html.Button('DELETE', id='delete_item')]),
        dcc.Store(id='Store_item', data='{}'),
        html.Br()
    ]),
    html.Div([
        html.P("4. 船條件 (船ID、船載重限制、最大航行天數、最佳化條件)"),
        dcc.Dropdown(options=ship_ls, id='ship_id', placeholder='船ID', value=31, style=inline_style(100, 'left')),
        dcc.Input(id='ship_limit_weight', type='int', placeholder='船載重限制', style=inline_style(120, 'left', height='30px')),
        dcc.Input(id='max_route_days', type='int', placeholder='最大航行天數', style=inline_style(120, 'left', height='30px')),
        dcc.Dropdown(options=opt_method_ls, id='opt_method', value=opt_method_ls[0]['value'], placeholder='最佳化條件', style=inline_style(150, 'left')),
        dcc.Checklist(id='is_panama', options=[{'label': '通過巴拿馬', 'value': 'is_panama'}], value=[], style={'margin':'20px', 'float': 'left'}),
        dcc.Input(id='panama_fee', type='int', placeholder='panama fee', style=inline_style(120, 'left', height='30px')),
        dcc.Input(id='panama_days', type='float', placeholder='panama days', style=inline_style(120, None, height='30px')),
        html.Br(), html.Br(), html.Br(),
        dcc.Markdown(id='ship_message', children=[], style=inline_style(400, 'left')),
        html.Br(), html.Br(),
        dcc.Store(id='Store_limit', data='{}'),
        html.Br(), html.Br()
    ]),
    html.Div([
        html.Br(),
        html.P("5. 船初始狀態"),
        dcc.Dropdown(id="initPort", placeholder='location', value='MAILIAO', options=port_ls, style=inline_style(150, 'left')),
        dcc.DatePickerSingle(id='initDate', placeholder='Date', date=date.today(), style=inline_style(None, None)),
        html.Label('     at 8:00 AM'),
        html.Br()
    ]),
    html.Div([
        html.P("6. 貨艙初始狀態: (預設每艙最大容量10000)"),
        dcc.Checklist(options=[{'label': "考慮貨艙限制", 'value': 'com_valid'}], value=['com_valid'],
                      id='com_valid', style={"margin":"20px"}),
        html.Label("Unit of Quantity:", style=inline_style(130, 'left')),
        dcc.Dropdown(options=["volume"], id='com_unit', value='volume', style={"width":"30%"}),
        html.Div([
            html.Div([html.Label(com_ls[com_int], style=inline_style(50, 'left')),
            dcc.Dropdown(
                options=cargo_ls+[None],
                id=f'cargo_name_{com_int}',
                placeholder='CARGO',
                style={'display':'inline-block', 'float':'left', 'width':100}
            ),
            dcc.Input(
                id=f'cargo_amount_{com_int}',
                type='int',
                value=0,
                placeholder="AMOUNT",
                style={"display":"inline-block", "width":100, 'float':'left', 'height':'30px'}
            ),
            dcc.Dropdown(
                options=cargo_ls,
                id=f'cargo_pre3_{com_int}',
                placeholder='PRE3',
                style={'display':'inline-block', 'width':300},
                multi=True
            )]) for com_int in range(len(com_ls))
        ]),
        html.Button('貨艙存檔', id='com_save', style=inline_style('30%', 100, height=35)),
        dcc.Store(id='Store_com', data='{}')
    ]),
    html.Br(),
    html.Div([html.Button('COMPUTE OPTIMIZATION ROUTES', id='Optimize',
              style=inline_style('100%', 100, height=60))]),
    html.Div([dcc.Markdown("Information Shows Here ....")], id='container_markdown')

])
