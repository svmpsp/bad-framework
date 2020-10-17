from concurrent.futures import ThreadPoolExecutor, as_completed

from sklearn.neighbors import NearestNeighbors
import pandas as pd
import numpy as np


def _score_partition(k, partition_data):
    """Computes all KNN-outlier scores for elements in the input data.

    :param k:
    :param partition_data:
    :return:
    """
    partition_model = NearestNeighbors(n_neighbors=k, algorithm="kd_tree")
    partition_model.fit(partition_data)

    knn_distances, _ = partition_model.kneighbors()
    scores = np.array([nn_distances[-1] for nn_distances in knn_distances]).reshape(
        (partition_data.shape[0], 1)
    )
    return np.concatenate(
        (partition_data, scores),
        axis=1,
    )


class PartKNN:
    def __init__(self, **kwargs):
        param_k = int(kwargs.get("k", 10))
        param_partitions_num = int(kwargs.get("partitions_num", 10))

        if param_k < 1:
            raise ValueError(
                "invalid parameter value. k must be positive: k={}".format(param_k)
            )
        if param_partitions_num < 1:
            raise ValueError(
                "invalid parameter value. "
                "partitions_num must be positive: partitions_num={}".format(
                    param_partitions_num
                )
            )
        self.k = param_k
        self.partitions_num = param_partitions_num
        self._model = None

    def fit(self, train_data):
        """Fits and compute score partition wise. Save scores for score method.

        :param train_data:
        :return:
        """
        df = pd.DataFrame(train_data)
        data_size = df.shape[0]

        # Assign a partition to each element
        df["partition"] = np.random.randint(
            low=0, high=self.partitions_num, size=data_size
        )

        # Compute scores independently for each partition
        self._model = {}
        with ThreadPoolExecutor() as executor:
            futures = []
            for partition_index in range(self.partitions_num):
                partition_data = (
                    df[df["partition"] == partition_index]
                    .drop(columns=["partition"])
                    .to_numpy()
                )
                futures.append(
                    executor.submit(
                        _score_partition,
                        k=self.k,
                        partition_data=partition_data,
                    )
                )
            for future in as_completed(futures):
                try:
                    data_with_scores = future.result()
                    for row in data_with_scores:
                        element = tuple(row[:-1])
                        score = row[-1]
                        self._model[element] = score

                except RuntimeError:
                    print("Error computing partition scores")
                    raise RuntimeError
        return self

    def score(self, element):
        """Returns score corresponding to element.

        :param element:
        :return:
        """
        if not self._model:
            raise ValueError("invalid state. The model has not been trained.")
        element_key = tuple(element)
        return self._model.get(element_key, 0.0)


def main():

    rng_seed = 1234
    sample_size = 100
    sample_dims = 2
    partition_size = 5

    np.random.seed(rng_seed)

    sample_params = {
        "k": 2,
        "partition_size": partition_size,
        "seed": rng_seed,
    }

    sample_matrix = np.random.random_sample(size=(sample_size, sample_dims))

    print("Fitting the model...")
    model = PartKNN(**sample_params).fit(sample_matrix)
    print("Done.")

    print("Generating scores...")
    np.apply_along_axis(model.score, axis=1, arr=sample_matrix)
    print("Scores generated correctly.")


if __name__ == "__main__":
    main()
