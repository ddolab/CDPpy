from tools.data_handler import load_raw_dataset, build_process_tensor, standardize_process_data
from tools.pca_funcs import fit_pca, transform_pca, get_pca_loadings, get_pca_variance, prepare_pca_2d_projection_plot_data

TOOLS = {
    "load_raw_dataset": load_raw_dataset,
    "build_process_tensor": build_process_tensor,
    "standardize_process_data": standardize_process_data,

    "fit_pca": fit_pca,
    "transform_pca": transform_pca,
    "get_pca_loadings": get_pca_loadings,
    "get_pca_variance": get_pca_variance,

    "prepare_pca_2d_projection_plot_data": prepare_pca_2d_projection_plot_data,
}