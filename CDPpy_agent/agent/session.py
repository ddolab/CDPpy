class AgentSession:
    def __init__(self):
        self.state = {
            "raw_dataset": None,
            "dataset_loaded": False,
            "tensor": None,
            "scaled": None,
            "pca_model": None,
            "pca_n_components": None,
            "last_projection": None,
        }