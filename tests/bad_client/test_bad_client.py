"""
Test module for the main bad-client module.

Global test fixtures are defined in 'bad-framework/tests/conftest.py'
"""
import pytest

from bad_framework.bad_client import parse_config_file, print_config


def test_parse_config_file_not_found():
    with pytest.raises(ValueError):
        parse_config_file("/file/not/found.conf")


def test_parse_empty_config_file(tmp_path):
    config_file = tmp_path / "empty.conf"
    config_file.write_text("")
    assert {} == parse_config_file(config_file.resolve())


def test_parse_config_file(tmp_path):
    config_file_content = "\n".join(
        ["dummy.path    /tmp/hello/world", "dummy.string  hello", "dummy.value   123"]
    )
    config_file = tmp_path / "test.conf"
    config_file.write_text(config_file_content)

    expected_config = {
        "dummy.path": "/tmp/hello/world",
        "dummy.string": "hello",
        "dummy.value": "123",
    }

    assert expected_config == parse_config_file(config_file.resolve())


def test_print_empty_config(bad_caplog):
    empty_config = {}
    expected_messages = ["Config = {", "}"]
    print_config(empty_config)
    assert bad_caplog.messages == expected_messages


def test_print_config(bad_caplog):
    import datetime

    dummy_date = datetime.datetime(1234, 5, 6, 7, 8, 9)

    empty_config = {"hello": "world", "now": dummy_date, "age": 42, "height": 178.9}
    expected_messages = [
        "Config = {",
        "  hello = 'world'",
        "  now = datetime.datetime(1234, 5, 6, 7, 8, 9)",
        "  age = 42",
        "  height = 178.9",
        "}",
    ]
    print_config(empty_config)
    assert bad_caplog.messages == expected_messages
