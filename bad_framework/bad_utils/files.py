"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import os
import re
import shutil
from tempfile import TemporaryDirectory

import bad_framework
from bad_framework.bad_utils.adt import conditional_casting


def get_candidate_filename(home_dir, suite_id):
    """Returns a suite-unique filename where to store a local candidate module.

    :param home_dir: (string) filename of the server home directory.
    :param suite_id: (string) suite identifier.
    :return: (string) filename of the candidate.
    """
    base_path = os.path.join(home_dir, suite_id)
    return os.path.join(base_path, "candidate.py")


def get_candidate_name(candidate_path):
    """Parses the candidate file and returns the name of the candidate class.

    :param candidate_path: (string) filename of the candidate file
    :return: (string) the candidate class name
    """
    if not candidate_path:
        raise ValueError("invalid candidate path {}".format(candidate_path))

    # Matches a python class definition and captures the class name.
    class_name_re = re.compile(r"^class[\s]+(\w+)[(:]")
    with open(candidate_path, "r") as candidate_file:
        for line in candidate_file.readlines():
            match = class_name_re.match(line)
            if match:
                # The first capture group is the candidate class name
                return str(match[1])
    raise ValueError("invalid candidate file {}".format(candidate_path))


def parse_param_line(line):
    """Parses a line of text specifying a parameter and returns the
    parsed fields.

    >>> parse_param_line("param_name  10")
    ['param_name', '10']
    >>> parse_param_line("")
    []
    >>> parse_param_line("param_name 1  10  1")
    ['param_name', '1', '10', '1']

    :param line: (string) line of text to parse
    :return: (list[string]) parameter specification fields.
    """
    if line:
        return re.split(r"\s+", line.strip())
    return []


def parse_value_parameter(fields):
    """

    >>> parse_value_parameter([])
    Traceback (most recent call last):
        ...
    ValueError: invalid value parameter fields
    >>> parse_value_parameter(["param_name", "10"])
    ('param_name', 10)
    >>> parse_value_parameter(["param_name", "string"])
    ('param_name', 'string')
    >>> parse_value_parameter(["param_name", "1.0"])
    ('param_name', 1.0)

    """
    if len(fields) != 2:
        raise ValueError("invalid value parameter fields")
    param_name = fields[0]
    value = conditional_casting(fields[1])
    return param_name, value


def parse_range_parameter(fields):
    """

    >>> parse_range_parameter(["param_name", "1.", "10.", "1."])
    ('param_name', 1.0, 10.0, 1.0)
    >>> parse_range_parameter(["param_name", "1", "10", "1"])
    ('param_name', 1, 10, 1)
    >>> parse_range_parameter(["param_name", "a", "b", "c"])
    Traceback (most recent call last):
        ...
    ValueError: invalid parameter range ...
    >>> parse_range_parameter(["param_name", "10.", "1.", "1."])
    Traceback (most recent call last):
        ...
    ValueError: invalid parameter range ...
    >>> parse_range_parameter(["param_name", "10", "1", "1"])
    Traceback (most recent call last):
        ...
    ValueError: invalid parameter range ...

    """
    if len(fields) != 4:
        raise ValueError("invalid range parameter fields")
    param_name = fields[0]
    start = conditional_casting(fields[1])
    end = conditional_casting(fields[2])
    step = conditional_casting(fields[3])
    param_type = start.__class__.__name__
    if type(start) == type(end) == type(step):
        if param_type == "float" or param_type == "int":
            if end >= start:
                return param_name, start, end, step
    raise ValueError(
        "invalid parameter range for {name}: <{start}, {end}, {step}> ".format(
            name=param_name,
            start=start,
            end=end,
            step=step,
        )
    )


def parse_requirements(requirements_filename):
    requirements = []
    with open(requirements_filename, "r") as requirements_file:
        for line in requirements_file:
            # Remove whitespaces, line and inline comments
            requirement = line.split("#")[0].strip()
            if requirement:
                requirements.append(requirement)
    requirements.sort()
    return requirements


def parse_parameters(parameters_filename):
    parameters = []
    with open(parameters_filename, "r") as parameters_file:
        for line in parameters_file:
            line = line.split("#")[0].strip()
            if line:
                fields = re.split(r"\s+", line)
                num_fields = len(fields)
                if num_fields == 2:
                    parameters.append(parse_value_parameter(fields))
                elif num_fields == 4:
                    parameters.append(parse_range_parameter(fields))
                else:
                    raise ValueError(
                        "invalid parameter specification at: {param_line}".format(
                            param_line=line
                        )
                    )
    return parameters


def get_include_dir():
    return os.path.join(os.path.dirname(bad_framework.__file__), "include")


def save_file(content, path):
    """Saves a byte-array to a binary file path.

    :param content: (bytes) content to write.
    :param path: (string) filepath to write to.
    :return: None
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, "wb+") as file:
        file.write(content)


def get_init_paths():
    """Returns the list of files that must be present in order to run BAD
    correctly.

    :return: (list[string]) list of paths

    >>> paths = get_init_paths(); paths.sort(); paths
    ['bad.conf', 'candidate_parameters.txt', 'candidate_requirements.txt', 'workers']
    """
    package_init_dir = os.path.join(get_include_dir(), "defaults")
    raw_files = os.listdir(package_init_dir)
    exclude_files = [
        "__pycache__",
    ]
    return [file for file in raw_files if file not in exclude_files]


def copy_files_to_bad_directory(dest_dir):
    """Initializes the directory with all required files to run the BAD framework.
    These include all files in the bad_framework/include/defaults directory.
    """

    # Copy all contents from the package to a temporary dir.
    src_dir_path = os.path.join(get_include_dir(), "defaults")

    with TemporaryDirectory() as temp_dir:
        dest_dir_path = os.path.join(temp_dir, "buffer_dir")
        shutil.copytree(src_dir_path, dest_dir_path)

        # Copy all contents of the temporary directory to the current directory
        for relative_path in get_init_paths():
            absolute_src = os.path.join(dest_dir_path, relative_path)
            if os.path.isfile(absolute_src):
                shutil.copy(absolute_src, dest_dir)
            elif os.path.isdir(absolute_src):
                shutil.copytree(absolute_src, os.path.join(dest_dir, relative_path))
            else:
                raise ValueError("neither a file nor a directory.")
