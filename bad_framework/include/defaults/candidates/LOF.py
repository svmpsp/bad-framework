import numpy as np
from sklearn.neighbors import LocalOutlierFactor


class LOF:
    """Implements the Local Outlier Factor (LOF) outlier detection method proposed in

    Breunig, Markus M., et al. "LOF: identifying density-based local outliers."
    ACM sigmod record 29.2 (2000): 93-104.

    This method assigns an outlier score to each data elements corresponding its LOF. LOF is computed as a function
    of the relative k-nearest-neighborhood density of each data element.

    Parameters:
    - k: (int) number of neighbors to consider (defaults to 10). Must be smaller than the data set size.
    - seed: (int) random number generator seed.

    This class wraps the implementation provided by the scikit-learn
    library (https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html).
    """

    def __init__(self, **kwargs):
        self.k = int(kwargs.get("k", 10))

    def score(self, data_matrix):

        lof_model = LocalOutlierFactor(
            n_neighbors=self.k, algorithm="kd_tree", contamination="auto",
        ).fit(data_matrix)
        scores = (-lof_model.negative_outlier_factor_).reshape(
            (data_matrix.shape[0], 1)
        )
        return np.concatenate((data_matrix, scores), axis=1,)
