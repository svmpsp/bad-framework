class InvalidCandidateError(Exception):
    pass


class SchedulingError(Exception):
    pass


def get_response_message(status, payload):
    return {
        "status": int(status),
        **payload,
    }


def get_error_message(reason):
    return get_response_message(500, {"error": reason})
