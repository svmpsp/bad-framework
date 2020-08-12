"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from pyod.models.feature_bagging import FeatureBagging as FB


class FeatureBagging:
    """Implements the Feature Bagging (FB) method proposed in:

    Lazarevic, Aleksandar, and Vipin Kumar.
    "Feature bagging for outlier detection."
    Proceedings of the eleventh ACM SIGKDD international conference
    on Knowledge discovery in data mining. ACM, 2005.

    This class wraps the implementation provided by the pyod library
    (see https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.feature_bagging)  # noqa 501

    Parameters:
    :combination: (string) either 'average' or 'max' (defaults to 'average').
    :m: (int) number of subspaces, i.e. weak detectors (defaults to 10).
    :max_features: (float) fraction of features to use for each
    subspace (defaults to 1.0). Must be between [0.5 and 1.0].
    :k: (int) number of neighbors to use in the weak LOF classifiers (defaults to 10).
    :seed: (int) random number generator seed.
    """

    def __init__(self, **kwargs):
        self.combination = str(kwargs.get("combination", "average"))
        self.estimator_params = {"n_neighbors": int(kwargs.get("k", 10))}
        self.m = int(kwargs.get("m", 10))
        self.max_features = float(kwargs.get("max_features", 1.0))
        self.seed = int(kwargs["seed"])
        self._model = None

    def fit(self, train_data):
        self._model = FB(
            n_estimators=self.m,
            max_features=self.max_features,
            random_state=self.seed,
            combination=self.combination,
            estimator_params=self.estimator_params,
        ).fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element = element.reshape(1, -1)
        return self._model.decision_function(element)[0]
