import pytest


@pytest.fixture(scope="function")
def bad_caplog(caplog):
    """Uses the pytest log capturing fixture to capture the
    application's log messages up to the DEBUG level.

    :param caplog (pytest.logging.LogCaptureFixture): log capturing fixture
    :return: (pytest.logging.LogCaptureFixture): modified log capturing fixture
    """
    import logging

    caplog.set_level(level=logging.DEBUG, logger="bad.client")
    return caplog
