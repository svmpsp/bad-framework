"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from sklearn.neighbors import LocalOutlierFactor


class LOF:
    """Implements the Local Outlier Factor (LOF) outlier detection method proposed in

    Breunig, Markus M., et al. "LOF: identifying density-based local outliers."
    ACM sigmod record 29.2 (2000): 93-104.

    Parameters:
    - k: (int) number of neighbors to consider (defaults to 10). Must be smaller than
    the data set size.
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the scikit-learn library
    (https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html).  # noqa 501
    """

    def __init__(self, **kwargs):
        self.k = int(kwargs.get("k", 10))
        self._model = None

    def fit(self, train_data):
        self._model = LocalOutlierFactor(
            n_neighbors=self.k,
            algorithm="kd_tree",
            contamination="auto",
            novelty=True,
        ).fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element = element.reshape(1, -1)
        return -self._model.decision_function(element)[0]
