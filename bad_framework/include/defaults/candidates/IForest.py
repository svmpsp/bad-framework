import numpy as np
from sklearn.ensemble import IsolationForest


class IForest:
    """Implements the Isolation forest method proposed in

    Liu, Fei Tony, Kai Ming Ting, and Zhi-Hua Zhou. "Isolation forest."
    Eighth IEEE International Conference on Data Mining. IEEE, 2008.

    The method identifies as outliers the data elements that can be easily isolated through random axis-parallel cuts
    in the data space. Intuitively, points in dense regions of space require a larger number of cuts to be isolated
    from the rest of the data sets. The IForest outlier score is a function of the number of cuts required to isolate
    a data element, i.e. the depth of the isolation tree. The algorithm generates several trees and aggregates the
    scores obtained from each component.

    Parameters:
    - m: (int) number of trees (defaults to 10).
    - partition_size: (int) number of data elements to use for constructing each tree (defaults to 50).
    Must be smaller than or equal to the data set size.
    - seed: (int) random number generator seed.
\
    This class wraps the implementation provided by the scikit-learn
    library (https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html).
    """

    def __init__(self, **kwargs):
        self.m = int(kwargs.get("m", 10))
        self.partition_size = int(kwargs.get("partition_size", 50))
        self.seed = int(kwargs["seed"])

    def score(self, data_matrix):
        iforest_model = IsolationForest(
            n_estimators=self.m,
            max_samples=self.partition_size,
            behaviour="new",
            contamination="auto",
            random_state=self.seed,
            n_jobs=1,
        ).fit(data_matrix)
        scores = (-iforest_model.score_samples(data_matrix)).reshape(
            (data_matrix.shape[0], 1)
        )
        return np.concatenate((data_matrix, scores), axis=1,)
