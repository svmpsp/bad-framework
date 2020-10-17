"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from pyod.models.ocsvm import OCSVM as SVM


class OCSVM:
    """Implements the one-class Support Vector Machine method proposed in:

    Schölkopf, Bernhard, et al. "Estimating the support of a
    high-dimensional distribution." Neural computation 13.7 (2001):
    1443-1471.

    Parameters:
    - kernel: (string) kernel function to use (defaults to
    'rbf'). It supports 'linear', 'poly', 'rbf', 'sigmoid',
    'precomputed' or a callable.
    - nu: (float) threshold on the number of training
    errors/support vectors to use (defaults to 0.5). Should be
    between (0.0, 1.0].
    - tolerance: (float) error tolerance for the solver (defaults to 1e-3).
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the pyod
    library (https://pyod.readthedocs.io/en/latest/pyod.models.html#module-pyod.models.ocsvm)  # noqa 501
    """

    def __init__(self, **kwargs):
        self.kernel = str(kwargs.get("kernel", "rbf"))
        self.nu = float(kwargs.get("nu", 0.5))
        self.tolerance = float(kwargs.get("tolerance", 1e-3))
        self.seed = int(kwargs["seed"])
        self._model = None

    def fit(self, train_data):
        self._model = SVM(
            kernel=self.kernel,
            nu=self.nu,
            tol=self.tolerance,
            max_iter=1000,
        ).fit(train_data)
        return self

    def score(self, element):
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element = element.reshape(1, -1)
        return self._model.decision_function(element)[0]
