class PartitionedLOF:
    """Implements a partitioned variant of the Local Outlier Factor (LOF) outlier detection method proposed in

    Breunig, Markus M., et al. "LOF: identifying density-based local outliers."
    ACM sigmod record 29.2 (2000): 93-104.

    This method assigns an outlier score to each data elements corresponding its LOF. LOF is computed as a function
    of the relative k-nearest-neighborhood density of each data element.

    In this variant, the LOF is computed with respect to a partition of the whole data set, where the partition
    size is defined as a fraction of the complete data set size.

    Parameters:
    - k: (int) number of neighbors to consider (defaults to 10). Must be smaller than the data set size.
    - partition_size: (int) integer number between 0 and 100. A partition_size of 100 corresponds to original LOF.

    This class wraps the implementation provided by the scikit-learn
    library (https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html).
    """

    def __init__(self, **kwargs):
        self.k = int(kwargs.get("k", 10))
        self.partition_size = int(kwargs.get("partition_size", 25))
        self.seed = int(kwargs["seed"])

    def score(self, data_matrix):
        raise NotImplementedError("Candidate PartitionedLOF needs refactoring!")

        # partitioned_data_matrix = self._partition_data_matrix(data_matrix)
        #
        # lof_model = LocalOutlierFactor(
        #     n_neighbors=self.k, algorithm="kd_tree", contamination="auto",
        # ).fit(data_matrix)
        # scores = (-lof_model.negative_outlier_factor_).reshape(
        #     (data_matrix.shape[0], 1)
        # )
        # return np.concatenate((data_matrix, scores), axis=1,)

    def _get_partition_id(self):
        pass

    def _partition_data_matrix(self, data_matrix):
        # TODO:
        #  - shuffling makes it impossible to return scores
        #  - improve BAD so that it is not a problem,
        #  - separate id,label and id/data???
        # shuffled_matrix = np.random.shuffle(data_matrix)
        # partition_id_column = self._get_partitions_id()
        #
        # # TODO: attach partition_id to data_matrix
        # partitioned_matrix = data_matrix
        #
        # return partitioned_matrix
        pass
