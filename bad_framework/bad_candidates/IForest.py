"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from sklearn.ensemble import IsolationForest


class IForest:
    """Implements the Isolation forest method proposed in:

    Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou. "Isolation forest."
    Eighth IEEE International Conference on Data Mining. IEEE, 2008.

    Parameters:
    - m: (int) number of trees (defaults to 10).
    - partition_size: (int) number of data elements to use for constructing
    each tree (defaults to 50). Must be smaller than or equal to the data set size.
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the scikit-learn library
    (see https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).  # noqa 501
    """

    def __init__(self, **kwargs):
        self.m = int(kwargs.get("m", 10))
        self.partition_size = int(kwargs.get("partition_size", 50))
        self.seed = int(kwargs["seed"])
        self._model = None

    def fit(self, train_data):
        self._model = IsolationForest(
            n_estimators=self.m,
            max_samples=self.partition_size,
            behaviour="new",
            contamination="auto",
            random_state=self.seed,
            n_jobs=1,
        ).fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element = element.reshape(1, -1)
        return -self._model.decision_function(element)[0]
