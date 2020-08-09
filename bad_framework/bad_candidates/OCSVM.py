import numpy as np
from pyod.models.ocsvm import OCSVM as SVM


class OCSVM:
    """Implements the one-class Support Vector Machine method proposed in

    TODO: add documentation

    ???

    The method ...

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

    def fit(self, train_data):
        raise NotImplementedError()

    def score(self, element):
        print(np, SVM)
        raise NotImplementedError()

    # def score(self, data_matrix):
    #
    #     feature_bagging_model = SVM(
    #         kernel=self.kernel, nu=self.nu, tol=self.tolerance, max_iter=1000,
    #     ).fit(data_matrix)
    #
    #     scores = feature_bagging_model.decision_scores_.reshape(
    #         (data_matrix.shape[0], 1)
    #     )
    #     return np.concatenate((data_matrix, scores), axis=1,)
