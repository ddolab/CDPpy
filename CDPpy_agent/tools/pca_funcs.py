from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt

def fit_pca(X, n_components, session_state=None):
    """
    Fits PCA and stores model in session state (if provided).
    """

    pca = PCA(n_components=n_components)
    pca.fit(X)

    result = {
        "model": pca,
        "explained_variance_ratio": pca.explained_variance_ratio_,
        "explained_variance_total": float(sum(pca.explained_variance_ratio_)),
        "n_components": n_components
    }

    # optional session persistence
    if session_state is not None:
        session_state["pca_model"] = pca
        session_state["pca_n_components"] = n_components

    return result

def transform_pca(X, pca_model=None, session_state=None):
    """
    Projects data into PCA space using stored or provided model.
    """

    if pca_model is None and session_state is not None:
        pca_model = session_state.get("pca_model")

    if pca_model is None:
        raise ValueError("No PCA model provided or found in session state.")

    projected = pca_model.transform(X)

    return {
        "projected_data": projected,
        "original_shape": X.shape,
        "projected_shape": projected.shape
    }

def get_pca_variance(pca_model=None, session_state=None):
    """
    Returns variance diagnostics for current PCA model.
    """

    if pca_model is None and session_state is not None:
        pca_model = session_state.get("pca_model")

    if pca_model is None:
        raise ValueError("No PCA model available.")

    return {
        "explained_variance_ratio": pca_model.explained_variance_ratio_,
        "total_explained_variance": float(sum(pca_model.explained_variance_ratio_))
    }

def get_pca_loadings(pca_model, feature_names):
    """
    Computes PCA loadings for each feature and component.

    Returns:
        DataFrame: rows = features, cols = PCs
    """

    # sklearn stores eigenvectors in components_
    # shape: (n_components, n_features)
    components = pca_model.components_

    # loadings: feature contribution magnitude
    # transpose -> (n_features, n_components)
    loadings = components.T

    loading_df = pd.DataFrame(
        loadings,
        index=feature_names,
        columns=[f"PC{i+1}" for i in range(components.shape[0])]
    )

    return loading_df

def rank_features_by_loading(loadings_df, pc="PC1", top_k=10):
    """
    Ranks features by absolute loading magnitude for a given PC.
    Returns a DataFrame with feature names and their loadings.
    """

    if pc not in loadings_df.columns:
        raise ValueError(f"{pc} not found in loadings")

    ranked = (
        loadings_df[pc]
        .abs()
        .sort_values(ascending=False)
        .head(top_k)
    )

    return pd.DataFrame({
        "feature": ranked.index,
        "loading": loadings_df.loc[ranked.index, pc],
        "abs_loading": ranked.values
    })


def plot_explained_variance_curve(pca_model):
    """
    Returns data structured for plotting explained variance curve.
    Returns:
        DataFrame with columns: PC, explained_variance, cumulative_variance
    """

    explained = pca_model.explained_variance_ratio_
    cumulative = np.cumsum(explained)

    df = pd.DataFrame({
        "PC": np.arange(1, len(explained) + 1),
        "explained_variance": explained,
        "cumulative_variance": cumulative
    })

    return df

def prepare_pca_2d_projection_plot_data(
    projected_data,
    titer_category,
    pca_model,
    max_components=None
) -> None:
    """
    Prepares all pairwise 2D PCA projections for visualization.
    """

    projected_data = np.array(projected_data)
    titer_category = np.array(titer_category)

    n_components = projected_data.shape[1]

    if max_components is not None:
        n_components = min(max_components, n_components)

    pairs = list(itertools.combinations(range(n_components), 2))

    fig, axs = plt.subplots(
        1,
        len(pairs),
        figsize=(5 * len(pairs), 5)
    )

    # handle single plot edge case
    if len(pairs) == 1:
        axs = [axs]

    top_mask = (titer_category == 1)
    mid_mask = (titer_category == 0)
    bot_mask = (titer_category == 2)

    for idx, (i, j) in enumerate(pairs):

        ax = axs[idx]

        ax.scatter(
            projected_data[top_mask, i],
            projected_data[top_mask, j],
            c="blue",
            marker=".",
            label="Top 20%"
        )

        ax.scatter(
            projected_data[mid_mask, i],
            projected_data[mid_mask, j],
            c="grey",
            marker=".",
            label="Middle 60%"
        )

        ax.scatter(
            projected_data[bot_mask, i],
            projected_data[bot_mask, j],
            c="red",
            marker=".",
            label="Bottom 20%"
        )

        ax.set_xlabel(
            f"PC{i+1} ({pca_model.explained_variance_ratio_[i]*100:.2f}%)"
        )
        ax.set_ylabel(
            f"PC{j+1} ({pca_model.explained_variance_ratio_[j]*100:.2f}%)"
        )

        ax.legend()

    fig.suptitle("PCA Projections")
    fig.tight_layout()

    plt.show()