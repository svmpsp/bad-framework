from tempfile import TemporaryDirectory
import logging
import os
import re
import shutil

from .adt import conditional_casting
import bad_framework

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bad.client")


def get_candidate_name(candidate_path):
    """
    TODO:
     - add error checking (e.g. candidate_path is empty)

    :param candidate_path:
    :return:
    """
    # Matches a python class definition and captures the class name.
    class_name_re = re.compile(r"^class[\s]+(\w+)[(:]")
    candidate_name = None
    with open(candidate_path, "r") as candidate_file:
        for line in candidate_file.readlines():
            match = class_name_re.match(line)
            if match:
                # The first capture group is the class name
                candidate_name = str(match[1])
    return candidate_name


def get_candidate_filename(home_dir, suite_id):
    """Returns a suite-unique filename where to store a local candidate module.

    TODO: refactor, maybe get_local_candidate_filename?

    :param home_dir:
    :param suite_id:
    :return:
    """
    base_path = os.path.join(home_dir, suite_id)
    return os.path.join(base_path, "candidate.py")


def parse_param_line(line):
    """Parse a line of text specifying a parameter and returns the
    parsed fields.

    :param line: (string) line of text to parse
    :return: (list[string]) parameter specification fields.
    """
    return re.split(r"\s+", line.strip())


def parse_value_parameter(fields):
    param_name = fields[0]
    value = conditional_casting(fields[1])
    return param_name, value


def parse_range_parameter(fields):
    param_name = fields[0]
    start = conditional_casting(fields[1])
    end = conditional_casting(fields[2])
    step = conditional_casting(fields[3])
    param_type = start.__class__.__name__
    if type(start) == type(end) == type(step) and (
        param_type == "float" or param_type == "int"
    ):
        return param_name, start, end, step
    else:
        raise ValueError(
            "invalid parameter range for {name}: <{start}, {end}, {step}> ".format(
                name=param_name, start=start, end=end, step=step,
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


def file_exists_with_content(path, expected_content):
    """Checks that the file identified by path exists and that it contains
    the given content.

    :param path: (string) path to file to check.
    :param expected_content: (bytes) bytes representing the expected content of the file.
    :return: (bool) True if the file exists and has
    the expected content, raises a ValueError otherwise.
    """
    if not os.path.exists(os.path.dirname(path)):
        raise ValueError("file {} does not exist.".format(path))
    with open(path, "rb") as file:
        actual_content = file.read()
        print("Actual content is:", actual_content)
        if not actual_content == expected_content:
            raise ValueError(
                "file {} does not contain the expected content.".format(path)
            )
    return True


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
        "__init__.py",
        "__pycache__",
    ]
    return [file for file in raw_files if file not in exclude_files]


def delete_bad_files():
    """Deletes BAD files inside of the current directory.

    :return: None
    """
    cur_dir = os.getcwd()

    if not cur_dir:
        raise ValueError("invalid directory path {}".format(cur_dir))

    for path in get_init_paths():
        absolute_path = os.path.join(cur_dir, path)
        try:
            if os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)
            else:
                os.remove(absolute_path)
        except FileNotFoundError as fnfe:
            log.debug("cannot remove file: %s", str(fnfe))


def copy_files_to_bad_directory(dest_dir):
    """Initializes the directory with all required files to run the BAD framework.
    These include all files in the bad_framework/include/defaults directory.
    """

    # Copy all contents from the package to a temporary dir.
    src_dir_path = os.path.join(get_include_dir(), "defaults")

    with TemporaryDirectory() as temp_dir:
        dest_dir_path = os.path.join(temp_dir, "buffer_dir")
        log.debug("Copying all contents from %s to %s", src_dir_path, dest_dir_path)
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
