"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import os

CANDIDATE_FILES = {
    "dummy": "Dummy.py",
    "fb": "FeatureBagging.py",
    "iforest": "IForest.py",
    "knn": "KNN.py",
    "loci": "LOCI.py",
    "lof": "LOF.py",
    "ocsvm": "OCSVM.py",
}

CANDIDATE_REQUIREMENTS = {
    "dummy": ["numpy"],
    "fb": ["pyod"],
    "iforest": ["scikit-learn"],
    "knn": ["scikit-learn"],
    "loci": ["pyod"],
    "lof": ["scikit-learn"],
    "ocsvm": ["pyod"],
}


def get_candidate_requirements(candidate_name):
    return CANDIDATE_REQUIREMENTS[candidate_name]


def get_default_candidate(candidate_name):
    """Returns the filename of one of the default candidate modules.

    :param candidate_name:
    :return:
    """
    candidate_dir = os.path.dirname(__file__)
    return os.path.join(candidate_dir, CANDIDATE_FILES[candidate_name])
