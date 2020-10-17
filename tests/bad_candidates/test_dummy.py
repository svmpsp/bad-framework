import numpy as np
import pytest

from bad_framework.bad_candidates.dummy import Dummy


def test_dummy_init():
    kwargs = {
        "p": 0.1,
        "seed": 42,
    }
    cnd = Dummy(**kwargs)
    assert cnd.p == 0.1 and cnd.seed == 42


def test_dummy_init_invalid_p():
    kwargs = {
        "p": 12.0,
    }
    with pytest.raises(ValueError):
        Dummy(**kwargs)


def test_dummy_init_default_args():
    cnd = Dummy()
    assert cnd.p == 0.5 and cnd.seed == 1234


def test_dummy_fit():
    train_data = None
    cnd = Dummy()
    fitted_cnd = cnd.fit(train_data)
    assert cnd == fitted_cnd


def test_dummy_score():
    test_element = np.array([1.0, 2.0, 3.0, 4.0])
    cnd = Dummy(p=1.0)
    assert cnd.score(test_element) == 1.0
