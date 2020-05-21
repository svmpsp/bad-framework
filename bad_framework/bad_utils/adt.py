"""Package for useful abstract data types (ADTs) for the BAD framework.

    CandidateSpec: represents the specification for a Candidate.
    CandidateSpec fields are:
    - name, candidate name.
    - candidate_path, path to Candidate module.
    - requirements_path, path to Candidate requirements file.
    - parameters_path, path to Candidate parameters file.

    >>> cs = CandidateSpec('TestCnd', 'TestCnd.py', 'test_cnd_requirements.txt', 'test_cnd_parameters.txt')
    >>> cs.name
    'TestCnd'
    >>> cs.candidate_path
    'TestCnd.py'
    >>> cs.requirements_path
    'test_cnd_requirements.txt'
    >>> cs.parameters_path
    'test_cnd_parameters.txt'

    ExperimentSettings: represents the specification of an experiment.
    ExperimentSettings fields are:
    - data, data set identifier
    - parameters, semicolon-separated hyperparameter string.

    >>> es = ExperimentSettings('test_data', 'a=1;b=2;c=3')
    >>> es.data
    'test_data'
    >>> es.parameters
    'a=1;b=2;c=3'

    ValueParameter: represents a parameter specified as a single value.
    ValueParameter fields are:
    - value, the value for the parameter.

    >>> vp = ValueParameter(100)
    >>> vp.value
    100

    RangeParameter: represents a parameter range of values.
    RangeParamete fields are:
    - start, the first value in the range.
    - end, the last value in the range.
    - step, the interval between elements in the range.

    >>> rp = RangeParameter(2, 10, 2)
    >>> rp.start
    2
    >>> rp.end
    10
    >>> rp.step
    2

    RunSpec: represents an assignment of an experiment to a worker.
    RunSpec fields are:
    - worker, the worker object.
    - experiment, the experiment object.

    >>> rs = RunSpec('test_worker', 'test_experiment')
    >>> rs.worker
    'test_worker'
    >>> rs.experiment
    'test_experiment'
"""
from collections import namedtuple

CandidateSpec = namedtuple(
    "CandidateSpec", "name candidate_path requirements_path parameters_path"
)
ExperimentSettings = namedtuple("ExperimentSettings", "dataset_name parameters")
ValueParameter = namedtuple("ValueParameter", "value")
RangeParameter = namedtuple("RangeParameter", "start end step")
RunSpec = namedtuple("RunSpec", "worker experiment")


class ExperimentStatus:
    CREATED = 0
    SCHEDULED = 1
    RUNNING = 2
    COMPLETED = 3
    FAILED = 4


def conditional_casting(str_value):
    """Tries to cast a string value to an integer or float.
    Falls back to the most general type if the casting fails.

    :param str_value: (string) value to be casted.
    :return: (int, float or string) the casted input value.

    >>> conditional_casting('1')
    1
    >>> conditional_casting('12a')
    '12a'
    >>> conditional_casting('12.0')
    12.0
    >>> conditional_casting('12a.0')
    '12a.0'
    """
    try:
        try:
            int_value = int(str_value)
            return int_value
        except ValueError:
            float_value = float(str_value)
            return float_value
    except ValueError:
        return str_value
