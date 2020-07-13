from bad_framework.bad_client.ui import format_status_message


def test_format_status_message():
    expected_message = "Elapsed time: 00:01:15 - experiments 88 (10 failed)/100 (98%)"
    actual_message = format_status_message(
        elapsed_seconds=75,
        experiments_num=100,
        completed_num=88,
        failed_num=10,
        percentage=0.98,
    )
    assert expected_message == actual_message
