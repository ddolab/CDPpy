from dash import html, dcc

VCC_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('VCC/TCC Profile Style', id='toggle-button-vcc-style'),
        html.Br(),
        html.Div(id='toggle-output-vcc-style', children=None)
    ]
)
IVCC_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('IVCC Profile Style', id='toggle-button-ivcc-style'),
        html.Br(),
        html.Div(id='toggle-output-ivcc-style', children=None)
    ]
)
CUMULATIVE_CELL_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('Cumulative Cell Profile Style', id='toggle-button-cell-cumulative-style'),
        html.Br(),
        html.Div(id='toggle-output-cell-cumulative-style', children=None)
    ]
)
GROWTH_RATE_PROFILE_STYLE = html.Div(style={'margin-right': '30px'},
    children = [
        html.Button('Growth Rate Profile Style', id='toggle-button-growth-rate-style'),
        html.Br(),
        html.Div(id='toggle-output-growth-rate-style', children=None)
    ]
)
CONCENTRATION_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('Concentration Profile Style', id='toggle-button-concentration-style'),
        html.Br(),
        html.Div(id='toggle-output-concentration-style', children=None)
    ]
)
CUMULATIVE_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('Cumulative Profile Style', id='toggle-button-cumulative-style'),
        html.Br(),
        html.Div(id='toggle-output-cumulative-style', children=None)
    ]
)
SP_RATE_PROFILE_STYLE = html.Div(
    style={'margin-right': '40px'},
    children = [
        html.Button('SP. Rate Profile Style', id='toggle-button-sp-rate-style'),
        html.Br(),
        html.Div(id='toggle-output-sp-rate-style', children=None)
    ]
)
X_AXIS_STYLE = html.Div([
    html.Label('x-axis', style={"font-weight": "bold"}),
    dcc.RadioItems(
        id='x-axis-radio',
        options=[{'label': 'Day', 'value': 'Run Time (day)'},
                 {'label': 'Hour', 'value': 'Run Time (hr)'}],
        value='Run Time (hr)', 
        inline=True,),
    ], 
    style={'margin-right': '40px'}
)
LEGEND_STYLE = html.Div([
    html.Label('Legend', style={"font-weight": "bold"}),
    dcc.RadioItems(
        id='legend-radio', 
        options=['on', "off"], 
        value='on', 
        inline=True,),
    ]
)

RADIO_BUTTONS_1 = [VCC_PROFILE_STYLE, 
                   IVCC_PROFILE_STYLE, 
                   CUMULATIVE_CELL_PROFILE_STYLE, 
                   GROWTH_RATE_PROFILE_STYLE]

RADIO_BUTTONS_2 = [CONCENTRATION_PROFILE_STYLE, 
                   CUMULATIVE_PROFILE_STYLE,
                   SP_RATE_PROFILE_STYLE]

RADIO_BUTTONS_3 = [X_AXIS_STYLE,
                   LEGEND_STYLE]