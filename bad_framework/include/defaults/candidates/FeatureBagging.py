import numpy as np
from pyod.models.feature_bagging import FeatureBagging as FB


class FeatureBagging:
    """Implements the FeatureBagging method proposed in

    Lazarevic, Aleksandar, and Vipin Kumar. "Feature bagging for outlier detection."
    Proceedings of the eleventh ACM SIGKDD international conference on Knowledge discovery in data mining. ACM, 2005.

    The method works as an ensemble of weak detectors. The base detector is the
    Local Outlier Factor algorithm. FeatureBagging selects random subspaces within the full
    feature set and applies the base detector on each subspace. It then combines the resulting
    outlier scores using the combination function.

    Parameters:
    - combination: (string) either 'average' or 'max' (defaults to 'average').
    - m: (int) number of subspaces, i.e. weak detectors (defaults to 10).
    - max_features: (float) fraction of features to use for each subspace  (defaults to 1.0).
    Must be between [0.5 and 1.0].
    - k: (int) number of neighbors to use in the weak LOF classifiers (defaults to 10).
    - seed: (int) random number generator seed.
\
    This class wraps the implementation provided by the pyod
    library (https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.feature_bagging)
    """

    def __init__(self, **kwargs):
        self.combination = str(kwargs.get("combination", "average"))
        self.estimator_params = {"n_neighbors": int(kwargs.get("k", 10))}
        self.m = int(kwargs.get("m", 10))
        self.max_features = float(kwargs.get("max_features", 1.0))
        self.seed = int(kwargs["seed"])

    def score(self, data_matrix):

        feature_bagging_model = FB(
            n_estimators=self.m,
            max_features=self.max_features,
            random_state=self.seed,
            combination=self.combination,
            estimator_params=self.estimator_params,
        ).fit(data_matrix)

        scores = feature_bagging_model.decision_scores_.reshape(
            (data_matrix.shape[0], 1)
        )
        return np.concatenate((data_matrix, scores), axis=1,)
