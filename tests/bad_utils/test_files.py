import pytest

from bad_framework.bad_utils.files import (
    get_candidate_filename,
    get_candidate_name,
    parse_parameters,
    parse_requirements,
    save_file,
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


def test_parse_parameters(tmp_path):
    parameters_file_contents = "\n".join(
        [
            "# This is a comment",
            "value_parameter  10",
            "range_parameter  1  10  1",
        ]
    )
    parameters_file = tmp_path / "requirements.txt"
    parameters_file.write_text(parameters_file_contents)

    expected_parameters = [
        ("value_parameter", 10),
        ("range_parameter", 1, 10, 1),
    ]

    assert expected_parameters == parse_parameters(parameters_file)


def test_parse_requirements(tmp_path):
    requirements_file_contents = "\n".join(
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
    requirements_file.write_text(requirements_file_contents)
    expected_requirements = [
        "naked-requirement",
        "requirement-with-comment",
        "versioned-requirement-with-spaces >= 1.2.3",
        "versioned-requirement==4.5.6",
    ]
    assert expected_requirements == parse_requirements(requirements_file)


def test_save_file(tmp_path):
    dummy_content = "hello world".encode("utf-8")
    test_file = tmp_path / "dummy_file"

    save_file(dummy_content, test_file)

    assert dummy_content == test_file.read_bytes()
