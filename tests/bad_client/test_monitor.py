import pytest

from bad_framework.bad_client.monitor import (
    get_count_by_status,
    initialize_status_cache,
    update_status_cache,
)


def test_get_count_by_status():
    test_cache = {
        "dummy_exp_1": "created",
        "dummy_exp_2": "scheduled",
        "dummy_exp_3": "scheduled",
    }
    assert 1 == get_count_by_status(test_cache, "created")
    assert 2 == get_count_by_status(test_cache, "scheduled")


def test_get_count_by_status_when_cache_is_none():
    with pytest.raises(ValueError):
        get_count_by_status(None, "created")


def test_get_count_by_status_with_invalid_status():
    with pytest.raises(ValueError):
        test_cache = {
            "dummy_exp_1": "created",
            "dummy_exp_2": "scheduled",
        }
        get_count_by_status(test_cache, "invalid_status")


def test_initialize_status_cache_with_none():
    with pytest.raises(ValueError):
        initialize_status_cache(None)


def test_initialize_status_cache():
    example_response = [
        {"id": "dummy_exp_1", "status": "running"},
        {"id": "dummy_exp_2", "status": "scheduled"},
    ]
    expected_cache = {
        "dummy_exp_1": "running",
        "dummy_exp_2": "scheduled",
    }
    assert expected_cache == initialize_status_cache(example_response)


def test_update_status_cache():
    test_cache = {
        "dummy_exp_1": "created",
        "dummy_exp_2": "scheduled",
    }
    test_experiments = [
        {"id": "dummy_exp_1", "status": "created"},
        {"id": "dummy_exp_2", "status": "running"},
    ]
    expected_cache = {
        "dummy_exp_1": "created",
        "dummy_exp_2": "running",
    }
    update_status_cache(test_experiments, test_cache)
    assert expected_cache == test_cache


def test_get_suite_experiments():
    # example_response = {
    #     "suite_id": "dummy_suite",
    #     "experiments": [
    #         {"id": "dummy_exp_1", "status": "dummy_status_1"},
    #         {"id": "dummy_exp_2", "status": "dummy_status_2"},
    #     ],
    # }
    pass
