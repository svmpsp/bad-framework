"""Main module for the BAD master process implementation."""
import json
import logging
import os
import time
import traceback

from jinja2 import Environment, PackageLoader
from tornado.ioloop import IOLoop
import tornado.web

from bad_framework.bad_utils import generate_experiments_settings, load_parameter_string
from bad_framework.bad_utils.adt import ExperimentStatus
from bad_framework.bad_utils.files import (
    get_candidate_file_paths,
    load_parameters,
    save_file,
)
from .models import Candidate, Dataset, Experiment, Suite, Worker

# TODO: move log to application.settings
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s", level="INFO"
)
log = logging.getLogger("bad.server.master")


class BaseMasterHandler(tornado.web.RequestHandler):
    """Base handler for BAD master HTTP requests."""

    def write_error(self, status_code, **kwargs):
        """Writes a custom error page to the output stream.

        :param status_code: (int) HTTP status code (not used).
        :param kwargs: (dict) keyword arguments (not used).
        """
        self.write("<div>You just got a big, BAD server error... sorry :(</div>")

    def get_wd(self):
        """Returns the path to the working directory for the BAD master.

        :return: (string) path to working directory.
        """
        return self.application.settings["master_home"]

    def head(self):
        """Handler for HTTP HEAD method."""
        self.set_status(200)
        self.flush()
        self.finish()

    def get_file_contents(self, file_name):
        """Returns the body of a multi-part encoded file sent with the HTTP request.

        The file is identified by a filename set by the HTTP client.

        :param file_name: (string) identifier of the file to fetch.
        :return: (bytes) contents of the file.
        """
        return self.request.files[file_name][0].body


class IndexHandler(BaseMasterHandler):
    """Handler for the BAD master index page."""

    def _render_index(self):
        """Renders the index HTML page."""
        suites = Suite.get_all()
        jinja2_env = Environment(
            loader=PackageLoader("bad_framework.bad_master", "templates")
        )
        template = jinja2_env.get_template("index.html")
        rendered_template = template.render(suites=suites)
        self.set_header("Content-type", "text/html")
        self.write(rendered_template.encode())

    def get(self):
        """Handler for HTTP GET method.

        Renders the index page and returns.
        """
        try:
            self._render_index()
            self.set_status(200)
        except Exception as e:
            self.set_status(500, reason=str(e))
        finally:
            self.flush()


class CandidateHandler(BaseMasterHandler):
    """Handler for candidate related requests."""

    def _get_candidate_file(self, candidate_id):
        """Writes the candidate.py file contents to the output stream.

        :param candidate_id: (string) candidate id.
        """
        candidate = Candidate.get_by_id(candidate_id)
        with open(candidate.source, "rb") as candidate_file:
            self.write(candidate_file.read())

    def _get_requirements_file(self, candidate_id):
        """Writes the requirements.txt file contents to the output stream.

        :param candidate_id: (string) candidate id.
        """
        candidate = Candidate.get_by_id(candidate_id)
        with open(candidate.requirements, "rb") as requirement_file:
            self.write(requirement_file.read())

    def get(self, candidate_id):
        """Handler for HTTP GET method.

        Returns candidate files depending on the requested path.
        """
        try:
            if "requirements" in self.request.path:
                self._get_requirements_file(candidate_id)
            else:
                self._get_candidate_file(candidate_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(status_code=500, reason=str(e))
        finally:
            self.flush()


class DatasetHandler(BaseMasterHandler):
    """Handler for dataset related requests."""

    def get(self, dataset_name):
        """Handler for HTTP GET method.

        Writes the requested dataset to the output stream.

        :param dataset_name: (string) dataset name.
        """
        try:
            dataset = Dataset.get_by_name(dataset_name)
            with open(dataset.path, "rb") as data_file:
                content = data_file.read()
                self.write(content)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(status_code=500, reason=str(e))
        finally:
            self.flush()
            self.finish()


class ExperimentHandler(BaseMasterHandler):
    """Handler for experiment related requests."""

    def _render_experiment_details(self, experiment_id):
        """Renders the experiment details HTML page.

        :param experiment_id: (string) experiment id.
        """
        experiment = Experiment.get_by_id(experiment_id)
        candidate = Candidate.get_by_id(experiment.candidate)
        jinja2_env = Environment(
            loader=PackageLoader("bad_framework.bad_master", "templates")
        )
        template = jinja2_env.get_template("experiment_details.html")
        rendered_template = template.render(candidate=candidate, experiment=experiment)
        self.set_header("Content-type", "text/html")
        self.write(rendered_template.encode())

    def _update_experiment_status(self, experiment_id):
        """Updates the status of an experiment.

        The updated status is encoded in the JSON payload of the request.

        :param experiment_id: (string) experiment id.
        """
        message = json.loads(self.request.body)
        experiment = Experiment.get_by_id(experiment_id)
        experiment.update_status(message["status"])

    def get(self, experiment_id):
        """Handler for HTTP GET method.

        Renders the experiment details page.

        :param experiment_id: (string) experiment id.
        """
        try:
            self._render_experiment_details(experiment_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(status_code=500, reason=str(e))
        finally:
            self.flush()
            self.finish()

    def post(self, experiment_id):
        """Handler for HTTP POST method.

        Updates an experiment's status.

        :param experiment_id: (string) experiment id.
        """
        try:
            self._update_experiment_status(experiment_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(500, reason=str(e))
        finally:
            self.finish()


class ResultHandler(BaseMasterHandler):
    """Handler for results related requests."""

    def save_experiment_results(self, experiment_id):
        """Saves the results experiment results received from a worker in a local file.
        Updates the experiment with the paths to the result files.

        :param experiment_id: (string) experiment id.
        """
        log.info("Saving results for experiment %s", experiment_id)
        experiment = Experiment.get_by_id(experiment_id)

        base_path = "{home_dir}/{suite_id}/{experiment_id}/".format(
            home_dir=self.get_wd(),
            suite_id=experiment.suite,
            experiment_id=experiment_id,
        )

        # If worker and master are on the same host, the files are already there
        metrics_path = base_path + "metrics.json"
        if not os.path.exists(metrics_path):
            metrics_content = self.get_file_contents("metrics.json")
            save_file(metrics_content, metrics_path)

        roc_path = base_path + "roc.png"
        if not os.path.exists(roc_path):
            roc_content = self.get_file_contents("roc.png")
            save_file(roc_content, roc_path)

        experiment.metrics = metrics_path
        experiment.roc = roc_path
        experiment.update_status(ExperimentStatus.COMPLETED)

    def post(self, experiment_id):
        """Handler for HTTP POST method.

        Receives the experiment result files from a worker and saves them to disk.

        :param experiment_id: (string) experiment id.
        """
        try:
            self.save_experiment_results(experiment_id)
            self.set_status(status_code=200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(500, reason=str(e))
        finally:
            self.finish()

    def _get_metrics_file(self, experiment_id):
        """Writes the metric.json file contents to the output stream.

        :param experiment_id: (string) experiment id.
        """
        experiment = Experiment.get_by_id(experiment_id)
        with open(experiment.metrics, "rb") as metrics_file:
            self.set_header("Content-type", "application/json")
            self.write(metrics_file.read())

    def _get_roc_file(self, experiment_id):
        """Writes the roc.png file contents to the output stream.

        :param experiment_id: (string) experiment id.
        """
        experiment = Experiment.get_by_id(experiment_id)
        with open(experiment.roc, "rb") as roc_file:
            self.set_header("Content-type", "image/png")
            self.write(roc_file.read())

    def get(self, experiment_id):
        """Handler for HTTP GET method.

        Returns the experiment's results file.

        :param experiment_id: (string) experiment id.
        """
        try:
            if "metrics.json" in self.request.path:
                self._get_metrics_file(experiment_id)
            elif "roc.png" in self.request.path:
                self._get_roc_file(experiment_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(500, reason=str(e))
        finally:
            self.flush()
            self.finish()


class SuiteHandler(BaseMasterHandler):
    """Handler for Suite related requests."""

    def _save_candidate_files(self, file_paths):
        """Writes candidate files to disc. The candidate files are multi-part encoded in the
        request payload.

        The files are written in the master working directory under the relative suite directory.

        :param file_paths: (dict) paths to candidate files.
        """
        save_file(self.get_file_contents("candidate_source"), file_paths["candidate"])
        save_file(
            self.get_file_contents("candidate_requirements"),
            file_paths["requirements"],
        )
        save_file(
            self.get_file_contents("candidate_parameters"), file_paths["parameters"]
        )

    def _create_candidate(self, suite_id):
        """Creates a new candidate.

        :param suite_id: (string) suite id.
        :return: (models.Candidate) created candidate.
        """
        file_paths = get_candidate_file_paths(self.get_wd(), suite_id)
        self._save_candidate_files(file_paths)
        candidate = Candidate.create(suite_id, file_paths)
        return candidate

    @classmethod
    def _generate_suite_experiments(cls, suite, candidate, parameters, datasets):
        """Creates the experiments related to this suite.

        An experiment is created for each dataset/parameter value combination.

        :param suite: (models.Suite) suite object.
        :param candidate: (models.Candidate) candidate object.
        :param parameters: (dict) parameter specification dictionary.
        :param datasets: (list[models.Dataset]) list of dataset objects.
        :return: (list[models.Experiment]) list of created experiments
        """
        for experiment_setting in generate_experiments_settings(datasets, parameters):
            Experiment.create(
                suite_id=suite.id,
                candidate_id=candidate.id,
                dataset_name=experiment_setting.dataset_name,
                parameters=experiment_setting.parameters,
            )
        return Experiment.get_by_suite(suite.id)

    @classmethod
    async def _schedule_experiment(cls, experiment, worker):
        """Sends an experiment to be scheduled to a worker.

        :param worker: (models.Worker) worker object.
        :param experiment: (models.Experiment) experiment object.
        """
        message = {
            "suite_id": experiment.suite,
            "data_name": experiment.dataset,
            "experiment_id": experiment.id,
            "master_address": worker.master_address,
            "parameters": experiment.parameters,
        }
        experiment.update_status(ExperimentStatus.SCHEDULED)
        await worker.session.post_json("run/", message)

    async def _start_scheduling_loop(self, experiments, workers):
        """Starts the experiment scheduling loop. Experiments are scheduled in time in order not
        to overload the workers.

        Each worker runs one experiment at-a-time.

        TODO:
         - make more clear/elegant/split
         - parameterize sleep interval

        :param experiments: (list[models.Experiment]) list of experiments to schedule.
        :param workers: (list[models.Worker]) list of workers to schedule the experiment on.
        """
        workers_num = len(workers)
        experiments_num = len(experiments)

        log.info(">>> Starting scheduling loop")
        log.info("Found %d available workers.", workers_num)
        log.info("Running %d experiments.", experiments_num)

        scheduled_experiments = []
        todo_experiments = experiments
        worker_index = 0
        scheduled_experiments_num = 0
        last_message = ""

        while todo_experiments:
            running_experiments_num = len(
                [
                    experiments
                    for experiment in scheduled_experiments
                    if experiment.status == ExperimentStatus.RUNNING
                ]
            )
            if running_experiments_num < workers_num:
                next_experiment, *todo_experiments = todo_experiments
                await self._schedule_experiment(
                    experiment=next_experiment, worker=workers[worker_index],
                )
                scheduled_experiments.append(next_experiment)
                worker_index = (worker_index + 1) % workers_num
            scheduled_experiments_num = len(scheduled_experiments)
            message = "...{running_num} ({scheduled_num}/{total_num}) running (scheduled/total) experiments.".format(
                running_num=running_experiments_num,
                scheduled_num=scheduled_experiments_num,
                total_num=experiments_num,
            )
            if message != last_message:
                log.info(message)
                last_message = message
            time.sleep(0.25)
        log.info(
            "<<< Scheduling loop completed (%d/%d).",
            scheduled_experiments_num,
            experiments_num,
        )

    @classmethod
    async def _initialize_worker_envs(cls, suite_id, candidate_id, workers, datasets):
        """Initializes each worker's environment with the dependencies required to run the experiments.

        :param suite_id: (string) suite id.
        :param workers: (list[models.Worker]) list of workers to initialize.
        :param datasets: (list[models.Dataset]) list of dataset required for the experiments.
        """
        for worker in workers:
            log.info("Setting up worker at %s on port %d", worker.hostname, worker.port)
            message = {
                "master_address": worker.master_address,
                "suite_id": suite_id,
                "candidate_id": candidate_id,
                "datasets": [dataset.name for dataset in datasets],
            }
            response = await worker.session.post_json("setup/", message)
            if response.status_code == 200:
                log.info("worker initialized correctly.")
            else:
                raise ValueError("worker initialization failed: ", response.reason)

    async def post(self):
        """Handler for HTTP POST method.

        Creates a new experiment suite with the settings encoded in the request's payload.
        """
        try:
            message = json.loads(self.get_file_contents("suite_settings"))
            seed = message["seed"]
            trainset_size = message["trainset_size"]
            data_name = message["data"]
            master_address = message["master_address"]
            workers_list = message["workers"]
            suite = Suite.create(seed, trainset_size)
            candidate = self._create_candidate(suite.id)
            if not Dataset.get_all():
                Dataset.setup()
            if data_name:
                datasets = [Dataset.get_by_name(data_name)]
            else:
                datasets = Dataset.get_all()
            if not Worker.get_all():
                Worker.setup(workers_list, master_address)
            workers = list(
                Worker.get_all()  # this returns a non-subscriptable set-like
            )
            parameters = load_parameters(candidate.parameters, suite)
            experiments = self._generate_suite_experiments(
                suite=suite,
                candidate=candidate,
                datasets=datasets,
                parameters=parameters,
            )
            await self._initialize_worker_envs(
                suite.id, candidate.id, workers, datasets
            )

            # runs scheduling loop in the background
            IOLoop.current().add_callback(
                callback=self._start_scheduling_loop,
                experiments=experiments,
                workers=workers,
            )

            message = {"suite_id": suite.id}
            self.write(message)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(500, reason=str(e))
        finally:
            await self.finish()

    def _render_suite_details(self, suite_id):
        """Renders the suite details HTML page.

        :param suite_id: (string) suite id.
        """
        candidate = Candidate.get_by_suite(suite_id)
        experiments = Experiment.get_by_suite(suite_id)
        jinja2_env = Environment(
            loader=PackageLoader("bad_framework.bad_master", "templates")
        )
        template = jinja2_env.get_template("suite_details.html")
        rendered_template = template.render(
            candidate=candidate, experiments=experiments
        )
        self.set_header("Content-type", "text/html")
        self.write(rendered_template.encode())

    def get(self, suite_id):
        """Handler for HTTP GET method.

        Renders the suite details HTML page.
        """
        try:
            self._render_suite_details(suite_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())
            self.set_status(status_code=500, reason=str(e))
        finally:
            self.flush()
            self.finish()


class SuiteExperimentsHandler(BaseMasterHandler):
    """Handler for requests related to suite experiments."""

    def _get_suite_experiments(self, suite_id):
        """Writes JSON-encoded information on suite experiments to the output stream.

        :param suite_id: (string) suite id.
        """
        message = {
            "suite_id": suite_id,
            "experiments": [
                {"id": experiment.id, "status": experiment.get_status_string()}
                for experiment in Experiment.get_by_suite(suite_id)
            ],
        }
        self.write(chunk=message)

    def get(self, suite_id):
        """Handler for HTTP GET method.

        Returns information on the suite experiments as a JSON-encoded file.
        """
        try:
            self._get_suite_experiments(suite_id)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))
        finally:
            self.flush()
            self.finish()


class SuiteDumpHandler(BaseMasterHandler):
    """Handler for requests related to the suite results dump."""

    def _get_suite_dump(self, suite_id):
        """Writes CSV-encoded suite results to the output stream.

        :param suite_id: (string) suite id.
        """

        def get_dump_header(params):
            parameter_names = sorted(params.keys())
            fields = [
                "experiment_id",
                "execution_time_microseconds",
                "data",
                "candidate",
                "roc_auc",
                "average_precision",
                *parameter_names,
            ]
            return ",".join(fields) + "\n"

        def get_digest_line(exp):
            metrics = experiment.load_metrics()

            exp_parameters = load_parameter_string(exp.parameters)
            parameter_values = [v for k, v in sorted(exp_parameters.items())]
            roc_auc = metrics["roc_auc"]
            average_precision = metrics["average_precision"]
            execution_time_microseconds = int(
                (exp.completed_ts - exp.scheduled_ts).total_seconds() * 1e6
            )
            digest_fields = [
                exp.id,
                str(execution_time_microseconds),
                exp.dataset,
                Candidate.get_by_id(exp.candidate).name,
                str(roc_auc),
                str(average_precision),
                *parameter_values,
            ]
            return ",".join(digest_fields) + "\n"

        experiments = Experiment.get_by_suite(suite_id)
        parameters = load_parameter_string(experiments[0].parameters)
        self.write(get_dump_header(parameters))
        for experiment in experiments:
            if experiment.status == ExperimentStatus.COMPLETED:
                experiment_digest_line = get_digest_line(experiment)
                self.write(chunk=experiment_digest_line)

    def get(self, suite_id):
        """Handler for HTTP GET method.

        Returns information on the suite results as a CSV-encoded file.
        """
        try:
            self._get_suite_dump(suite_id)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))
        finally:
            self.flush()
            self.finish()
