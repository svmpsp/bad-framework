"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import numpy as np


class Dummy:
    """Random anomaly detector. Assigns score 1.0 (a.k.a anomalous) to data elements at
    random with probability p.

    Parameters:
    - p: (float) probability of classifying an element as
    anomalous (must be between 0.0 and 1.0).
    - seed: (int) random number generator seed.
    """

    def __init__(self, **kwargs):
        param_p = float(kwargs.get("p", 0.5))
        if not 0.0 <= param_p <= 1.0:
            raise ValueError(
                "invalid parameter value. p must be between 0.0 and 1.0: p={}".format(
                    param_p
                )
            )

        self.p = param_p
        self.seed = int(kwargs.get("seed", 1234))
        np.random.seed(self.seed)

    def fit(self, train_data):
        """No fitting required.

        :param train_data: (numpy.ndarray) training dataset (ignored).
        :return: (bad.Candidate) the trained model.
        """
        return self

    def score(self, element):
        """Classifies element as anomalous with probability p.

        :param element: (numpy.ndarray) data element as a row vector (ignored).
        :return: (float) anomaly score for element.
        """
        random_number = np.random.uniform()
        if random_number >= 1.0 - self.p:
            return 1.0
        return 0.0
