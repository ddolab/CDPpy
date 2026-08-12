import plotly.express as px
from pydantic_ai import RunContext
from CDPpy_agent.agent.agent import CDPpy_agent
import streamlit as st

def filter_data(df, column, values):
    """Filtering data by columns with the corresponding values."""
    return df[df[column].isin(values)]

@CDPpy_agent.tool
def get_VCD_profile(ctx: RunContext[dict], 
                    run_ids: list, 
                    cell_line: list,
                    viability: str) -> str:
    """Plots the VCD profile for specfied run IDs and cell lines.
    This function should be used when the user asks for the viable cell density or viable cell concentration or VCC/vcc/VCD/vcd.

    Args:
        ctx (RunContext[dict]): Pydantic AI context
        run_ids (list): List of run IDs to plot VCD profiles for
        cell_line (list): List of cell lines to show VCD profiles for
        viability (str): Show viability profile on the plot

    Returns:
        str: Aserialized JSON string prefixed so the Streamlit UI can detect and render it
    """
    if not (run_ids and cell_line):
            return "Failed: Missing required parameters (run_ids, profiles, or cell_line)."
    
    ## Access fed_batch_obj safely through context dependencies instead of st.session_state
    try: 
        CL_fed_batch = st.session_state.get("fed_batch_obj")
    except:
        try:
            CL_fed_batch = ctx.deps.get("fed_batch_obj")
        except Exception as e:
            return f"Error accessing processed cell line object: {str(e)}"
    if not CL_fed_batch:
        return "Failed: No fed_batch_obj found in session dependencies."

    # Clean IDs
    cleaned_run_ids = list(run_ids)
    for cl in cell_line:
        cleaned_run_ids = [rid.replace(f'{cl}-', '') for rid in cleaned_run_ids]

    cell_data = CL_fed_batch.get_cell_data()
    conc_df = cell_data['conc']
    ivcc_df = cell_data['integral']
    cumulative_conc_df = cell_data['cumulative']
    growth_rate_df = cell_data['growth_rate']

    conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
    conc_filtered_by_id = conc_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(conc_filtered_by_cl, 'ID', cleaned_run_ids)

    x_axis = "Run Time (day)"
    legend = "on"
    color = ["red", "green", "blue", "goldenrod", "magenta"]
    vcc_mask = conc_filtered_by_id['state'] == 'VCD'
    df = conc_filtered_by_id[vcc_mask]
    fig = px.line(df, x=x_axis, y='value', title='Viable Cell Concentration') #, color_discrete_sequence=color, line_dash_sequence=[line], symbol_sequence=[symbol])
    if not df.empty and 'unit' in df.columns:
        fig.update_yaxes(title_text=f"VCC {df['unit'].iat[0]}")

    if viability == 'on':
        viab_mask = conc_filtered_by_id['state'] == 'Viability'
        df2 = conc_filtered_by_id[viab_mask]
        fig2 = px.line(df2, x=x_axis, y='value', color_discrete_sequence=px.colors.qualitative.Pastel1) #, line_dash_sequence=[line], symbol_sequence=[symbol])
        fig2.update_traces(yaxis='y2')
        for fig_data in fig2.data:
            fig.add_trace(fig_data)

        fig.update_layout(legend_x=1.15, legend_y=1)
        fig.update_layout(yaxis2={'side': 'right', 'title': 'Viability (%)', 'overlaying': "y"})
    
    fig.update_layout(showlegend=(legend == "on"))

    # Return serialized JSON string prefixed so the Streamlit UI can detect and render it
    return f"PLOTLY_JSON:{fig.to_json()}"

# @CDPpy_agent.tool
def get_cell_profiles(
    ctx: RunContext[dict], 
    profiles: list, 
    run_ids: list, 
    method: str, 
    cell_line: list,
    color: str = "blue",
    line: str = "solid",
    symbol: str = "circle",
    legend: str = "on", 
    x_axis: str = "Run Time (day)", 
    viability: str = "on"
) -> str:
    """Plots the cell profiles plots (i.e. VCC, TCC, growth rate etc.) for a specified run.

    This function is designed to be called as a tool within the CDPpy Agent framework. It generates interactive Plotly charts based on the processed cell culture data stored in the session state.
    This tool MUST be called after the cell line data has been processed and stored in the session state (i.e., after `process_cell_line_data` has been executed).
    The profiles parameter allows the user to specify which cell profiles to plot. This can include Viable Cell Concentration (VCC), Total Cell Concentration (TCC), Integral Viable Cell Concentration (IVCC), Cumulative Cell Production, and Growth Rate.
    The run_ids parameter allows filtering by specific runs. 
    The method parameter can be used to specify the type of plot (e.g., line, scatter), and additional parameters allow customization of the plot's appearance.

    Args:
        ctx (RunContext[dict]): Run context from pydantic
        profiles (list): Can be VCC, TCC, IVCC, CUMULATIVE, GROWTHRATE
        run_ids (list): Can be a list of run IDs or 'All' to plot all runs
        method (str): The method to use for plotting (e.g., 'line', 'scatter', etc.)
        cell_line (list): Cell line(s) to filter the data for plotting. Can be a list of cell line names or 'All' to include all cell lines.
        color (str, optional): Color of the plot elements. Defaults to "blue".
        line (str, optional): Line style for the plot elements. Defaults to "solid".
        symbol (str, optional): Symbol style for the plot elements. Defaults to "circle".
        legend (str, optional): Whether to display the legend. Defaults to "on".
        x_axis (str, optional): Label for the x-axis. Defaults to "Run Time (day)".
        viability (str, optional): Whether to display viability data. Defaults to "on".

    Returns:
        str: A message indicating the success or failure of the plotting operation.
    """
    print("------------1. Plotting figures------------")

    if not (run_ids and profiles and cell_line):
        return "Failed: Missing required parameters (run_ids, profiles, or cell_line)."

    # Access fed_batch_obj safely through context dependencies instead of st.session_state
    CL_fed_batch = ctx.deps.get("fed_batch_obj")
    if not CL_fed_batch:
        return "Failed: No fed_batch_obj found in session dependencies."

    # Clean IDs
    cleaned_run_ids = list(run_ids)
    for cl in cell_line:
        cleaned_run_ids = [rid.replace(f'{cl}-', '') for rid in cleaned_run_ids]

    cell_data = CL_fed_batch.get_cell_data()
    conc_df = cell_data['conc']
    ivcc_df = cell_data['integral']
    cumulative_conc_df = cell_data['cumulative']
    growth_rate_df = cell_data['growth_rate']

    fig = None

    if 'VCC' in profiles:
        conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
        conc_filtered_by_id = conc_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(conc_filtered_by_cl, 'ID', cleaned_run_ids)
        
        vcc_mask = conc_filtered_by_id['state'] == 'VCD'
        df = conc_filtered_by_id[vcc_mask]
        fig = px.line(df, x=x_axis, y='value', title='Viable Cell Concentration', color_discrete_sequence=[color], line_dash_sequence=[line], symbol_sequence=[symbol])
        if not df.empty and 'unit' in df.columns:
            fig.update_yaxes(title_text=f"VCC {df['unit'].iat[0]}")

        if viability == 'on':
            viab_mask = conc_filtered_by_id['state'] == 'Viability'
            df2 = conc_filtered_by_id[viab_mask]
            fig2 = px.line(df2, x=x_axis, y='value', color_discrete_sequence=px.colors.qualitative.Pastel1, line_dash_sequence=[line], symbol_sequence=[symbol])
            fig2.update_traces(yaxis='y2')
            for fig_data in fig2.data:
                fig.add_trace(fig_data)

            fig.update_layout(legend_x=1.15, legend_y=1)
            fig.update_layout(yaxis2={'side': 'right', 'title': 'Viability (%)', 'overlaying': "y"})
        
        fig.update_layout(showlegend=(legend == "on"))

    elif 'TCC' in profiles:
        conc_filtered_by_cl = filter_data(conc_df, 'Cell Line', cell_line)
        conc_filtered_by_id = conc_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(conc_filtered_by_cl, 'ID', cleaned_run_ids)
        
        tcc_mask = conc_filtered_by_id['state'] == 'TCD'
        df = conc_filtered_by_id[tcc_mask]
        fig = px.line(df, x=x_axis, y='value', title='Total Cell Concentration', color_discrete_sequence=[color], line_dash_sequence=[line], symbol_sequence=[symbol])
        if not df.empty and 'unit' in df.columns:
            fig.update_yaxes(title_text=f"TCC {df['unit'].iat[0]}")
        fig.update_layout(showlegend=(legend == "on"))

    elif 'IVCC' in profiles:
        ivcc_filtered_by_cl = filter_data(ivcc_df, 'Cell Line', cell_line)
        ivcc_filtered_by_id = ivcc_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(ivcc_filtered_by_cl, 'ID', cleaned_run_ids)
        fig = px.line(ivcc_filtered_by_id, x=x_axis, y='value', title='Integral Viable Cell Concentration', color_discrete_sequence=[color], line_dash_sequence=[line], symbol_sequence=[symbol])
        fig.update_layout(showlegend=(legend == "on"))

    elif 'CUMULATIVE' in profiles:
        cum_filtered_by_cl = filter_data(cumulative_conc_df, 'Cell Line', cell_line)
        cum_filtered_by_id = cum_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(cum_filtered_by_cl, 'ID', cleaned_run_ids)
        fig = px.line(cum_filtered_by_id, x=x_axis, y='value', title='Cumulative Cell Production', color_discrete_sequence=[color], line_dash_sequence=[line], symbol_sequence=[symbol])
        fig.update_layout(showlegend=(legend == "on"))

    elif 'GROWTHRATE' in profiles:
        gr_filtered_by_cl = filter_data(growth_rate_df, 'Cell Line', cell_line)
        gr_filtered_by_id = gr_filtered_by_cl if 'All' in cleaned_run_ids else filter_data(gr_filtered_by_cl, 'ID', cleaned_run_ids)
        fig = px.line(gr_filtered_by_id, x=x_axis, y='value', title='Growth Rate', color_discrete_sequence=[color], line_dash_sequence=[line], symbol_sequence=[symbol])
        fig.update_layout(showlegend=(legend == "on"))

    if fig:
        # Save figure directly in context deps dictionary so main Streamlit thread can extract it
        print("Saving generated figure to context dependencies for rendering...")
        ctx.deps["generated_fig"] = fig
        return f"Successfully generated chart for {profiles}."
    
    return "No valid profiles processed."