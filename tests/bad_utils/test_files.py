import pytest

from bad_framework.bad_utils.files import (
    get_candidate_filename,
    get_candidate_name,
    parse_param_line,
    parse_requirements,
    parse_value_parameter,
)


def test_get_candidate_filename():
    assert "dummy_home/dir/suit1234/candidate.py" == get_candidate_filename(
        "dummy_home/dir",
        "suit1234",
    )


def test_get_candidate_name(tmp_path):
    candidate_file_contents = "\n".join(
        [
            "import numpy as np",
            "class TestCandidate:",
            "    def __init__(self, kwargs):",
            "        pass",
            "",
        ]
    )
    candidate_file = tmp_path / "candidate.py"
    candidate_file.write_text(candidate_file_contents)
    assert "TestCandidate" == get_candidate_name(candidate_file)


def test_get_candidate_name_with_no_path():
    with pytest.raises(ValueError):
        get_candidate_name("")


def test_get_candidate_name_with_multiple_classes(tmp_path):
    candidate_file_contents = "\n".join(
        [
            "import numpy as np",
            "class FirstClass:",
            "    def __init__(self, kwargs):",
            "        pass",
            "",
            "class SecondClass:",
            "    def __init__(self, kwargs):",
            "        pass",
        ]
    )
    candidate_file = tmp_path / "candidate.py"
    candidate_file.write_text(candidate_file_contents)
    assert "FirstClass" == get_candidate_name(candidate_file)


def test_get_candidate_name_with_no_classes(tmp_path):
    candidate_file_contents = "\n".join(
        [
            "import numpy as np",
            "def dummy_method():",
            "    pass",
        ]
    )
    candidate_file = tmp_path / "candidate.py"
    candidate_file.write_text(candidate_file_contents)

    with pytest.raises(ValueError):
        get_candidate_name(candidate_file)


def test_parse_param_line():
    assert ["param_name", "10", "100", "10"] == parse_param_line(
        "param_name  10  100  10"
    )


def test_parse_param_line_with_empty_line():
    assert [] == parse_param_line("")


def test_parse_value_parameter():
    expected_output = ("param_name", 100)
    assert expected_output == parse_value_parameter(["param_name", "100"])


def test_parse_value_parameter_with_empty_fields():
    with pytest.raises(ValueError):
        parse_value_parameter([])


def test_parse_requirements(tmp_path):
    dummy_requirements = "\n".join(
        [
            "# This is a comment",
            "versioned-requirement-with-spaces >= 1.2.3",
            "versioned-requirement==4.5.6",
            "naked-requirement",
            "requirement-with-comment  # Dummy comment",
            "",
        ]
    )
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text(dummy_requirements)
    expected_requirements = [
        "naked-requirement",
        "requirement-with-comment",
        "versioned-requirement-with-spaces >= 1.2.3",
        "versioned-requirement==4.5.6",
    ]
    assert expected_requirements == parse_requirements(requirements_file)
