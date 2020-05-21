import io
import json
import logging
import os
import time
import traceback

from jinja2 import Environment, PackageLoader
import tornado.web

from bad_framework.bad_utils import generate_experiments_settings
from bad_framework.bad_utils.adt import ExperimentStatus
from bad_framework.bad_utils.files import (
    get_candidate_file_paths,
    load_parameters,
    save_file,
)
from .models import Candidate, Dataset, Experiment, Suite, Worker

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)5s - %(message)s", level="INFO"
)
log = logging.getLogger("bad.server.master")


class BaseMasterHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.write("<div>You just got a big, BAD server error... sorry :(</div>")

    def get_wd(self):
        return self.application.settings["master_home"]

    def head(self):
        self.set_status(200)
        self.flush()

    def get_file_contents(self, file_name):
        return self.request.files[file_name][0].body


class IndexHandler(BaseMasterHandler):
    def _render_index(self):
        suites = Suite.get_all()
        jinja2_env = Environment(
            loader=PackageLoader("bad_framework.bad_master", "templates")
        )
        template = jinja2_env.get_template("index.html")
        rendered_template = template.render(suites=suites)
        self.set_header("Content-type", "text/html")
        self.write(rendered_template.encode())

    def get(self):
        try:
            self._render_index()
            self.set_status(200)
        except Exception as e:
            self.set_status(500, reason=str(e))
        finally:
            self.flush()


class CandidateHandler(BaseMasterHandler):
    def _get_candidate_file(self, candidate_id):
        candidate = Candidate.get_by_id(candidate_id)
        with open(candidate.source, "rb") as candidate_file:
            self.write(candidate_file.read())

    def _get_requirements_file(self, candidate_id):
        candidate = Candidate.get_by_id(candidate_id)
        with open(candidate.requirements, "rb") as requirement_file:
            self.write(requirement_file.read())

    def get(self, candidate_id):
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


class DataHandler(BaseMasterHandler):
    def get(self, dataset_name):
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


class ExperimentHandler(BaseMasterHandler):
    def _render_experiment_details(self, experiment_id):
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
        message = json.loads(self.request.body)
        experiment = Experiment.get_by_id(experiment_id)
        experiment.update_status(message["status"])

    def get(self, experiment_id):
        try:
            self._render_experiment_details(experiment_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(status_code=500, reason=str(e))
        finally:
            self.flush()

    def post(self, experiment_id):
        try:
            self._update_experiment_status(experiment_id)
            self.set_status(200)
        except Exception as e:
            self.set_status(500, reason=str(e))
        finally:
            self.flush()


class ResultHandler(BaseMasterHandler):
    def save_experiment_results(self, experiment_id):
        log.info("Saving results for experiment %s", experiment_id)
        experiment = Experiment.get_by_id(experiment_id)
        metrics_content = self.get_file_contents("metrics.json")
        roc_content = self.get_file_contents("roc.png")

        base_path = "{home_dir}/{suite_id}/{experiment_id}/".format(
            home_dir=self.get_wd(),
            suite_id=experiment.suite,
            experiment_id=experiment_id,
        )

        # If worker and master are on the same host, the files are already there
        metrics_path = base_path + "metrics.json"
        if not os.path.exists(metrics_path):
            save_file(metrics_content, metrics_path)

        roc_path = base_path + "roc.png"
        if not os.path.exists(roc_path):
            save_file(roc_content, roc_path)

        experiment.metrics = metrics_path
        experiment.roc = roc_path
        experiment.update_status(ExperimentStatus.COMPLETED)

    def post(self, experiment_id):
        try:
            self.save_experiment_results(experiment_id)
            self.set_status(status_code=200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))

    def _get_metrics_file(self, experiment_id):
        experiment = Experiment.get_by_id(experiment_id)
        with open(experiment.metrics, "rb") as metrics_file:
            self.set_header("Content-type", "application/json")
            self.write(metrics_file.read())

    def _get_roc_file(self, experiment_id):
        experiment = Experiment.get_by_id(experiment_id)
        with open(experiment.roc, "rb") as roc_file:
            self.set_header("Content-type", "image/png")
            self.write(roc_file.read())

    def get(self, experiment_id):
        try:
            if "metrics.json" in self.request.path:
                self._get_metrics_file(experiment_id)
            elif "roc.png" in self.request.path:
                self._get_roc_file(experiment_id)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))
        finally:
            self.flush()


class SuiteHandler(BaseMasterHandler):
    def _save_candidate_files(self, suite_id):
        file_paths = get_candidate_file_paths(self.get_wd(), suite_id)
        save_file(self.get_file_contents("candidate_source"), file_paths["candidate"])
        save_file(
            self.get_file_contents("candidate_requirements"),
            file_paths["requirements"],
        )
        save_file(
            self.get_file_contents("candidate_parameters"), file_paths["parameters"]
        )

    def _create_candidate(self, suite_id):
        self._save_candidate_files(suite_id)
        candidate = Candidate.create(
            suite_id, get_candidate_file_paths(self.get_wd(), suite_id)
        )
        return candidate

    @classmethod
    def _generate_suite_experiments(cls, suite, candidate, datasets):
        parameters = load_parameters(candidate.parameters, suite.seed)

        log.info("Parameters are: %s", parameters)

        for experiment_setting in generate_experiments_settings(datasets, parameters):

            log.info("Experiment settings parameters: %s", experiment_setting.parameters)

            Experiment.create(
                suite_id=suite.id,
                candidate_id=candidate.id,
                dataset_name=experiment_setting.dataset_name,
                parameters=experiment_setting.parameters,
            )
        return Experiment.get_by_suite(suite.id)

    @classmethod
    async def _schedule_experiment(cls, worker, experiment):
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
        """
        TODO:
         - make more clear/elegant/split
         - parameterize sleep interval

        :param experiments:
        :param workers:
        :return:
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
                await self._schedule_experiment(workers[worker_index], next_experiment)
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
        """
        TODO:
         - parallelize worker initialization

        :param suite_id:
        :param workers:
        :param datasets:
        :return:
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
        try:
            message = json.loads(self.get_file_contents("suite_settings"))
            seed = message["seed"]
            data_name = message["data"]
            master_address = message["master_address"]
            workers_list = message["workers"]
            suite = Suite.create(seed)
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
            experiments = self._generate_suite_experiments(suite, candidate, datasets)
            await self._initialize_worker_envs(
                suite.id, candidate.id, workers, datasets
            )

            await self._start_scheduling_loop(experiments, workers)

            message = {"suite_id": suite.id}
            self.write(message)
            self.set_status(200)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))

    def get(self, suite_id):
        candidate = Candidate.get_by_suite(suite_id)
        experiments = Experiment.get_by_suite(suite_id)
        jinja2_env = Environment(
            loader=PackageLoader("bad_framework.bad_master", "templates")
        )
        template = jinja2_env.get_template("suite_details.html")
        rendered_template = template.render(candidate=candidate, experiments=experiments)
        self.set_header("Content-type", "text/html")
        self.write(rendered_template.encode())


class SuiteExperimentsHandler(BaseMasterHandler):

    def _get_suite_experiments(self, suite_id):
        message = {
            "suite_id": suite_id,
            "experiments": [
                {
                    "id": experiment.id,
                    "status": experiment.get_status_string()
                }
                for experiment in Experiment.get_by_suite(suite_id)
            ],
        }
        self.write(chunk=message)

    def get(self, suite_id):
        try:
            self._get_suite_experiments(suite_id)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))


class SuiteDumpHandler(BaseMasterHandler):

    def _get_suite_dump(self, suite_id):

        def get_dump_header():
            fields = [
                "experiment_id",
                "execution_time_microseconds",
                "data",
                "candidate",
                "parameters",
                "roc_auc",
                "average_precision",
            ]
            return ",".join(fields) + "\n"

        def get_digest_line(experiment):
            metrics = experiment.load_metrics()

            roc_auc = metrics["roc_auc"]
            average_precision = metrics["average_precision"]
            execution_time_microseconds = int(
                (experiment.completed_ts - experiment.scheduled_ts).total_seconds() * 1e6
            )
            digest_fields = [
                experiment.id,
                str(execution_time_microseconds),
                experiment.dataset,
                experiment.candidate,
                experiment.parameters,
                str(roc_auc),
                str(average_precision),
            ]
            return ",".join(digest_fields) + "\n"

        self.write(get_dump_header())
        for experiment in Experiment.get_by_suite(suite_id):
            if experiment.status == ExperimentStatus.COMPLETED:
                experiment_digest_line = get_digest_line(experiment)
                self.write(chunk=experiment_digest_line)

    def get(self, suite_id):
        try:
            self._get_suite_dump(suite_id)
        except Exception as e:
            log.error(traceback.format_exc())  # Write on master log
            self.set_status(500, reason=str(e))

