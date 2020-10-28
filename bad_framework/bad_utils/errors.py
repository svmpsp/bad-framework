"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""


class InvalidCandidateError(Exception):
    pass


class SchedulingError(Exception):
    pass


def get_error_message(reason):
    return get_response_message(500, {"error": reason})


def get_response_message(status, payload):
    return {
        "status": int(status),
        **payload,
    }
