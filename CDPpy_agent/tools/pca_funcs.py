import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools

from numpy.ma.extras import average
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA as _PCA_for_variance
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression, Lasso
import plotly.express as px
from typing import List, Literal, Optional
from pydantic_ai import RunContext
from CDPpy_agent.agent.agent import CDPpy_agent
from pydantic import BaseModel, Field
import streamlit as st
import threading
import pandas as pd

@CDPpy_agent.tool
def pca_analysis(ctx: RunContext[dict], n_components = 3)-> str:
    """Performs PCA analysis on the dataset. The dataset is already flattened (i.e. pivoted by time) and normalized by feature.

    The function returns the explained variance from the specified number of PCA components.
    Additionally, the PCA projected dataset is stored in the streamlit session state.
    
    Args:
        n_components (int, optional): Number of PCA components for analysis. Defaults to 3.

    Returns:
        str: Returns string that tells you what the explained variance is.
    """
    try:
        process_param_data = st.session_state.get("ml_ready_dataset")
    except:
        try:
            process_param_data = ctx.deps.get("ml_ready_dataset")
        except Exception as e:
            return f"Error accessing processed dataset: {str(e)}"
    # if not process_param_data:
    #     return "Failed: No ml_ready_dataset found in session dependencies."
    # n_components = 30
    scaler = StandardScaler() 
    norm_dataset = scaler.fit_transform(process_param_data)
    pca = PCA(n_components)
    pca.fit(norm_dataset)
    # print(pca.explained_variance_ratio_)
    # print("Explained variance = "+ str(sum(pca.explained_variance_ratio_)))
    projected_data = pca.transform(norm_dataset)
    # print("Shape of Original Dataset:", process_param_data.shape)
    # print("Shape after PCA:", projected_data.shape)
    st.session_state.pca_obj = pca
    st.session_state.projected_data = projected_data

    return f"Explained variance with {n_components} = {sum(pca.explained_variance_ratio_)}, component variance ratio by component {pca.explained_variance_ratio_}"

@CDPpy_agent.tool
def get_pca_loadings(ctx: RunContext[dict], pca_component: int = 1, top_n:int = 10)-> str:
    """_summary_

    Args:
        pca_component (int, optional): PC component to analyze loadings. Defaults to 1.
        top_n (int, optional): Top N loadings to show on plot.  Defaults to 10.

    Returns:
        str: Returns Plotly plot as JSON
    """
    try:
        pca = st.session_state.get("pca_obj")
        process_param_data = st.session_state.get("ml_ready_dataset")
    except:
        try:
            process_param_data = ctx.deps.get("ml_ready_dataset")
            pca = ctx.deps.get("pca_obj")
        except Exception as e:
            return f"Error accessing processed dataset: {str(e)}"
    # if not process_param_data:
    #     return "Failed: No ml_ready_dataset found in session dependencies."

    flattened_features = process_param_data.columns
    # 1. Compute loadings matrix
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    # n_features = 10
    # pca_component = 1
    # 2. Extract PC1 loadings into a DataFrame
    pc1_series = pd.Series(loadings[:, pca_component-1], index=flattened_features)


    # 3. Get top 10 features by magnitude and preserve original directions
    top10_idx = pc1_series.abs().nlargest(top_n).index
    top10_df = pc1_series.loc[top10_idx].reset_index()
    top10_df.columns = ['Feature', 'Loading']

    # Add direction label for distinct coloring and sort for plotting
    top10_df['Direction'] = np.where(top10_df['Loading'] >= 0, 'Positive', 'Negative')
    top10_df = top10_df.sort_values('Loading', ascending=True)

    # 4. Create Plotly figure
    fig = px.bar(
        top10_df,
        x='Loading',
        y='Feature',
        orientation='h',
        color='Direction',
        color_discrete_map={'Positive': '#1f77b4', 'Negative': '#ff7f0e'},
        title=f'Top {top_n} Features by PC{pca_component} Loading Magnitude',
        text_auto='.3f'  # Displays rounded loading values directly on the bars
    )

    # 5. Styling & layout adjustments
    fig.add_vline(x=0, line_dash='dash', line_color='black', line_width=1)

    fig.update_layout(
        xaxis_title='PC1 Loading',
        yaxis_title='Feature',
        showlegend=False,
        template='plotly_white',
        height=500,
        width=800
    )

    # fig.show()
#     plt.tight_layout()
# plt.show()

    return f"PLOTLY_JSON:{fig.to_json()}"