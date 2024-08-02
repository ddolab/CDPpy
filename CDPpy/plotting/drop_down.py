from dash import html, dcc

def cell_line_dropdown(options):
    return html.Div(children=[
        html.Div("Cell Line: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='cell-line-dropdown',
                     options=options,
                     value=[],
                     placeholder='Select Cell Lines', 
                     multi=True,),],
        style={'width': '40%', 'display': 'inline-block', 'margin-right': '20px'},
        )

def exp_id_dropdown():
    return html.Div(children=[
        html.Div("ID: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='experiment-dropdown',
                     value=[],
                     placeholder='Select Experiment ID',
                     multi=True,),],
        style={'width': '40%', 'display': 'inline-block'},
        )

def cell_profile_dropdown(options):
    return html.Div(children=[
        html.Div("Cell Profile: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='cell-profile-dropdown', 
                     options=options, 
                     value=[],
                     placeholder='Select Cell Profiles',
                     multi=True,)],
        style={'width': '40%', 'display': 'inline-block', 'margin-right': '20px'},
        )

def profile_dropdown(options):
    return html.Div(children=[
        html.Div("Species Profile: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='profile-dropdown', 
                     options=options, 
                     value=[],
                     placeholder='Select Species Profiles',
                     multi=True,)],
        style={'width': '40%', 'display': 'inline-block'},
        )

def species_dropdown(options):
    return html.Div(children=[
        html.Div("Species: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='species-dropdown',
                     options=options,
                     value=[],
                     placeholder='Select Species', 
                     multi=True,),],
        style={'width': '40%', 'display': 'inline-block', 'margin-right': '20px'},
        )

def method_dropdown(options):
    return html.Div(children=[
        html.Div("SP. Rate Method: ", style={"margin-right": "10px", "font-weight": "bold"}),
        dcc.Dropdown(id='method-dropdown', 
                     options=options, 
                     value=[],
                     placeholder='Select Method',multi=True,),],
        style={'width': '40%', 'display': 'inline-block'},
        )
