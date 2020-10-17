import pytest
import numpy as np

from bad_framework.bad_candidates.partknn import PartKNN


def test_partknn_init():
    kwargs = {"k": 1, "partitions_num": 12}
    cnd = PartKNN(**kwargs)
    assert cnd.k == 1 and cnd.partitions_num == 12


def test_partknn_init_invalid_k():
    kwargs = {
        "k": -1,
    }
    with pytest.raises(ValueError):
        PartKNN(**kwargs)


def test_partknn_init_invalid_partitions_num():
    kwargs = {
        "partitions_num": 0,
    }
    with pytest.raises(ValueError):
        PartKNN(**kwargs)


def test_partknn_init_default_args():
    cnd = PartKNN()
    assert cnd.k == 10 and cnd.partitions_num == 10


def test_partknn_fit():
    train_data = np.array(
        [
            [-1.0, -1.0],
            [-1.0, 0.0],
            [-1.0, 1.0],
            [0.0, -1.0],
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, -1.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ]
    )
    cnd = PartKNN(k=1, partitions_num=2)
    fitted_cnd = cnd.fit(train_data)
    assert cnd == fitted_cnd


def test_partknn_score_without_fit():
    test_element = np.array([1.0, 2.0, 3.0, 4.0])
    cnd = PartKNN()
    with pytest.raises(ValueError):
        cnd.score(test_element)


def test_partknn_score():
    train_data = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [2.0, 0.0],
        ]
    )
    test_element = np.array([2.0, 0.0])
    cnd = PartKNN(k=1, partitions_num=1).fit(train_data)
    assert cnd.score(test_element) == 1.0
