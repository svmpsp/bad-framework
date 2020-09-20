"""Copyright (C) 2020 Sivam Pasupathipillai <s.pasupathipillai@unitn.it>.

All rights reserved.
"""
import json
import importlib.util
import logging
import os
import traceback

from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    roc_curve,
)
import jinja2 as j2
import matplotlib.pyplot as plt
import numpy as np
import tornado.web

from bad_framework.bad_utils import (
    install_requirements,
    load_parameter_string,
    load_data_matrix,
)
from bad_framework.bad_utils.adt import ExperimentStatus
from bad_framework.bad_utils.files import get_candidate_name
from bad_framework.bad_utils.magic import LOG_FORMAT
from bad_framework.bad_utils.network import AsyncHTTPSessionManager

logging.basicConfig(format=LOG_FORMAT, level="INFO")
log = logging.getLogger("bad.server.worker")


class BaseWorkerHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.write("<div>You've just got a big, BAD server error... sorry :(</div>")

    def get_wd(self):
        return self.application.settings["worker_home"]

    def head(self):
        self.set_status(200)
        self.flush()
        self.finish()


class IndexHandler(BaseWorkerHandler):
    def get(self):
        try:
            jinja2_env = j2.Environment(
                loader=j2.PackageLoader("bad_framework.bad_worker", "templates")
            )
            template = jinja2_env.get_template("index.html")
            rendered_template = template.render()
            self.set_status(200)
            self.set_header("Content-type", "text/html")
            self.write(rendered_template.encode())
        finally:
            self.flush()
            self.finish()


class SetupHandler(BaseWorkerHandler):
    async def _setup_worker(self):
        log.info(">>> Setting up worker")
        message = json.loads(self.request.body)

        candidate_id = message["candidate_id"]
        datasets = message["datasets"]
        master_address = message["master_address"]
        requirements = message["requirements"]
        suite_id = message["suite_id"]

        base_path = self.get_wd()
        master_session = AsyncHTTPSessionManager(master_address)
        await self._download_candidate_files(
            master_session, candidate_id, suite_id, base_path
        )
        install_requirements(requirements)
        await self._download_datasets(master_session, base_path, datasets)
        log.info("<<< Done.")

    @classmethod
    async def _download_candidate_files(
        cls, master_session, candidate_id, suite_id, base_path
    ):
        """Downloads candidate source file and its requirements.txt file.
        Installs the requirements.txt file in the current interpreter.

        :param master_session: (bad_utils.network.SessionManager) master session manager
        :param suite_id: (str) suite id
        :param base_path: (str) path to worker home directory
        :return: None
        """
        log.info("Downloading candidate file...")
        await master_session.download_file(
            url="candidate/{candidate_id}/".format(candidate_id=candidate_id),
            path="{home_dir}/{suite_id}/candidate.py".format(
                home_dir=base_path, suite_id=suite_id
            ),
        )

    @classmethod
    async def _download_datasets(cls, master_session, base_path, datasets):
        """Downloads the data sets required for suite execution.

        Only downloads data sets that have not been previously downloaded.

        :param master_session: (bad_utils.network.SessionManager) master session manager
        :param datasets: (list[string]) list of data set names to download.
        :return: None
        """
        log.info("Downloading datasets: %r", datasets)
        data_urls = [
            "dataset/{dataset_name}/".format(dataset_name=dataset)
            for dataset in datasets
        ]
        data_paths = [
            "{base_path}/datasets/{dataset_name}.arff".format(
                base_path=base_path, dataset_name=dataset
            )
            for dataset in datasets
        ]
        for data_url, data_path in zip(data_urls, data_paths):
            if not os.path.isfile(data_path):
                await master_session.download_file(data_url, data_path)

    async def post(self):
        try:
            await self._setup_worker()
            self.set_status(status_code=200)
        except Exception:
            log.error(traceback.format_exc())  # Write on worker log
        finally:
            await self.finish()


class RunHandler(BaseWorkerHandler):
    """Handles POST requests to the "/run/" path.

    This executes BAD experiment.
    """

    def prepare(self):
        message = json.loads(self.request.body)
        self._data_name = message["data_name"]
        self._experiment_id = message["experiment_id"]
        self._home_dir = self.get_wd()
        self._master_address = message["master_address"]
        self._master_session = AsyncHTTPSessionManager(self._master_address)
        self._suite_id = message["suite_id"]
        self._parameters = load_parameter_string(message["parameters"])
        self._trainset_size = self._parameters["trainset_size"]

    async def _update_experiment_status(self, status):
        experiment_url = "experiment/{experiment_id}/".format(
            experiment_id=self._experiment_id
        )
        message = {"status": status}
        await self._master_session.post_json(url=experiment_url, data=message)

    @classmethod
    def _import_candidate_module(cls, candidate_path):
        spec = importlib.util.spec_from_file_location("bad_candidate", candidate_path)
        bad_candidate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bad_candidate)
        return bad_candidate

    def _generate_metrics_file(self, labels, scores):
        metrics_path = "{home_dir}/{suite_id}/{experiment_id}/metrics.json".format(
            home_dir=self._home_dir,
            suite_id=self._suite_id,
            experiment_id=self._experiment_id,
        )
        if not os.path.exists(os.path.dirname(metrics_path)):
            os.makedirs(os.path.dirname(metrics_path))

        roc_auc = roc_auc_score(y_score=scores, y_true=labels)
        average_precision = average_precision_score(y_score=scores, y_true=labels)

        metrics = {
            "experiment_id": self._experiment_id,
            "roc_auc": roc_auc,
            "average_precision": average_precision,
        }
        pretty_json = json.dumps(metrics, indent=2)
        with open(metrics_path, "w") as metrics_file:
            metrics_file.write(pretty_json)
        return metrics_path

    def _generate_scores(
        self,
        candidate,
        data_matrix,
    ):
        feature_matrix = data_matrix[:, 2:]

        # Subsample feature matrix to obtain training set
        np.random.seed(int(self._parameters["seed"]))
        num_rows = feature_matrix.shape[0]
        trainset_size = int(num_rows * float(self._parameters["trainset_size"]))
        training_indexes = np.random.choice(num_rows, size=trainset_size, replace=False)
        training_matrix = feature_matrix[training_indexes, :]

        candidate = candidate.fit(training_matrix)
        scores = np.apply_along_axis(candidate.score, axis=1, arr=feature_matrix)
        return scores

    def _generate_roc_file(self, labels, scores):
        roc_path = "{home_dir}/{suite_id}/{experiment_id}/roc.png".format(
            home_dir=self._home_dir,
            suite_id=self._suite_id,
            experiment_id=self._experiment_id,
        )
        if not os.path.exists(os.path.dirname(roc_path)):
            os.makedirs(os.path.dirname(roc_path))
        fpr, tpr, _ = roc_curve(y_score=scores, y_true=labels)
        plt.figure()
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.plot([0, 1], [0, 1], color="navy", linestyle="--")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.title("ROC")
        plt.plot(fpr, tpr, color="blue", lw=2)
        plt.savefig(roc_path, format="png")
        plt.close()
        return roc_path

    async def _send_results(
        self,
        # scores_path,
        metrics_path,
        roc_path,
    ):
        results_url = "experiment/{experiment_id}/results/".format(
            experiment_id=self._experiment_id,
        )

        with open(metrics_path, "rb") as metrics_file:
            metrics_content = metrics_file.read()

        with open(roc_path, "rb") as roc_file:
            roc_content = roc_file.read()

        files = {
            # "scores": open(scores_path, "rb"),
            "metrics.json": metrics_content,
            "roc.png": roc_content,
        }
        await self._master_session.post_files(url=results_url, files=files)

    async def _run_experiment(self):
        log.info(
            ">>> Loading experiment %s received from %s",
            self._experiment_id,
            self._master_address,
        )
        home_dir = self.get_wd()
        candidate_path = "{home_dir}/{suite_id}/candidate.py".format(
            home_dir=home_dir, suite_id=self._suite_id
        )
        data_path = "{home_dir}/datasets/{data_name}.arff".format(
            home_dir=home_dir,
            data_name=self._data_name,
        )
        candidate_name = get_candidate_name(candidate_path)

        log.info("Loading candidate %s from candidate module...", candidate_name)
        bad_candidate = self._import_candidate_module(candidate_path)
        candidate_class = getattr(bad_candidate, candidate_name)
        candidate = candidate_class(**self._parameters)

        try:
            log.info(">>> Running experiment %s", self._experiment_id)
            log.info("Loading data matrix from %s", data_path)
            data_matrix = load_data_matrix(data_path)
            labels = data_matrix[:, 1]
            log.info("Running experiment...")
            scores = self._generate_scores(candidate, data_matrix)
            log.info("Experiment completed.")
            # log.info("Saving scores file...")
            # scores_path = _save_scores_to_file(
            #     suite_id=suite_id,
            #     experiment_id=experiment_id,
            #     result_matrix=result_matrix,
            # )
            log.info("Generating metrics file...")
            metrics_path = self._generate_metrics_file(
                labels=labels,
                scores=scores,
            )
            log.info("Generating ROC plot...")
            roc_path = self._generate_roc_file(
                labels=labels,
                scores=scores,
            )
            log.info("Sending results to master...")
            await self._send_results(
                # scores_path=scores_path,
                metrics_path=metrics_path,
                roc_path=roc_path,
            )
            log.info("<<< Experiment %s completed successfully.", self._experiment_id)
        except Exception as e:
            await self._update_experiment_status(status=ExperimentStatus.FAILED)
            log.error("Experiment runtime error: %s", e)
            log.error("<<< Experiment %s failed.", self._experiment_id)
            raise e  # Handled in self post()

    async def post(self):
        try:
            await self._update_experiment_status(status=ExperimentStatus.RUNNING)
            await self._run_experiment()
            self.set_status(status_code=200)
        except Exception:
            log.error(traceback.format_exc())  # Write on worker log
        finally:
            await self.finish()
