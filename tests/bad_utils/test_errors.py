from bad_framework.bad_utils.errors import get_error_message, get_response_message


def test_get_response_message():
    expected_object = {
        "status": 200,
        "msg": "hello",
    }
    assert expected_object == get_response_message(200, {"msg": "hello"})


def test_get_error_message():
    expected_error = {
        "status": 500,
        "error": "dummy error",
    }
    assert expected_error == get_error_message("dummy error")
