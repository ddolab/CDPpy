import plotly.express as px
from typing import List, Literal, Optional
from pydantic_ai import RunContext
from CDPpy_agent.agent.agent import CDPpy_agent
from pydantic import BaseModel, Field
import streamlit as st
import threading
import pandas as pd


def filter_data(df, column, values):
    """Filtering data by columns with the corresponding values."""
    return df[df[column].isin(values)]


class MergePlotlyConfig(BaseModel):
    # Core Data Mapping
    x_col: str = Field(description="Column name for the X axis")
    y_col: str = Field(description="Column name for the Y axis")
    group_col: Optional[str] = Field(
        default=None,
        description="Column to group/color lines, bars, or points by (e.g., 'Batch', 'Replicate')",
    )
    facet_col: Optional[str] = Field(
        default=None,
        description="Column to split plot into side-by-side subplots (facets)",
    )

    # Chart Styling & Types
    chart_type: Literal["line", "bar", "scatter", "area"] = Field(
        default="line", description="Chart visualization style"
    )
    title: str = Field(
        default="Bioprocess Data Plot", description="Main title of the plot"
    )
    x_label: Optional[str] = Field(
        default=None,
        description="Custom label for the X-axis (e.g., 'Culture Time (hours)')",
    )
    y_label: Optional[str] = Field(
        default=None,
        description="Custom label for the Y-axis (e.g., 'VCD (10^6 cells/mL)')",
    )

    # Axis Controls
    log_x: bool = Field(default=False, description="Set X-axis to logarithmic scale")
    log_y: bool = Field(default=False, description="Set Y-axis to logarithmic scale")

    # Visual Adjustments
    show_markers: bool = Field(
        default=True, description="Show markers/dots on line or area charts"
    )
    barmode: Literal["group", "stack", "overlay"] = Field(
        default="group", description="Bar chart layout mode when group_col is supplied"
    )
    height: int = Field(
        default=500, description="Height of the rendered chart in pixels"
    )


@CDPpy_agent.tool
def merge_and_plot_data(
    ctx: RunContext[dict],
    config: MergePlotlyConfig,
    key1: str,
    key2: str,
    on_cols: List[str],
) -> str:
    """Merges two datasets stored in data_store using an inner join and generates a Plotly chart with advanced configuration.

    Args:
        config (MergePlotlyConfig): Comprehensive plot visual settings.
        key1 (str): First key in data_store (e.g. 'cell_subset').
        key2 (str): Second key in data_store (e.g. 'metabolite_subset').
        on_cols (List[str]): Column name(s) to perform the inner join on (e.g. ['Time'] or ['Time', 'Batch']).

    Returns:
        str: JSON string of the Plotly figure formatted as 'PLOTLY_JSON:<json>', or an error message string.
    """
    # 1. Safely retrieve data_store from st.session_state or ctx.deps
    data_store = None
    if "data_store" in st.session_state:
        data_store = st.session_state["data_store"]
    elif isinstance(ctx.deps, dict) and "data_store" in ctx.deps:
        data_store = ctx.deps["data_store"]

    if not data_store:
        return "Error: `data_store` is uninitialized or empty. Please run a data query tool first."

    # 2. Extract DataFrames
    df1 = data_store.get(key1)
    df2 = data_store.get(key2)

    if df1 is None or df1.empty:
        return (
            f"Error: Dataset for key '{key1}' does not exist or is empty in data_store."
        )
    if df2 is None or df2.empty:
        return (
            f"Error: Dataset for key '{key2}' does not exist or is empty in data_store."
        )

    # 3. Perform Inner Join
    try:
        merged_df = pd.merge(df1, df2, on=on_cols, how="inner")

        if merged_df.empty:
            return f"Warning: Inner join between '{key1}' and '{key2}' on {on_cols} yielded 0 matching rows."
    except Exception as e:
        return f"Error performing inner join on columns {on_cols}: {str(e)}"

    # 4. Construct Plotly Figure based on config
    try:
        plot_kwargs = {
            "data_frame": merged_df,
            "x": config.x_col,
            "y": config.y_col,
            "color": config.group_col,
            "facet_col": config.facet_col,
            "title": config.title,
            "log_x": config.log_x,
            "log_y": config.log_y,
            "height": config.height,
            "labels": {},
        }

        # Custom Axis Labels
        if config.x_label:
            plot_kwargs["labels"][config.x_col] = config.x_label
        if config.y_label:
            plot_kwargs["labels"][config.y_col] = config.y_label

        # Chart Type Selection
        if config.chart_type == "bar":
            plot_kwargs["barmode"] = config.barmode
            fig = px.bar(**plot_kwargs)
        elif config.chart_type == "scatter":
            fig = px.scatter(**plot_kwargs)
        elif config.chart_type == "area":
            fig = px.area(**plot_kwargs)
        else:  # line
            plot_kwargs["markers"] = config.show_markers
            fig = px.line(**plot_kwargs)

        fig.update_layout(template="plotly_white", hovermode="x unified")

        # Return serialized JSON string prefixed for UI capture
        return f"PLOTLY_JSON:{fig.to_json()}"
    except Exception as e:
        return f"Failed to build figure: {str(e)}"


# TODO: Figure out a way to display plotly app as seen in jupyter notebook
@st.cache_resource
def _ensure_dash_server_running(cell_line_obj, port: int = 8050):
    """Starts the Dash app in a background daemon thread if not already running."""
    thread = threading.Thread(
        target=cell_line_obj.interactive_plot,
        kwargs={"port": port, "mode": "external"},
        daemon=True,
    )
    thread.start()
    return True


@CDPpy_agent.tool
def create_interactive_plotly_chart(ctx: RunContext[dict], port: int = 8050) -> str:
    """Creates an interactive Plotly chart for the processed cell culture data and renders it in the Streamlit app."""
    CL_fed_batch = ctx.deps.get("fed_batch_obj")

    # 1. Ensure the Dash server is spun up in background
    _ensure_dash_server_running(CL_fed_batch, port=port)

    # 2. Render the iframe inside the Streamlit chatbot UI
    st.components.v1.iframe(f"http://localhost:{port}", height=700, scrolling=True)

    # 3. Return confirmation message to the LLM
    return f"Interactive plot dashboard has been displayed in the UI on port {port}."


# Define reusable Literal types for strict parameter enforcement
ProfileType = Literal["vcc", "tcc", "ivcc", "cumulative", "growthRate"]
MethodType = Literal["line", "scatter"]


class GetCellProfilesArgs(BaseModel):
    profiles: List[ProfileType] = Field(
        ...,
        description=(
            "List of cell profile metrics to plot. Valid options include "
            "'vcc' (Viable Cell Concentration), 'tcc' (Total Cell Concentration), "
            "'ivcc' (Integral Viable Cell Concentration), 'cumulative' (Cumulative Cell Production), "
            "or 'growthRate' (Growth Rate)."
        ),
    )
    run_ids: List[str] = Field(
        ...,
        description="List of run IDs to filter by, or ['All'] to include all available runs.",
    )
    method: MethodType = Field(
        ...,
        description="The type of plot visualization to generate (e.g., 'line', 'scatter').",
    )
    cell_line: List[str] = Field(
        ...,
        description="List of cell line names to filter by, or ['All'] to include all cell lines.",
    )
    color: List[str] = Field(
        default_factory=lambda: ["blue"],
        description="List of color strings/column names for styling the plot traces.",
    )
    line: List[str] = Field(
        default_factory=lambda: ["solid"],
        description="List of line styles/column names (e.g., 'solid', 'dash') for the plot.",
    )
    symbol: List[str] = Field(
        default_factory=lambda: ["circle"],
        description="List of marker symbols/column names (e.g., 'circle', 'square') for data points.",
    )
    legend: bool = Field(
        default=True,
        description="Whether to display the legend on the generated chart.",
    )
    x_axis: str = Field(
        default="Run Time (day)", description="Label text for the x-axis."
    )
    viability: bool = Field(
        default=True,
        description="Whether to overlay viability (%) data on a secondary y-axis (applicable when profile includes 'vcc').",
    )

    class Config:
        title = "GetCellProfilesArgs"
        description = "Schema for function arguments to plot cell profiles (VCC, TCC, IVCC, etc.)."


@CDPpy_agent.tool
def get_cell_profiles(
    ctx: RunContext[dict],
    profiles: list[str],
    run_ids: list[str],
    method: str,
    cell_line: list[str],
    color: str = "Cell Line",
    line: str = "ID",
    symbol: str = "ID",
    legend: bool = True,
    x_axis: str = "Run Time (day)",
    viability: bool = True,
) -> str:
    """Plots cell profile metrics (e.g., VCC, TCC, growth rate) for specified runs.

    Generates interactive Plotly charts based on processed cell culture data
    stored in session state or context dependencies. This tool MUST be called
    after `process_cell_line_data` has been executed.

    Args:
        ctx (RunContext[dict]): Pydantic run context supplied automatically.
        profiles (list[str]): List of profile metrics to plot. Valid choices include:
            'vcc', 'tcc', 'ivcc', 'cumulative', 'growthRate'.
        run_ids (list[str]): List of run IDs to include, or ['All'] to plot all runs.
        method (str): Plotting method (e.g., 'line', 'scatter').
        cell_line (list[str]): List of cell line names to filter by, or ['All'].
        color (str, optional): Name of the DataFrame column to group trace colors by.
            Typically 'Cell Line' or 'ID'. Defaults to "Cell Line".
        line (str, optional): Name of the DataFrame column to group line dash styles by.
            Typically 'Cell Line' or 'ID'. Defaults to "ID".
        symbol (str, optional): Name of the DataFrame column to group marker symbols by.
            Typically 'Cell Line' or 'ID'. Defaults to "ID".
        legend (bool, optional): Whether to display the plot legend. Defaults to True.
        x_axis (str, optional): Label for the x-axis (e.g., "Run Time (day)", "Run Time (hr)").
            Defaults to "Run Time (day)".
        viability (bool, optional): Whether to display secondary viability (%) axis on VCC plots. Defaults to True.

    Returns:
        str: JSON string of the Plotly figure formatted as 'PLOTLY_JSON:<json>', or an error message string.
    """

    try:
        CL_fed_batch = st.session_state.get("fed_batch_obj")
    except:
        try:
            CL_fed_batch = ctx.deps.get("fed_batch_obj")
        except Exception as e:
            return f"Error accessing processed cell line object: {str(e)}"
    if not CL_fed_batch:
        return "Failed: No fed_batch_obj found in session dependencies."

    if not (run_ids and profiles and cell_line):
        return None
    # Cleaning IDs
    for cl in cell_line:
        run_ids = [id.replace(f"{cl}-", "") for id in run_ids]

    # print(cell_line, run_ids, profiles)

    # Get data
    cell_data = CL_fed_batch.get_cell_data()

    # Get data
    conc_df = cell_data["conc"]
    ivcc_df = cell_data["integral"]
    cumulative_conc_df = cell_data["cumulative"]
    growth_rate_df = cell_data["growth_rate"]

    figures = {}
    if "vcc" in profiles:
        # Filtering by Cell Line and ID
        conc_filtered_by_cl = filter_data(conc_df, "Cell Line", cell_line)
        # if 'All' is not selected
        if "All" not in run_ids:
            conc_filtered_by_id = filter_data(conc_filtered_by_cl, "ID", run_ids)
        else:
            conc_filtered_by_id = conc_filtered_by_cl

        # Filtering by VCD
        vcc_mask = conc_filtered_by_id["state"] == "VCD"
        df = conc_filtered_by_id[vcc_mask]
        fig = px.line(
            df,
            x=x_axis,
            y="value",
            title="Viable Cell Concentration",
            color=color,
            line_dash=line,
            symbol=symbol,
        )
        fig.update_yaxes(title_text=f"VCC {df['unit'].iat[0]}")

        if viability:
            # Filtering by Viability
            viab_mask = conc_filtered_by_id["state"] == "Viability"
            df2 = conc_filtered_by_id[viab_mask]
            fig2 = px.line(
                df2,
                x=x_axis,
                y="value",
                color=color,
                line_dash=line,
                symbol=symbol,
                color_discrete_sequence=px.colors.qualitative.Pastel1,
            )
            fig2.update_traces(yaxis="y2")
            for fig_data in fig2.data:
                fig.add_trace(fig_data)

            fig.update_layout(legend_x=1.15, legend_y=1)
            fig.update_layout(
                yaxis2={
                    "side": "right",
                    "title": "Viability (%)",
                    "overlaying": "y",
                }
            )

        # figures['figure1'] = fig

    elif "tcc" in profiles:
        # Filtering by Cell Line and ID
        conc_filtered_by_cl = filter_data(conc_df, "Cell Line", cell_line)
        # if 'All' is not selected
        if "All" not in run_ids:
            conc_filtered_by_id = filter_data(conc_filtered_by_cl, "ID", run_ids)
        else:
            conc_filtered_by_id = conc_filtered_by_cl

        # Filtering by TCD
        tcc_mask = conc_filtered_by_id["state"] == "TCD"
        df = conc_filtered_by_id[tcc_mask]

        fig = px.line(
            df,
            x=x_axis,
            y="value",
            title="Total Cell Concentration",
            color=color,
            line_dash=line,
            symbol=symbol,
        )
        fig.update_yaxes(title_text=f"TCC {df['unit'].iat[0]}")
        # figures['figure2'] = fig

    elif "ivcc" in profiles:
        # Filtering by Cell Line and ID
        ivcc_filtered_by_cl = filter_data(ivcc_df, "Cell Line", cell_line)
        # if 'All' is not selected
        if "All" not in run_ids:
            ivcc_filtered_by_id = filter_data(ivcc_filtered_by_cl, "ID", run_ids)
        else:
            ivcc_filtered_by_id = ivcc_filtered_by_cl

        fig = px.line(
            ivcc_filtered_by_id,
            x=x_axis,
            y="value",
            title="Integral Viable Cell Concentration",
            color=color,
            line_dash=line,
            symbol=symbol,
        )
        fig.update_yaxes(title_text=f"IVCC {ivcc_filtered_by_id['unit'].iat[0]}")
        # figures['figure3'] = fig

    elif "cumulative" in profiles:
        # Filtering by Cell Line and ID
        cumulative_filtered_by_cl = filter_data(
            cumulative_conc_df, "Cell Line", cell_line
        )
        # if 'All' is not selected
        if "All" not in run_ids:
            cumulative_filtered_by_id = filter_data(
                cumulative_filtered_by_cl, "ID", run_ids
            )
        else:
            cumulative_filtered_by_id = cumulative_filtered_by_cl

        fig = px.line(
            cumulative_filtered_by_id,
            x=x_axis,
            y="value",
            title="Cumulative Cell Production",
            color=color,
            line_dash=line,
            symbol=symbol,
        )
        fig.update_yaxes(
            title_text=f"Cumulative Cell Production {cumulative_filtered_by_id['unit'].iat[0]}"
        )
        # figures['figure4'] = fig

    elif "growthRate" in profiles:
        # Filtering by Cell Line and ID
        growth_rate_filtered_by_cl = filter_data(growth_rate_df, "Cell Line", cell_line)
        # if 'All' is not selected
        if "All" not in run_ids:
            growth_rate_filtered_by_id = filter_data(
                growth_rate_filtered_by_cl, "ID", run_ids
            )
        else:
            growth_rate_filtered_by_id = growth_rate_filtered_by_cl

        fig = px.line(
            growth_rate_filtered_by_id,
            x=x_axis,
            y="value",
            title="Growth Rate",
            color=color,
            line_dash=line,
            symbol=symbol,
        )
        fig.update_yaxes(
            title_text=f"Growth Rate {growth_rate_filtered_by_id['unit'].iat[0]}"
        )
        # figures['figure5'] = fig

    else:
        return "No valid profiles processed."

    if legend:
        fig.update_layout(showlegend=True, legend_y=1)
    else:
        fig.update_layout(showlegend=False)

    return f"PLOTLY_JSON:{fig.to_json()}"


@CDPpy_agent.tool
def get_metabolite_profiles(
    ctx: RunContext[dict],
    profiles: list[str],
    run_ids: list[str],
    species: list[str],
    cell_line: list[str],
    method: list[str] | None = None,
    color: str = "Cell Line",
    line: str = "ID",
    symbol: str = "ID",
    legend: bool = True,
    x_axis: str = "Run Time (day)",
) -> str:
    """Displays metabolite profile plots (e.g., concentration, cumulative, specific rate) for specified runs.

    Generates interactive Plotly charts based on processed metabolite data stored in
    session state or context dependencies. This tool MUST be called after
    `process_cell_line_data` has been executed.

    Args:
        ctx (RunContext[dict]): Pydantic run context supplied automatically.
        profiles (list[str]): List of metabolite profile metrics to plot. Valid choices include:
            'concentration', 'cumulative', 'spRate'.
        run_ids (list[str]): List of run IDs to filter by, or ['All'] to include all runs.
        species (list[str]): List of metabolite species to include (e.g., ['Glucose', 'Lactate', 'Glutamine']).
        cell_line (list[str]): List of cell line names to filter by, or ['All'].
        method (list[str], optional): Calculation methods to filter data by (e.g., ['twoPoint'], ['polynomial']),
            primarily required when 'spRate' is included in profiles. Defaults to None.
        color (str, optional): Name of the DataFrame column to group trace colors by.
            Typically 'Cell Line' or 'ID'. Defaults to "Cell Line".
        line (str, optional): Name of the DataFrame column to group line dash styles by.
            Typically 'Cell Line' or 'ID'. Defaults to "ID".
        symbol (str, optional): Name of the DataFrame column to group marker symbols by.
            Typically 'Cell Line' or 'ID'. Defaults to "ID".
        legend (bool, optional): Whether to display the plot legend. Defaults to True.
        x_axis (str, optional): Label for the x-axis (e.g., "Run Time (day)", "Run Time (hr)").
            Defaults to "Run Time (day)".

    Returns:
        str: JSON string of the Plotly figure formatted as 'PLOTLY_JSON:<json>', or an error message string.
    """
    try:
        CL_fed_batch = st.session_state.get("fed_batch_obj")
    except:
        try:
            CL_fed_batch = ctx.deps.get("fed_batch_obj")
        except Exception as e:
            return f"Error accessing processed cell line object: {str(e)}"
    if not CL_fed_batch:
        return "Failed: No fed_batch_obj found in session dependencies."
    if not (run_ids and species and profiles and cell_line):
        return None

    # Cleaning IDs
    for cl in cell_line:
        run_ids = [id.replace(f"{cl}-", "") for id in run_ids]

    data = CL_fed_batch.get_metabolite_data()

    # Filtering data
    conc_df = data["conc"]
    cumulative_conc_df = data["cumulative"]
    sp_rate_df = data["sp_rate"]

    # Filter data by species, Cell Line and ID
    conc_df = filter_data(conc_df, "species", species)
    conc_df = filter_data(conc_df, "Cell Line", cell_line)
    if "All" not in run_ids:
        conc_df = filter_data(conc_df, "ID", run_ids)
    cumulative_conc_df = filter_data(cumulative_conc_df, "species", species)
    cumulative_conc_df = filter_data(cumulative_conc_df, "Cell Line", cell_line)
    if "All" not in run_ids:
        cumulative_conc_df = filter_data(cumulative_conc_df, "ID", run_ids)
    sp_rate_df = filter_data(sp_rate_df, "species", species)
    sp_rate_df = filter_data(sp_rate_df, "Cell Line", cell_line)
    if "All" not in run_ids:
        sp_rate_df = filter_data(sp_rate_df, "ID", run_ids)

    # Creating figures
    figures = {}
    if "concentration" in profiles:
        fig = create_figure(
            conc_df, x_axis, "line", True, "Concentration", color, line, symbol, legend
        )
        fig = rename_yaxis(conc_df, fig, "concentration")
        # figures['figure1'] = fig

    elif "cumulative" in profiles:
        data1 = filter_data(cumulative_conc_df, "method", ["twoPoint"])
        data2 = filter_data(cumulative_conc_df, "method", ["polynomial"])

        fig1 = create_figure(
            data1,
            x_axis,
            "scatter",
            False,
            "Cumulative Consumption/Production",
            color,
            line,
            symbol,
            legend,
        )
        fig2 = create_figure(
            data2,
            x_axis,
            "line",
            False,
            "Cumulative Concentration",
            color,
            line,
            None,
            legend,
        )
        for fig_data in fig2.data:
            fig1.add_trace(fig_data)
        fig = rename_yaxis(data2, fig1, "cumulative")
        fig = rename_yaxis(data1, fig1, "cumulative")
        # figures['figure2'] = fig

    elif "spRate" in profiles and method:
        data = filter_data(sp_rate_df, "method", method)
        fig = create_figure(
            data, x_axis, "line", True, "Specific Rate", color, line, symbol, legend
        )
        fig = rename_yaxis(data, fig, "spRate")
        # figures['figure3'] = fig

    else:
        return "No valid profiles processed."

    return f"PLOTLY_JSON:{fig.to_json()}"


def create_figure(df, x, kind, makers, title, color, line_dash, symbol, legend):
    """Create a figure of plotly.express"""
    if kind == "line":
        fig = px.line(
            df,
            x=x,
            y="value",
            title=title,
            facet_row="species",
            markers=makers,
            color=color,
            line_dash=line_dash,
            symbol=symbol,
        )

    elif kind == "scatter":
        fig = px.scatter(
            df,
            x=x,
            y="value",
            title=title,
            facet_row="species",
            color=color,
            symbol=symbol,
        )

    fig.update_yaxes(matches=None)
    fig.for_each_annotation(lambda a: a.update(visible=False))

    spc_list = df["species"].unique()
    height_per_row = 500
    fig.update_layout(height=height_per_row * len(spc_list), width=800)

    if legend:
        fig.update_layout(showlegend=True, legend_x=1, legend_y=1)
    else:
        fig.update_layout(showlegend=False)
    return fig


def rename_yaxis(df, fig, profile):
    """Rename y-axis nanme."""
    spc_list = df["species"].unique()
    yaxis_titles = {}
    for name in spc_list:
        mask = df["species"] == name
        unit = df[mask]["unit"].iat[0]

        if profile == "cumulative":
            state = df[mask]["state"].iat[0]
            yaxis_titles[name] = f"Cumulative {name} {state} {unit}"
        elif profile == "spRate":
            yaxis_titles[name] = f"q{name} {unit}"
        else:
            yaxis_titles[name] = f"{name} {unit}"

    for i, annotation in enumerate(fig.layout.annotations):
        yaxis = "yaxis" + str(i + 1)
        fig["layout"][yaxis]["title"]["text"] = yaxis_titles[
            annotation.text.split("=")[-1]
        ]
    return fig
