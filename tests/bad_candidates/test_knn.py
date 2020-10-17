import pytest
import numpy as np

from bad_framework.bad_candidates.knn import KNN


def test_knn_init():
    kwargs = {
        "k": 1,
    }
    cnd = KNN(**kwargs)
    assert cnd.k == 1


def test_knn_init_invalid_k():
    kwargs = {
        "k": -1,
    }
    with pytest.raises(ValueError):
        KNN(**kwargs)


def test_knn_init_default_args():
    cnd = KNN()
    assert cnd.k == 10


def test_knn_fit():
    train_data = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ]
    )
    cnd = KNN(k=1)
    fitted_cnd = cnd.fit(train_data)
    assert cnd == fitted_cnd


def test_knn_score_without_fit():
    test_element = np.array([1.0, 2.0, 3.0, 4.0])
    cnd = KNN(k=1)
    with pytest.raises(ValueError):
        cnd.score(test_element)


def test_knn_score():
    train_data = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
        ]
    )
    test_element = np.array([2.0, 0.0])
    cnd = KNN(k=1).fit(train_data)
    assert cnd.score(test_element) == 1.0
