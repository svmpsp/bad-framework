import numpy as np
from pyod.models.loci import LOCI as Loci


class LOCI:
    """Implements the Local Outlier Correlation Integral (LOCI) method proposed in

    TODO: add documentation

    ???

    The method works by ...

    Parameters:
    - alpha: (float) local neighborhood selection parameter (defaults to 0.5).
    - k: (int) outlier cutoff threshold (defaults to 3).
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the pyod library
    (https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.feature_bagging)  # noqa 501
    """

    def __init__(self, **kwargs):
        self.alpha = float(kwargs.get("alpha", 0.5))
        self.k = int(kwargs.get("k", 3))
        self.seed = int(kwargs["seed"])

    def fit(self, train_data):
        raise NotImplementedError()

    def score(self, element):
        print(np)
        print(Loci)
        raise NotImplementedError()

    # def score(self, data_matrix):
    #     loci_model = Loci(alpha=self.alpha, k=self.k,).fit(data_matrix)
    #     scores = loci_model.decision_scores_.reshape((data_matrix.shape[0], 1))
    #     return np.concatenate((data_matrix, scores), axis=1,)
