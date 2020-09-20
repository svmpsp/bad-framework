"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import datetime
import os


def format_status_message(
    elapsed_seconds, experiments_num, completed_num, failed_num, percentage
):
    elapsed_minutes = elapsed_seconds // 60
    return "Elapsed time: {0}:{1}:{2} - experiments {3}{4}/{5} ({6}%)".format(
        str(elapsed_minutes // 60).zfill(2),
        str(elapsed_minutes % 60).zfill(2),
        str(elapsed_seconds % 60).zfill(2),
        completed_num,
        "" if failed_num == 0 else " ({0} failed)".format(failed_num),
        experiments_num,
        int(percentage * 100),
    )


def get_progress_bar(total_length, percentage, item="#", start="[", end="]"):
    """Builds a progress bar representation, drawn item as base symbol.
    The bar is delimited by start and end.

    The length of the progress bar is proportional to the percentage with respect to
    the total_length.

    :param total_length: (int) total length, representing 100%.
    :param percentage: (float) progress completion percentage, between 0.0 and 1.0.
    :param item: (string) character used to draw the bar.
    :param start: (string) start character for the bar.
    :param end: (string) end character for the bar.
    :return: (string) representing the progress bar.

    Examples:

    >>> get_progress_bar(10, 0.0)
    '[]'
    >>> get_progress_bar(10, 1.0)
    '[########]'
    >>> get_progress_bar(10, 1.0, item='$')
    '[$$$$$$$$]'
    >>> get_progress_bar(10, 0.5, start='E', end='X')
    'E###X'
    """
    bar_length = int(percentage * total_length) - 2
    return start + (item * bar_length) + end


def print_status_bar(start_ts, experiments_num, completed_num, failed_num):
    _, terminal_width = os.popen("stty size", "r").read().split()
    percentage = float(completed_num + failed_num) / experiments_num
    bar = get_progress_bar(int(terminal_width), percentage)
    elapsed_seconds = int((datetime.datetime.now() - start_ts).total_seconds())
    status_message = format_status_message(
        elapsed_seconds,
        experiments_num,
        completed_num,
        failed_num,
        percentage,
    )
    overhead = 4
    if len(status_message) + overhead >= len(bar):
        status_bar = "[ " + status_message + " ]"
    else:
        padded_message = "[ {} ".format(status_message)
        status_bar = padded_message + bar[len(padded_message) :]
    print(status_bar, end="\r", flush=True)
