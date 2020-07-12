from tempfile import TemporaryDirectory
import logging
import os
import re
import shutil

from .adt import conditional_casting, RangeParameter, ValueParameter
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


def get_candidate_file_paths(home_dir, suite_id):
    base_path = "{home_dir}/{suite_id}/".format(home_dir=home_dir, suite_id=suite_id)
    return {
        "candidate": base_path + "candidate.py",
        "parameters": base_path + "parameters.txt",
        "requirements": base_path + "requirements.txt",
    }


def load_parameters(parameter_file, suite):
    """Loads the parameter dictionary from a parameter file.

    The parameter file contains one parameter per line. Each parameter can be either a value parameter
    or a range parameter, with the following specifications.

    Value parameter:
    <param_name>  <param_value>

    Range parameter:
    <param_name>  <param_range_start>  <param_range_stop>  <param_range_step>

    NOTE: if the range cannot be divided into an integer number of steps the behavior is undefined.

    :param parameter_file: (string) path to parameter file.
    :param suite: (models.Suite) contains default values for required parameters.
    :return: (dict) parameter dictionary
    """
    parameters = {}
    with open(parameter_file, "r") as parameters_file:
        for line in parameters_file:
            if line.strip() and not line.startswith("#"):
                fields = re.split(r"\s+", line.strip())
                param_name = fields[0]
                num_fields = len(fields)
                if num_fields == 2:
                    value = conditional_casting(fields[1])
                    parameters[param_name] = ValueParameter(value=value)
                elif num_fields == 4:
                    start = conditional_casting(fields[1])
                    end = conditional_casting(fields[2])
                    step = conditional_casting(fields[3])
                    param_type = start.__class__.__name__
                    if type(start) == type(end) == type(step) and (
                        param_type == "float" or param_type == "int"
                    ):
                        parameters[param_name] = RangeParameter(
                            start=start, end=end, step=step,
                        )
                    else:
                        raise ValueError(
                            "invalid range parameter specification. Error on line: {param_line}".format(
                                param_line=line
                            )
                        )
                else:
                    raise ValueError(
                        "formatting error in parameters file. Error on line: {param_line}".format(
                            param_line=line
                        )
                    )
    # Add default values for required parameters
    if "seed" not in parameters:
        parameters["seed"] = ValueParameter(value=suite.seed)
    if "trainset_size" not in parameters:
        parameters["trainset_size"] = ValueParameter(value=suite.trainset_size)
    return parameters


def get_include_dir():
    return "{package_file}/include".format(
        package_file=os.path.dirname(bad_framework.__file__)
    )


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
    :return: (bool) True if the file exists and has the expected content, raises a ValueError otherwise.
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


def _get_init_paths():
    """Returns the list of files that must be present in order to run BAD
    correctly.

    :return: (list[string]) list of paths

    >>> paths = _get_init_paths(); paths.sort(); paths
    ['candidate_parameters.txt', 'candidate_requirements.txt', 'candidates', 'conf']
    """
    package_init_dir = "{include_dir}/defaults".format(include_dir=get_include_dir())
    return os.listdir(package_init_dir)


def delete_bad_files():
    """Deletes BAD files inside of the current directory.

    :return: None
    """
    cur_dir = os.getcwd()

    if not cur_dir:
        raise ValueError("invalid directory path {}".format(cur_dir))

    for path in _get_init_paths():
        absolute_path = os.path.join(cur_dir, path)
        try:
            if os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)
            else:
                os.remove(absolute_path)
        except FileNotFoundError as fnfe:
            log.debug("cannot remove file: %s", str(fnfe))


def is_directory_init(cur_dir):
    """Verifies if the given directory contains the files necessary to run the BAD framework.

    :param cur_dir: (string) path to current directory
    :return: (bool) True if the directory is already initialized, False otherwise.
    """
    paths_to_check = _get_init_paths()

    for path in paths_to_check:
        absolute_path = os.path.join(cur_dir, path)
        if not os.path.exists(absolute_path):
            return False
    return True


def init_working_directory(cur_dir):
    """Initializes the directory with all required files to run
    the BAD framework. These include all files in the bad_framework/include/defaults directory.
    """

    # Copy all contents from the package to a temporary dir.
    src_dir_path = "{include_dir}/defaults".format(include_dir=get_include_dir())

    with TemporaryDirectory() as temp_dir:
        dest_dir_path = os.path.join(temp_dir, "buffer_dir")
        log.debug("Copying all contents from %s to %s", src_dir_path, dest_dir_path)
        shutil.copytree(src_dir_path, dest_dir_path)

        # Copy all contents of the temporary directory to the current directory
        for relative_path in os.listdir(dest_dir_path):
            absolute_src = os.path.join(dest_dir_path, relative_path)
            if os.path.isfile(absolute_src):
                shutil.copy(absolute_src, cur_dir)
            elif os.path.isdir(absolute_src):
                shutil.copytree(absolute_src, os.path.join(cur_dir, relative_path))
            else:
                raise ValueError("neither a file nor a directory.")
