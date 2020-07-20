import numpy as np

from bad_framework.bad_utils import (
    generate_experiments_settings,
    get_parameter_combinations,
    load_data_matrix,
)
from bad_framework.bad_utils.adt import (
    ExperimentSettings,
    RangeParameter,
    ValueParameter,
)


def test_generate_experiments_settings():
    dummy_datasets = [
        "dummy_data_1",
    ]
    dummy_parameters = {
        "a": ValueParameter(10),
        "b": RangeParameter(2, 6, 2),
    }
    expected_settings = [
        ExperimentSettings("dummy_data_1", "a=10;b=2"),
        ExperimentSettings("dummy_data_1", "a=10;b=4"),
        ExperimentSettings("dummy_data_1", "a=10;b=6"),
    ]
    assert expected_settings == list(
        generate_experiments_settings(dummy_datasets, dummy_parameters)
    )


def test_get_parameter_combinations():
    dummy_parameters = {
        "a": ValueParameter(10),
        "b": RangeParameter(2, 6, 2),
    }
    expected_combinations = [
        (10, 2),
        (10, 4),
        (10, 6),
    ]
    assert expected_combinations == list(get_parameter_combinations(dummy_parameters))


def test_load_data_matrix(tmp_path):
    dummy_data_content = "\n".join(
        [
            "@ RELATION 'Dummy BAD data'",
            "@ ATTRIBUTE 'id' integer",
            "@ ATTRIBUTE 'outlier' real",
            "@ ATTRIBUTE 'att1' real",
            "@ ATTRIBUTE 'att2' real",
            "@ ATTRIBUTE 'att3' real",
            "@ ATTRIBUTE 'att4' real",
            "",
            "@ DATA",
            "0, 0.0, 8.0, 66.0, 9.0, 100.0",
            "1, 1.0, 0.0, 57.0, 33.0, 76.0",
            "2, 0.0, 81.0, 80.0, 28.0, 87.0",
            "3, 1.0, 0.0, 67.0, 28.0, 94.0",
            "4, 0.0, 82.0, 62.0, 85.0, 100.0",
        ]
    )
    data_file = tmp_path / "dummy.arff"
    data_file.write_text(dummy_data_content)
    expected_matrix = np.array(
        [
            [0.0, 0.0, 8.0, 66.0, 9.0, 100.0],
            [1.0, 1.0, 0.0, 57.0, 33.0, 76.0],
            [2.0, 0.0, 81.0, 80.0, 28.0, 87.0],
            [3.0, 1.0, 0.0, 67.0, 28.0, 94.0],
            [4.0, 0.0, 82.0, 62.0, 85.0, 100.0],
        ]
    )
    assert expected_matrix.tolist() == load_data_matrix(data_file).tolist()
