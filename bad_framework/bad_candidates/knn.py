"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from sklearn.neighbors import NearestNeighbors


class KNN:
    """Implements the KNN outlier detection method proposed in

    Ramaswamy, Sridhar, Rajeev Rastogi, and Kyuseok Shim.
    "Efficient algorithms for mining outliers from large data sets."
    ACM SIGMOD Record. Vol. 29. No. 2. ACM, 2000.

    Parameters:
    - k: (int) number of neighbors to consider (defaults to 10). Must
    be smaller than the data set size.
    - seed: (int) random number generator seed.
    """

    def __init__(self, **kwargs):
        param_k = int(kwargs.get("k", 10))
        if param_k < 1:
            raise ValueError(
                "invalid parameter value. k must be positive: k={}".format(param_k)
            )
        self.k = param_k
        self._model = None

    def fit(self, train_data):
        self._model = NearestNeighbors(n_neighbors=self.k, algorithm="kd_tree")
        self._model.fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")

        element = element.reshape(1, -1)
        neighbor_distances, _ = self._model.kneighbors(
            element
        )  # neighbor_distances has shape (1, k)
        knn_distance = neighbor_distances[0][-1]
        return knn_distance
