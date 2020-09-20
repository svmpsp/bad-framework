"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import itertools
import numpy as np
import sys
import subprocess

from . import adt


def generate_experiments_settings(datasets, parameter_settings):
    """Generates experiment settings for a particular experiment suite.
    The total number of experiment settings depends on the number of required data sets
    and on the parameter configurations.

    :param datasets: (list[str]) dataset names to be used for the experiments.
    :param parameter_settings: (dict) a map between parameter names
    and parameter values.
    :return: iterable of ExperimentSettings.
    """
    parameter_names = parameter_settings.keys()
    parameter_strings = []
    for parameter_values in get_parameter_combinations(parameter_settings):
        parameter_dict = dict(
            (name, value) for name, value in zip(parameter_names, parameter_values)
        )
        parameter_strings.append(get_parameter_string(parameter_dict))
    for combination in itertools.product(datasets, parameter_strings):
        yield adt.ExperimentSettings(
            dataset_name=combination[0],
            parameters=combination[1],
        )


def get_parameter_combinations(parameters):
    """Takes a dictionary of parameters and returns all possible parameter combinations.

    :param parameters: (dict) dictionary name -> ValueParameter or RangeParameter.
    :return: (iterator) N-tuple iterator corresponding to parameter combinations.
    N is the number of items in parameters.
    """
    distinct_values = []
    for param_name, param in parameters.items():
        param_type = param.__class__
        if param_type == adt.ValueParameter:
            distinct_values.append([param.value])
        elif param_type == adt.RangeParameter:
            value_range = [
                boxed_value.item()
                for boxed_value in np.arange(
                    start=param.start, stop=param.end + param.step, step=param.step
                )
            ]
            distinct_values.append(value_range)
        else:
            raise ValueError("invalid parameter type '{}'".format(param_type))
    # Generate all parameters combinations
    return itertools.product(*distinct_values)


def get_parameter_string(parameters):
    """Converts a parameter dictionary into a parameter string.

    :param parameters: (dict) parameters dictionary.
    :return: (string) formatted parameter string.

    Examples:

    >>> get_parameter_string({"a": 10, "b": "hello"})
    'a=10;b=hello'
    >>> get_parameter_string({})
    ''
    """
    return ";".join(
        "{key}={value}".format(key=k, value=v) for k, v in parameters.items()
    )


def init_worker_environments(workers, suite_id, candidate_id, datasets):
    for worker in workers:
        message = {
            "master_address": worker.master_address,
            "suite_id": suite_id,
            "candidate_id": candidate_id,
            "datasets": [dataset.name for dataset in datasets],
        }
        worker.session.post_json("setup/", message)


def install_requirements(requirements):
    """Installs a requirements.txt file using the pip defined in the current interpreter.

    :param requirements: (list[string]) list of pip requirement specifiers.
    :return: None
    """
    subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])


def load_data_matrix(path):
    """Read a data file in ARFF format and returns
    the numpy matrix corresponding to the data.

    :param path: (string) path to data file.
    :return: (numpy.ndarray) data matrix
    """
    return np.loadtxt(path, dtype=float, comments=["#", "@"], delimiter=",")


def load_parameter_string(parameter_string):
    """Converts a parameter string into a dictionary parameter.
    Parameter values are represented as strings.

    :param parameter_string: (string) parameter string.
    :return: (dict) parameters dictionary.

    Examples:

    >>> load_parameter_string("a=10;b=hello")
    {'a': '10', 'b': 'hello'}
    >>> load_parameter_string("")
    {}
    """
    parameters_dict = {}
    if parameter_string:
        parameters = parameter_string.split(";")
        for key_value in parameters:
            k, v = key_value.split("=")
            parameters_dict[k] = v
    return parameters_dict
