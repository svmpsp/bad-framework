"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
from uuid import uuid4
import datetime
import glob
import json
import logging
import os

from bad_framework.bad_utils.adt import ExperimentStatus
from bad_framework.bad_utils.files import get_candidate_name, get_include_dir
from bad_framework.bad_utils.network import AsyncHTTPSessionManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s", level="INFO"
)
log = logging.getLogger("bad.server.master")


class Model:
    @classmethod
    def get_by_id(cls, query_id):
        return cls._objects[query_id]

    @classmethod
    def get_all(cls):
        return cls._objects.values()

    @classmethod
    def _get_id(cls, tag):
        return tag[:4] + str(uuid4())[:8]


class Candidate(Model):

    _objects = {}

    def __init__(self, suite_id, source_filename, parameters, requirements):
        self.id = self._get_id("candidate")
        self.suite = suite_id
        self.name = get_candidate_name(source_filename)
        self.source = source_filename
        self.parameters = parameters
        self.requirements = requirements

    @classmethod
    def create(cls, suite_id, source_filename, parameters, requirements):
        new_candidate = Candidate(suite_id, source_filename, parameters, requirements)
        cls._objects[new_candidate.id] = new_candidate
        return new_candidate

    @classmethod
    def get_by_suite(cls, suite_id):
        for candidate in cls._objects.values():
            if candidate.suite == suite_id:
                return candidate


class Dataset(Model):

    _objects = {}

    def __init__(self, dataset_name, file_path):
        self.id = self._get_id("dataset")
        self.name = dataset_name
        self.path = file_path

    @classmethod
    def create(cls, dataset_name, file_path):
        new_dataset = Dataset(dataset_name, file_path)
        cls._objects[new_dataset.id] = new_dataset
        return new_dataset

    @classmethod
    def get_by_name(cls, name):
        for dataset in cls._objects.values():
            if dataset.name == name:
                return dataset

    @classmethod
    def setup(cls):
        data_dir = os.path.join(get_include_dir(), "data")
        arff_files = glob.glob("{data_dir}/*.arff".format(data_dir=data_dir))
        for dataset_file in arff_files:
            dataset_name = os.path.splitext(os.path.basename(dataset_file))[0]
            cls.create(dataset_name=dataset_name, file_path=dataset_file)


class Experiment(Model):

    _objects = {}

    _status_strings = {
        ExperimentStatus.CREATED: "created",
        ExperimentStatus.SCHEDULED: "scheduled",
        ExperimentStatus.RUNNING: "running",
        ExperimentStatus.COMPLETED: "completed",
        ExperimentStatus.FAILED: "failed",
    }

    def __init__(self, suite_id, candidate_id, dataset_name, parameters):
        self.id = self._get_id("experiment")
        self.suite = suite_id
        self.candidate = candidate_id
        self.completed_ts = None
        self.dataset = dataset_name
        self.metrics = None
        self.parameters = parameters
        self.roc = None
        self.scheduled_ts = None
        self.scores = None
        self.status = ExperimentStatus.CREATED

    def update_status(self, status):
        if status == ExperimentStatus.RUNNING:
            self.scheduled_ts = datetime.datetime.now()
        if status == ExperimentStatus.COMPLETED:
            self.completed_ts = datetime.datetime.now()
        self.status = status

    def load_metrics(self):
        if self.metrics:
            with open(self.metrics, "r") as metrics_file:
                return json.load(metrics_file)
        else:
            ValueError("metrics file not found.")

    @classmethod
    def create(cls, suite_id, candidate_id, dataset_name, parameters):
        new_experiment = Experiment(suite_id, candidate_id, dataset_name, parameters)
        cls._objects[new_experiment.id] = new_experiment
        return new_experiment

    @classmethod
    def get_by_suite(cls, suite_id):
        suite_experiments = []
        for experiment in cls._objects.values():
            if experiment.suite == suite_id:
                suite_experiments.append(experiment)
        return suite_experiments

    def get_status_string(self):
        return self._status_strings[self.status]


class Suite(Model):

    _objects = {}

    def __init__(self):
        self.id = self._get_id("suite")
        self.created_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def create(cls):
        new_suite = Suite()
        cls._objects[new_suite.id] = new_suite
        return new_suite


class Worker(Model):

    _objects = {}

    def __init__(self, hostname, port, master_address):
        self.id = self._get_id("worker")
        self.hostname = hostname
        self.port = int(port)
        self.master_address = master_address
        self.session = AsyncHTTPSessionManager(
            domain="{hostname}:{port}".format(hostname=self.hostname, port=self.port)
        )

    @classmethod
    def create(cls, hostname, port, master_address):
        new_worker = Worker(hostname, port, master_address)
        cls._objects[new_worker.id] = new_worker
        return new_worker

    @classmethod
    def setup(cls, workers, master_address):
        for hostname, port in workers:
            cls.create(hostname, port, master_address)
