import plotly.express as px
import plotly.graph_objects as go
from CDPpy.plotting.InteractivePlot import filter_data
from CDPpy_agent.agent.agent import CDPpy_agent

@CDPpy_agent.tool
def get_cell_profiles(self, profiles, run_ids, color_opts=None, line_opts=None, 
                        symbol_opts=None, legend="on", x_axis="Time", viability="on", cell_line=None):
    """
    Refactored: Returns raw Plotly figures for cell profiles.
    """
    if not (run_ids and profiles and cell_line):
        return {}

    # Default options if not provided
    color_opts = color_opts or ["Cell Line", "Cell Line", "Cell Line", "Cell Line"]
    line_opts = line_opts or [None, None, None, None]
    symbol_opts = symbol_opts or [None, None, None, None]

    # Cleaning IDs    
    for cl in cell_line:
        run_ids = [run_id.replace(f'{cl}-', '') for run_id in run_ids]

    cell_data = self.get_cell_data()
    conc_df = cell_data['conc']
    ivcc_df = cell_data['integral']
    cumulative_conc_df = cell_data['cumulative']
    growth_rate_df = cell_data['growth_rate']

    figures = {}

    # 1. VCC Profile
    if 'vcc' in profiles:
        conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
        conc_filtered_by_id = conc_filtered_by_cl if 'All' in run_ids else filter_data(conc_filtered_by_cl, 'ID', run_ids)
        
        vcc_mask = conc_filtered_by_id['state'] == 'VCD'
        df = conc_filtered_by_id[vcc_mask]
        
        fig1 = px.line(df, x=x_axis, y='value', title='Viable Cell Concentration', 
                        color=color_opts[0], line_dash=line_opts[0], symbol=symbol_opts[0])
        fig1.update_yaxes(title_text=f"VCC {df['unit'].iat[0]}")

        if viability == 'on':
            viab_mask = conc_filtered_by_id['state'] == 'Viability'
            df2 = conc_filtered_by_id[viab_mask]
            fig2 = px.line(df2, x=x_axis, y='value', color=color_opts[0], line_dash=line_opts[0], symbol=symbol_opts[0],
                            color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig2.update_traces(yaxis='y2')
            for fig_data in fig2.data:
                fig1.add_trace(fig_data)

            fig1.update_layout(legend_x=1.15, legend_y=1)
            fig1.update_layout(yaxis2={'side': 'right', 'title': 'Viability (%)', 'overlaying': "y"})
        
        figures['vcc'] = fig1
    
    # 2. TCC Profile
    if 'tcc' in profiles:
        conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
        conc_filtered_by_id = conc_filtered_by_cl if 'All' in run_ids else filter_data(conc_filtered_by_cl, 'ID', run_ids)
        tcc_mask = conc_filtered_by_id['state'] == 'TCD'
        df = conc_filtered_by_id[tcc_mask]

        fig = px.line(df, x=x_axis, y='value', title='Total Cell Concentration', 
                        color=color_opts[0], line_dash=line_opts[0], symbol=symbol_opts[0])
        fig.update_yaxes(title_text=f"TCC {df['unit'].iat[0]}")
        figures['tcc'] = fig

    # 3. IVCC Profile
    if 'ivcc' in profiles:
        ivcc_filtered_by_cl = filter_data(ivcc_df, 'Cell Line', cell_line)
        ivcc_filtered_by_id = ivcc_filtered_by_cl if 'All' in run_ids else filter_data(ivcc_filtered_by_cl, 'ID', run_ids)

        fig = px.line(ivcc_filtered_by_id, x=x_axis, y='value', title='Integral Viable Cell Concentration', 
                        color=color_opts[1], line_dash=line_opts[1], symbol=symbol_opts[1])
        fig.update_yaxes(title_text=f"IVCC {ivcc_filtered_by_id['unit'].iat[0]}")
        figures['ivcc'] = fig

    # ... (Repeat similarly for 'cumulative' and 'growthRate')

    # Apply Global Layout Options
    for fig in figures.values():
        fig.update_layout(showlegend=(legend == "on"))
        if legend == "on":
            fig.update_layout(legend_y=1)

    return figures  # Returns Dictionary of { 'profile_name': plotly_figure_obj