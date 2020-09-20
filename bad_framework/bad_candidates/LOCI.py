"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from pyod.models.loci import LOCI as Loci


class LOCI:
    """Implements the Local Outlier Correlation Integral (LOCI) method proposed in:

    Papadimitriou, Spiros, et al. "Loci: Fast outlier detection using
    the local correlation integral." Proceedings 19th international
    conference on data engineering (Cat. No. 03CH37405). IEEE, 2003.

    Parameters:
    - alpha: (float) local neighborhood selection parameter (defaults to 0.5).
    - k: (int) outlier cutoff threshold (defaults to 3).
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the PyOD library
    (see https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.loci).  # noqa 501
    """

    def __init__(self, **kwargs):
        self.alpha = float(kwargs.get("alpha", 0.5))
        self.k = int(kwargs.get("k", 3))
        self.seed = int(kwargs["seed"])
        self._model = None

    def fit(self, train_data):
        self._model = Loci(
            alpha=self.alpha,
            k=self.k,
        ).fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element = element.reshape(1, -1)
        return self._model.decision_function(element)[0]
