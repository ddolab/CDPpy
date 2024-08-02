from dash import html, dcc

CELL_CONCENTRATION_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  '),
        dcc.RadioItems(
            id='color-option-vcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
            ],
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-vcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
            ],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol'),
        dcc.RadioItems(
            id='symbol-option-vcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
            ],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Viability'),
        dcc.RadioItems(
            id='viability-radio',
            options=['on', "off"], 
            value='on', 
            inline=True,
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),]

CELL_INTEGRAL_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  '),
        dcc.RadioItems(
            id='color-option-ivcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-ivcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol'),
        dcc.RadioItems(
            id='symbol-option-ivcc',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        )
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),]

GROWTH_RATE_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  ', ),
        dcc.RadioItems(
            id='color-option-growth-rate',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
                {'label': 'Method', 'value': 'method'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-growth-rate',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
                {'label': 'Method', 'value': 'method'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol: '),
        dcc.RadioItems(
            id='symbol-option-growth-rate',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'},
                {'label': 'Method', 'value': 'method'}],
            value='method',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        )
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'})
]

CELL_CUMULATIVE_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  '),
        dcc.RadioItems(
            id='color-option-cell-cumulative',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-cell-cumulative',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol'),
        dcc.RadioItems(
            id='symbol-option-cell-cumulative',
            options=[
                {'label': 'Cell Line', 'value': 'Cell Line'},
                {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        )
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),]

CONCENTRATION_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  '),
        dcc.RadioItems(
            id='color-option-1',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-1',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol'),
        dcc.RadioItems(
            id='symbol-option-1',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}],
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'})]

CUMULATIVE_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  '),
        dcc.RadioItems(
            id='color-option-2',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-2',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol'),
        dcc.RadioItems(
            id='symbol-option-2',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        )
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),]

SP_RATE_STYLE_CHILDREN = [
    html.Div([
        html.Label('Color:  ', ),
        dcc.RadioItems(
            id='color-option-3',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'},
                        {'label': 'Method', 'value': 'method'}], 
            value='Cell Line',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Line:   '),
        dcc.RadioItems(
            id='line-option-3',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                        {'label': 'ID', 'value': 'ID'},
                        {'label': 'Method', 'value': 'method'}],
            value='ID',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        ),
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'}),
    html.Div([
        html.Label('Symbol: '),
        dcc.RadioItems(
            id='symbol-option-3',
            options=[{'label': 'Cell Line', 'value': 'Cell Line'},
                     {'label': 'ID', 'value': 'ID'},
                     {'label': 'Method', 'value': 'method'}],
            value='method',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'},
        )
    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '5px'})
]