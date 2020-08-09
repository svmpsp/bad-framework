from bad_framework.bad_utils.files import parse_requirements


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
