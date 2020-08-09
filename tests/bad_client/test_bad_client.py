"""
Test module for the main bad-client module.

Global test fixtures are defined in 'bad-framework/tests/conftest.py'
"""
import pytest
import sys

from bad_framework.bad_client import (
    add_settings,
    load_default_config,
    parse_arguments,
    parse_config_file,
    print_config,
)


def test_add_settings():
    dummy_config = {
        "dummy_one": 1,
        "dummy_two": 2,
    }
    new_settings = {
        "dummy_three": 3,
    }
    expected_config = {
        "dummy_one": 1,
        "dummy_two": 2,
        "dummy_three": 3,
    }
    assert expected_config == add_settings(dummy_config, new_settings)


def test_add_settings_to_empty_config():
    dummy_config = {}
    new_settings = {
        "dummy_one": 1,
    }
    expected_config = {
        "dummy_one": 1,
    }
    assert expected_config == add_settings(dummy_config, new_settings)


def test_add_settings_without_settings():
    dummy_config = {
        "dummy_one": 1,
    }
    new_settings = {}
    expected_config = {
        "dummy_one": 1,
    }
    assert expected_config == add_settings(dummy_config, new_settings)


def test_add_settings_does_not_overwrite():
    dummy_config = {
        "dummy_one": "old_value",
    }
    new_settings = {
        "dummy_one": "new_value",
    }
    expected_config = {
        "dummy_one": "old_value",
    }
    assert expected_config == add_settings(dummy_config, new_settings)


def test_load_default_config(tmp_path):
    import os

    config_file_content = "\n".join(
        ["dummy.path    /config/file/path", "dummy.string  hello", "dummy.value   123"]
    )
    os.chdir(tmp_path)
    bad_dir = tmp_path / ".bad/"
    bad_dir.mkdir()
    config_file = bad_dir / "bad.conf"
    config_file.write_text(config_file_content)

    initial_config = {
        "dummy.path": "original/path",
        "dummy.value": "456",
    }
    expected_config = {
        "dummy.path": "original/path",
        "dummy.string": "hello",
        "dummy.value": "456",
    }
    assert expected_config == load_default_config(initial_config)


def test_parse_arguments_without_arguments(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(sys, "argv", ["bad"])
        with pytest.raises(SystemExit):
            parse_arguments()


def test_parse_arguments_without_command(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(sys, "argv", ["bad", "-c", "./dummy_candidate.py"])
        with pytest.raises(SystemExit):
            parse_arguments()


def test_parse_arguments(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(sys, "argv", ["bad", "run", "-c", "./dummy_candidate.py"])
        expected_config = {
            "command": "run",
            "bad.candidate": "./dummy_candidate.py",
            "bad.debug": False,
            "bad.log.verbose": False,
        }
        assert expected_config == parse_arguments()


def test_parse_arguments_with_debug_flag(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(sys, "argv", ["bad", "run", "-D"])
        expected_config = {
            "command": "run",
            "bad.debug": True,
            "bad.log.verbose": False,
        }
        assert expected_config == parse_arguments()


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
