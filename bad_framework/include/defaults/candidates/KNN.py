from sklearn.neighbors import NearestNeighbors


class KNN:
    """Implements the KNN outlier detection method proposed in

     Ramaswamy, Sridhar, Rajeev Rastogi, and Kyuseok Shim. "Efficient algorithms for mining outliers from large data sets."
     ACM Sigmod Record. Vol. 29. No. 2. ACM, 2000.

     This method assigns an outlier score to each data elements corresponding to the distance with its
     k-th nearest neighbor.

    Parameters:
    - k: (int) number of neighbors to consider (defaults to 10). Must be smaller than the data set size.
    - seed: (int) random number generator seed.
    """

    def __init__(self, **kwargs):
        self.k = int(kwargs.get("k", 10))
        self._model = None

    def fit(self, train_data):
        self._model = NearestNeighbors(n_neighbors=self.k, algorithm="kd_tree")
        self._model.fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        point_distances, _ = self._model.kneighbors(element)
        return point_distances[-1]
