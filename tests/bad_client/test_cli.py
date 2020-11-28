from bad_framework.bad_client.cli import (
    _load_candidate_spec,
    _load_data_spec,
    _load_workers,
)
from bad_framework.bad_utils.adt import CandidateSpec, DataSpec


def test_load_candidate_spec_with_local_candidate(tmp_path):
    candidate_file = tmp_path / "candidate.py"
    candidate_file.write_text("dummy_content")
    assert CandidateSpec("local", candidate_file) == _load_candidate_spec(
        candidate_file
    )


def test_load_candidate_spec_with_remote_candidate():
    assert CandidateSpec("remote", "knn") == _load_candidate_spec("knn")


def test_load_data_spec_with_local_dataset(tmp_path):
    dataset_file = tmp_path / "data.arff"
    dataset_file.write_text("dummy_content")
    assert DataSpec("local", dataset_file) == _load_data_spec(dataset_file)


def test_load_data_spec_with_remote_dataset():
    assert DataSpec("remote", "shuttle") == _load_data_spec("shuttle")


def test_load_workers(tmp_path):
    workers_file_contents = "\n".join(
        [
            "localhost:1234",
            "example.host.com:4321",
        ]
    )
    workers_file = tmp_path / "workers"
    workers_file.write_text(workers_file_contents)
    expected_workers = [
        ("localhost", "1234"),
        ("example.host.com", "4321"),
    ]
    assert expected_workers == _load_workers(workers_file)
