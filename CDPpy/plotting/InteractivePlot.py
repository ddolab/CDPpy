# Import packages
import numpy as np
# from jupyter_dash import JupyterDash
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px

from .layout import CELL_CONCENTRATION_STYLE_CHILDREN, CELL_INTEGRAL_STYLE_CHILDREN, CELL_CUMULATIVE_STYLE_CHILDREN, GROWTH_RATE_STYLE_CHILDREN
from .layout import CONCENTRATION_STYLE_CHILDREN, CUMULATIVE_STYLE_CHILDREN, SP_RATE_STYLE_CHILDREN
from .options import PROFILE_OPTIONS, CELL_PROFILE_OPTIONS
from .options import TWO_POINT_CALC, POLYNOMIAL, ROLLING_WINDOW
from .options import CELL_LINE_OPTION, EXP_OPTION, METHOD_OPTION
from .drop_down import cell_line_dropdown, exp_id_dropdown, cell_profile_dropdown, profile_dropdown, species_dropdown, method_dropdown
from .radio_buttons import RADIO_BUTTONS_1, RADIO_BUTTONS_2, RADIO_BUTTONS_3

class InteractivePlotMixin:
    '''Mixin class used in CellLine class for displaying an interactive plot.
    '''
    def __init_options(self, spec_list, method_list):
        '''Initialize options for the interactive plot.
        '''
        # Cell line list
        cell_line_list = list(self.get_cell_line_handles().keys())
        # cell_line_options = list(self._processed_cell_lines.keys())
        cell_line_options = list(self._processed_cell_lines.keys())

        # Cell line options; [{'label': 'CL1', 'value': ['CL1-1', 'CL1-2', 'CL1-3']}]
        # Experiment ID options; {'cell line': 'experiment ID'}
        exp_options = self._processed_cell_lines
        for cell_line in cell_line_list:
            cell_line_handler = self.get_cell_line_handles(cell_line)
            exp_list = list(cell_line_handler.get_experiment_handle().keys())
            exp_options[cell_line] = [exp for exp in exp_list]
        #print(exp_options)

        # Species options
        species_options = spec_list
        
        # Method options for cumulative concentration and specific rate
        method_options = [TWO_POINT_CALC]
        if 'polynomial' in method_list:
            method_options.append(POLYNOMIAL)
        if 'rollingWindowPolynomial' in method_list:
            method_options.append(ROLLING_WINDOW)
        
        # Plot style options for each profile
        plot_style_options = [CELL_LINE_OPTION, EXP_OPTION]
        plot_style_options2 = [CELL_LINE_OPTION, EXP_OPTION, METHOD_OPTION]

        options = {'Cell Line': cell_line_options,
                   'ID': exp_options,
                   'species': species_options,
                   'profile': PROFILE_OPTIONS,
                   'cell_profile': CELL_PROFILE_OPTIONS,
                   'method': method_options,
                   'style1': plot_style_options,
                   'style2': plot_style_options2}
        return options
    
    def __init_layout(self, mode, options):
        '''Initialize the layout
        '''
        # Initialize the app
        # if mode=='inline':
        #     app = JupyterDash(__name__)
        # else:
        app = Dash(__name__)

        # Get options
        cell_line_options = options['Cell Line']
        exp_options = options['ID']
        species_options = options['species']
        cell_profile_options = options['cell_profile']
        profile_options = options['profile']
        method_options = options['method']
        plot_style_options1 = options['style1']
        plot_style_options2 = options['style2']

        #
        global radio_buttons

        # App layout
        app.layout = html.Div([
            html.Div(
                children=[
                    cell_line_dropdown(options=cell_line_options),
                    exp_id_dropdown()
                ],
                style={'display': 'flex', 'align-items': 'center'},
            ),
            html.Hr(),
            html.Div(
                children=[
                    cell_profile_dropdown(options=cell_profile_options),
                    profile_dropdown(options=profile_options)
                ],
                style={'display': 'flex', 'align-items': 'center'},
            ),
            html.Hr(),
            html.Div(
                children=[
                    species_dropdown(options=species_options),
                    method_dropdown(options=method_options)
                ],
                style={'display': 'flex', 'align-items': 'center'},
            ),
            html.Hr(),
            html.Div(children=RADIO_BUTTONS_1, id='radio-container-1', style={'display': 'flex', 'flex-direction': 'row',}),
            html.Hr(),
            html.Div(children=RADIO_BUTTONS_2, id='radio-container-2', style={'display': 'flex', 'flex-direction': 'row',}),
            html.Hr(),
            html.Div(children=RADIO_BUTTONS_3, id='radio-container-3', style={'display': 'flex', 'flex-direction': 'row',}),
            html.Hr(),
            # Display Cell
            html.Div(id='figure-container-cell'),
            # Display Metabolite
            html.Div(id='figure-container-metabolite'),
        ])
        return app

    def interactive_plot(self, port=8050, mode='inline'):
        '''Interactive Plot.
        '''
        # Initialization
        data = self.get_metabolite_data()['sp_rate']
        species_list = data['species'].unique()
        method_list = data['method'].unique()

        options = self.__init_options(species_list, method_list)
        app = self.__init_layout(mode=mode, options=options)

        # Update expriment ID dropdown
        app.callback(
            Output(component_id='experiment-dropdown', component_property='options'),
            Input(component_id='cell-line-dropdown', component_property='value'),
        )(self.__set_exp_options)

        # Toggle On/Off
        app.callback(
            Output('toggle-output-vcc-style', 'children'),
            [Input('toggle-button-vcc-style', 'n_clicks')],
            [State('toggle-output-vcc-style', 'children')]
        )(self.__toggle_output_vcc)

        app.callback(
            Output('toggle-output-ivcc-style', 'children'),
            [Input('toggle-button-ivcc-style', 'n_clicks')],
            [State('toggle-output-ivcc-style', 'children')]
        )(self.__toggle_output_ivcc)

        app.callback(
            Output('toggle-output-cell-cumulative-style', 'children'),
            [Input('toggle-button-cell-cumulative-style', 'n_clicks')],
            [State('toggle-output-cell-cumulative-style', 'children')]
        )(self.__toggle_output_cell_cumulative)

        app.callback(
            Output('toggle-output-growth-rate-style', 'children'),
            [Input('toggle-button-growth-rate-style', 'n_clicks')],
            [State('toggle-output-growth-rate-style', 'children')]
        )(self.__toggle_output_growth_rate)

        app.callback(
            Output('toggle-output-concentration-style', 'children'),
            [Input('toggle-button-concentration-style', 'n_clicks')],
            [State('toggle-output-concentration-style', 'children')]
        )(self.__toggle_output_conc)

        app.callback(
            Output('toggle-output-cumulative-style', 'children'),
            [Input('toggle-button-cumulative-style', 'n_clicks')],
            [State('toggle-output-cumulative-style', 'children')]
        )(self.__toggle_output_cumulative)

        app.callback(
            Output('toggle-output-sp-rate-style', 'children'),
            [Input('toggle-button-sp-rate-style', 'n_clicks')],
            [State('toggle-output-sp-rate-style', 'children')]
        )(self.__toggle_output_sp_rate)

        # Update cell profiles to display
        app.callback(
            Output('figure-container-cell', 'children'),
            Input('cell-profile-dropdown', 'value'),
            Input('experiment-dropdown', 'value'),
            Input('method-dropdown', 'value'),

            Input('color-option-vcc', 'value'),
            Input('color-option-ivcc', 'value'),
            Input('color-option-cell-cumulative', 'value'),
            Input('color-option-growth-rate', 'value'),

            Input('line-option-vcc', 'value'),
            Input('line-option-ivcc', 'value'),
            Input('line-option-cell-cumulative', 'value'),
            Input('line-option-growth-rate', 'value'),

            Input('symbol-option-vcc', 'value'),
            Input('symbol-option-ivcc', 'value'),
            Input('symbol-option-cell-cumulative', 'value'),
            Input('symbol-option-growth-rate', 'value'),

            Input('legend-radio', 'value'),
            Input('x-axis-radio', 'value'),
            Input('viability-radio', 'value'),
            State('cell-line-dropdown', 'value')
        )(self.__display_cell_profiles)

        # Update metabolite profiles to display
        app.callback(
            Output('figure-container-metabolite', 'children'),
            Input('profile-dropdown', 'value'),
            Input('experiment-dropdown', 'value'),
            Input('species-dropdown', 'value'),
            Input('method-dropdown', 'value'),
            Input('color-option-1', 'value'),
            Input('color-option-2', 'value'),
            Input('color-option-3', 'value'),
            Input('line-option-1', 'value'),
            Input('line-option-2', 'value'),
            Input('line-option-3', 'value'),
            Input('symbol-option-1', 'value'),
            Input('symbol-option-2', 'value'),
            Input('symbol-option-3', 'value'),
            Input('legend-radio', 'value'),
            Input('x-axis-radio', 'value'),
            State('cell-line-dropdown', 'value')
        )(self.__display_profiles)

        # Start the app
        if mode=='inline':
            app.run_server(port=port, mode="inline")
        else:
            app.run_server(port=port)
    
    def __set_exp_options(self, cl_chosen):
        '''Update expriment ID dropdown
        '''
        options = []
        if cl_chosen==[]:
            return options
        for cl in cl_chosen:
            #cell_line_handler = self.get_cell_line_handles(cl)
            #exp_list = list(cell_line_handler.get_experiment_handle().keys())
            exp_list = self._processed_cell_lines[cl]
            for exp in exp_list:
                options.append({'label': f'{cl}-{exp}', 'value': f'{cl}-{exp}'})
        return options
    
    def __toggle_output_vcc(self, n_clicks, current_children):
        ''''''
        hidden_children = CELL_CONCENTRATION_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
        
    def __toggle_output_ivcc(self, n_clicks, current_children):
        ''''''
        hidden_children = CELL_INTEGRAL_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
    
    def __toggle_output_cell_cumulative(self, n_clicks, current_children):
        ''''''
        hidden_children =  CELL_CUMULATIVE_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
        
    def __toggle_output_growth_rate(self, n_clicks, current_children):
        ''''''
        hidden_children =  GROWTH_RATE_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
    
    def __toggle_output_conc(self, n_clicks, current_children):
        ''''''
        hidden_children =  CONCENTRATION_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
    
    def __toggle_output_cumulative(self, n_clicks, current_children):
        ''''''
        hidden_children =  CUMULATIVE_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children
        
    def __toggle_output_sp_rate(self, n_clicks, current_children):
        ''''''
        hidden_children =  SP_RATE_STYLE_CHILDREN
        if n_clicks is None:
            return hidden_children
        if current_children is not None:
            return None
        else:
            return hidden_children

    def __display_cell_profiles(self, profiles, run_ids, method, 
                                color_1, color_2, color_3, color_4,
                                line_1, line_2, line_3, line_4, 
                                symbol_1, symbol_2, symbol_3, symbol_4,
                                legend, x_axis, viability, cell_line):
        ''''''
        if not (run_ids and profiles and cell_line):
            return None
        # Cleaning IDs    
        for cl in cell_line:
            run_ids = [id.replace(f'{cl}-', '') for id in run_ids]

        # print(cell_line, run_ids, profiles)
        
        # Get data
        cell_data = self.get_cell_data()

        # Get data
        conc_df = cell_data['conc']
        ivcc_df = cell_data['integral']
        cumulative_conc_df = cell_data['cumulative']
        growth_rate_df = cell_data['growth_rate']

        figures = {}
        if 'vcc' in profiles:
            # Filtering by Cell Line and ID
            conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
            conc_filtered_by_id = filter_data(conc_filtered_by_cl, 'ID', run_ids)
            
            # Filtering by VCD
            vcc_mask = conc_filtered_by_id['state']=='VCD'
            df = conc_filtered_by_id[vcc_mask]
            fig1 = px.line(df, x=x_axis, y='value', title='Viable Cell Concentration', color=color_1, line_dash=line_1, symbol=symbol_1)
            fig1.update_yaxes(title_text=f"VCC {df['unit'].iat[0]}")

            if viability=='on':
                # Filtering by Viability
                viab_mask = conc_filtered_by_id['state']=='Viability'
                df2 = conc_filtered_by_id[viab_mask]
                fig2 = px.line(df2, x=x_axis, y='value', color=color_1, line_dash=line_1, symbol=symbol_1,
                               color_discrete_sequence=px.colors.qualitative.Pastel1,)
                fig2.update_traces(yaxis='y2')
                for fig_data in fig2.data:
                    fig1.add_trace(fig_data)

                fig1.update_layout(legend_x=1.15, legend_y=1)
                fig1.update_layout(yaxis2={'side': 'right', 'title': 'Viability (%)', 'overlaying': "y",})
            
            figures['figure1'] = fig1
        
        if 'tcc' in profiles:
            # Filtering by Cell Line and ID
            conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
            conc_filtered_by_id = filter_data(conc_filtered_by_cl, 'ID', run_ids)

            # Filtering by TCD
            tcc_mask = conc_filtered_by_id['state']=='TCD'
            df = conc_filtered_by_id[tcc_mask]

            fig = px.line(df, x=x_axis, y='value', title='Total Cell Concentration', color=color_1, line_dash=line_1, symbol=symbol_1)
            fig.update_yaxes(title_text=f"TCC {df['unit'].iat[0]}")
            figures['figure2'] = fig

        if 'ivcc' in profiles:
            # Filtering by Cell Line and ID
            ivcc_filtered_by_cl = filter_data(ivcc_df, 'Cell Line', cell_line)
            ivcc_filtered_by_id = filter_data(ivcc_filtered_by_cl, 'ID', run_ids)

            fig = px.line(ivcc_filtered_by_id, x=x_axis, y='value', title='Integral Viable Cell Concentration', color=color_2, line_dash=line_2, symbol=symbol_2)
            fig.update_yaxes(title_text=f"IVCC {ivcc_filtered_by_id['unit'].iat[0]}")
            figures['figure3'] = fig

        if 'cumulative' in profiles:
            # Filtering by Cell Line and ID
            cumulative_filtered_by_cl = filter_data(cumulative_conc_df, 'Cell Line', cell_line)
            cumulative_filtered_by_id = filter_data(cumulative_filtered_by_cl, 'ID', run_ids)

            fig = px.line(cumulative_filtered_by_id, x=x_axis, y='value', title='Cumulative Cell Production', color=color_3, line_dash=line_3, symbol=symbol_3)
            fig.update_yaxes(title_text=f"Cumulative Cell Production {cumulative_filtered_by_id['unit'].iat[0]}")
            figures['figure4'] = fig

        if 'growthRate' in profiles:
            # Filtering by Cell Line and ID
            growth_rate_filtered_by_cl = filter_data(growth_rate_df, 'Cell Line', cell_line)
            growth_rate_filtered_by_id = filter_data(growth_rate_filtered_by_cl, 'ID', run_ids)

            fig = px.line(growth_rate_filtered_by_id, x=x_axis, y='value', title='Growth Rate', color=color_4, line_dash=line_4, symbol=symbol_4)
            fig.update_yaxes(title_text=f"Growth Rate {growth_rate_filtered_by_id['unit'].iat[0]}")
            figures['figure5'] = fig

        for fig in figures.values():
            if legend=="on":
                fig.update_layout(showlegend=True, legend_y=1)
            else:
                fig.update_layout(showlegend=False)
        ''
        # Create children
        children = [dcc.Graph(figure=fig, id=id) for id, fig in figures.items()]
        return [html.Div(
                    style={'overflow-x': 'scroll', 'display': 'flex'},
                    children=children,
                ),]

    
    def __display_profiles(self, profiles, run_ids, species, method, 
                           color_1, color_2, color_3, 
                           line_1, line_2, line_3,
                           symbol_1, symbol_2, symbol_3, 
                           legend, x_axis, cell_line):
        '''Display profiles. 
        '''
        if not (run_ids and species and profiles and cell_line):
            return None
        # Cleaning IDs    
        for cl in cell_line:
            run_ids = [id.replace(f'{cl}-', '') for id in run_ids]

        data = self.get_metabolite_data()
        
        # Filtering data
        conc_df = data['conc']
        cumulative_conc_df = data['cumulative']
        sp_rate_df = data['sp_rate']

        # Filter data by species, Cell Line and ID
        conc_df = filter_data(conc_df, 'species', species)
        conc_df = filter_data(conc_df, 'Cell Line', cell_line)
        conc_df = filter_data(conc_df, 'ID', run_ids)
        cumulative_conc_df = filter_data(cumulative_conc_df, 'species', species)
        cumulative_conc_df = filter_data(cumulative_conc_df, 'Cell Line', cell_line)
        cumulative_conc_df = filter_data(cumulative_conc_df, 'ID', run_ids)
        sp_rate_df = filter_data(sp_rate_df, 'species', species)
        sp_rate_df = filter_data(sp_rate_df, 'Cell Line', cell_line)
        sp_rate_df = filter_data(sp_rate_df, 'ID', run_ids)
        
        # Creating figures
        figures = {}
        if 'concentration' in profiles:
            fig = create_figure(conc_df, x_axis, 'line', True, 'Concentration', color_1, line_1, symbol_1, legend)
            fig = rename_yaxis(conc_df, fig, 'concentration')
            figures['figure1'] = fig

        if 'cumulative' in profiles:
            data1 = filter_data(cumulative_conc_df, 'method', ['twoPoint'])
            data2 = filter_data(cumulative_conc_df, 'method', ['polynomial'])

            fig1 = create_figure(data1, x_axis, 'scatter', False, 'Cumulative Consumption/Production', color_2, line_2, symbol_2, legend)
            fig2 = create_figure(data2, x_axis, 'line', False, 'Cumulative Concentration', color_2, line_2, None, legend)
            for fig_data in fig2.data:
                fig1.add_trace(fig_data)
            fig = rename_yaxis(data2, fig1, 'cumulative')
            fig = rename_yaxis(data1, fig1, 'cumulative')
            figures['figure2'] = fig

        if 'spRate' in profiles and method:
            data = filter_data(sp_rate_df, 'method', method)
            fig = create_figure(data, x_axis, 'line', True, 'Specific Rate', color_3, line_3, symbol_3, legend)
            fig = rename_yaxis(data, fig, 'spRate')
            figures['figure3'] = fig
        
        # Create children
        children = [dcc.Graph(figure=fig, id=id) for id, fig in figures.items()]
        return [html.Div(
                    style={'overflow-x': 'scroll', 'display': 'flex'},
                    children=children,
                ),]

def create_figure(df, x, kind, makers, title, color, line_dash, symbol, legend):
    '''Create a figure of plotly.express
    '''
    if kind=='line':
        fig = px.line(df, x=x, y='value', title=title, facet_row='species',
                      markers=makers,
                      color=color,
                      line_dash=line_dash,
                      symbol=symbol,
                      )
        
    elif kind=='scatter':
        fig = px.scatter(df, x=x, y='value', title=title, facet_row='species',
                         color=color,
                         symbol=symbol,
                         )
    
    fig.update_yaxes(matches=None)
    fig.for_each_annotation(lambda a: a.update(visible=False))

    spc_list = df['species'].unique()
    height_per_row = 500
    fig.update_layout(height=height_per_row * len(spc_list), width=800)

    if legend=="on":
        fig.update_layout(showlegend=True, legend_x=1, legend_y=1)
    else:
        fig.update_layout(showlegend=False)
    return fig

def filter_data(df, column, values):
    '''filtering data by columns with the corresponding values.'''
    return df[df[column].isin(values)]

def rename_yaxis(df, fig, profile):
    '''Rename y-axis nanme.
    '''
    spc_list = df['species'].unique()
    yaxis_titles = {}
    for name in spc_list:
        mask = df['species']==name
        unit = df[mask]['unit'].iat[0]

        if profile=='cumulative':
            state = df[mask]['state'].iat[0]
            yaxis_titles[name] = f"Cumulative {name} {state} {unit}"
        elif profile=='spRate':
            yaxis_titles[name] = f"q{name} {unit}"
        else:
            yaxis_titles[name] = f"{name} {unit}"

    for i, annotation in enumerate(fig.layout.annotations):
        yaxis = 'yaxis' + str(i + 1)
        fig['layout'][yaxis]['title']['text'] = yaxis_titles[annotation.text.split('=')[-1]]
    return fig

