import numpy as np


class Dummy:
    """Random anomaly detector. Classify data elements as anomalies with probability p.

    Parameters:
    - p: (float) probability of assigning the anomalous score. Must be between [0.0, 1.0].
    - seed: (int) random number generator seed.
    """

    def __init__(self, **kwargs):
        self.p = float(kwargs.get("p", 0.5))
        np.random.seed(int(kwargs["seed"]))

    def fit(self, train_data):
        return self

    def score(self, element):
        random_number = np.random.uniform()
        if random_number >= 1.0 - self.p:
            return 1.0
        return 0.0
