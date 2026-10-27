"""Behavior of the learning bench: validation, fits, the runner, and HTTP."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from ml_studio.catalog import catalog, validate_request
from ml_studio.runner import TaskRunner
from ml_studio.server import make_server
from ml_studio.train import TrainResult, fit_job

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_MINIMUM_PNG_BYTES = 2000
_SEED = 19680801


def _classification_request(**overrides):
    payload = {
        "dataset": "blobs",
        "estimator": "logistic_regression",
        "dataset_parameters": {"n_samples": 180, "cluster_std": 1.2},
        "parameters": {"C": 1.0, "max_iter": 200},
        "test_size": 0.25,
        "random_state": _SEED,
    }
    payload.update(overrides)
    return payload


def _regression_request(**overrides):
    payload = {
        "dataset": "synthetic_regression",
        "estimator": "linear_regression",
        "dataset_parameters": {"n_samples": 240, "noise": 8.0},
        "parameters": {"fit_intercept": True},
        "test_size": 0.25,
        "random_state": _SEED,
    }
    payload.update(overrides)
    return payload


def _stub_result():
    return TrainResult(
        metrics={"task": "classification", "test_accuracy": 1.0},
        figures={"scores": _PNG_SIGNATURE + b"0" * 16},
    )


class _HoldingExecutor:
    """Records work and does not run it."""

    def __init__(self):
        self.submitted = []

    def submit(self, fn, *args, **kwargs):
        self.submitted.append((fn, args, kwargs))
        return None

    def shutdown(self, wait=True):
        return None


def test_catalog_ids_are_unique_and_parameters_are_typed():
    data = catalog()
    dataset_ids = [item["id"] for item in data["datasets"]]
    estimator_ids = [item["id"] for item in data["estimators"]]
    assert len(dataset_ids) == len(set(dataset_ids))
    assert len(estimator_ids) == len(set(estimator_ids))
    allowed = {"int", "float", "bool", "choice"}
    specs = list(data["shared_parameters"])
    for collection in (data["datasets"], data["estimators"]):
        for item in collection:
            specs.extend(item["parameters"])
            assert item["task"] in {task["id"] for task in data["tasks"]}
    for spec in specs:
        assert spec["type"] in allowed
        assert "default" in spec
        assert spec["label"]


def test_validate_request_is_stable_and_fills_labels():
    once = validate_request(_classification_request())
    twice = validate_request(once)
    assert once == twice
    assert once["dataset_label"] == "Blobs"
    assert once["estimator_label"] == "Logistic regression"
    assert once["task"] == "classification"


def test_validate_request_rejects_an_unknown_dataset():
    payload = _classification_request(dataset="missing")
    with pytest.raises(ValueError, match="dataset"):
        validate_request(payload)


def test_validate_request_rejects_an_estimator_for_the_other_task():
    payload = _classification_request(estimator="ridge", parameters={"alpha": 1.0})
    with pytest.raises(ValueError, match="regression"):
        validate_request(payload)


def test_validate_request_rejects_an_unknown_parameter():
    payload = _classification_request()
    payload["parameters"] = {"C": 1.0, "max_iter": 200, "gamma": 0.1}
    with pytest.raises(ValueError, match="gamma"):
        validate_request(payload)


def test_validate_request_rejects_a_bool_used_as_an_integer():
    payload = _classification_request()
    payload["parameters"] = {"C": 1.0, "max_iter": True}
    with pytest.raises(ValueError, match="max_iter"):
        validate_request(payload)


def test_validate_request_rejects_a_test_fraction_of_zero():
    payload = _classification_request(test_size=0)
    with pytest.raises(ValueError, match="test_size"):
        validate_request(payload)


def test_validate_request_rejects_too_many_trees():
    payload = _classification_request(
        estimator="random_forest",
        parameters={"n_estimators": 10_000, "max_depth": 4},
    )
    with pytest.raises(ValueError, match="n_estimators"):
        validate_request(payload)


def test_validate_request_rejects_parameters_that_are_not_an_object():
    payload = _classification_request(parameters=["C"])
    with pytest.raises(ValueError, match="parameters"):
        validate_request(payload)


def test_logistic_regression_on_blobs_reports_accuracy_and_png_figures():
    result = fit_job(_classification_request())
    minimum_test_accuracy = 0.85
    assert result.metrics["test_accuracy"] > minimum_test_accuracy
    assert result.metrics["n_train"] + result.metrics["n_test"] == 180
    assert set(result.figures) >= {"scores", "confusion", "projection", "importance"}
    for name, payload in result.figures.items():
        assert payload.startswith(_PNG_SIGNATURE), name
        assert len(payload) > _MINIMUM_PNG_BYTES


def test_regression_score_chart_separates_r2_and_absolute_error():
    from ml_studio.plots import _scores_figure

    fig = _scores_figure(
        "regression",
        {
            "train_r2": 0.47,
            "test_r2": 0.46,
            "train_mae": 45.6,
            "test_mae": 46.0,
        },
    )
    fig.canvas.draw()
    assert [ax.get_title() for ax in fig.axes] == ["R²", "Mean absolute error"]
    r2_span = fig.axes[0].get_ylim()[1] - fig.axes[0].get_ylim()[0]
    mae_span = fig.axes[1].get_ylim()[1] - fig.axes[1].get_ylim()[0]
    assert mae_span > r2_span * 5


def test_split_skips_stratify_for_a_singleton_class():
    from ml_studio.train import _split

    features = [[0.0, 0.0]] * 5
    target = [0, 0, 0, 0, 1]
    request = {"task": "classification", "test_size": 0.4, "random_state": _SEED}
    _x_train, _x_test, y_train, y_test = _split(request, features, target)
    assert len(y_train) + len(y_test) == 5


def test_split_does_not_hide_an_unrelated_error(monkeypatch):
    from ml_studio import train as train_mod

    def fail_once(*_args, **_kwargs):
        raise ValueError("bad columns")

    monkeypatch.setattr(train_mod, "train_test_split", fail_once)
    features = [[0.0, 0.0]] * 8
    target = [0, 0, 0, 0, 1, 1, 1, 1]
    request = {"task": "classification", "test_size": 0.25, "random_state": _SEED}
    with pytest.raises(ValueError, match="bad columns"):
        train_mod._split(request, features, target)


def test_projection_of_iris_does_not_invent_a_decision_grid():
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    from ml_studio.train import _plane

    bunch = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        bunch.data,
        bunch.target,
        test_size=0.25,
        random_state=_SEED,
        stratify=bunch.target,
    )
    estimator = LogisticRegression(max_iter=200).fit(x_train, y_train)
    plane = _plane(
        estimator,
        x_train,
        x_test,
        y_test,
        estimator.predict(x_test),
        list(bunch.feature_names),
        _SEED,
        "classification",
    )
    assert plane is not None
    assert plane.predict is None
    assert plane.xlabel == "Component 1"
    result = fit_job(
        _classification_request(
            dataset="iris",
            dataset_parameters={},
            parameters={"C": 1.0, "max_iter": 200},
        )
    )
    assert result.figures["projection"].startswith(_PNG_SIGNATURE)


def test_two_feature_plane_predicts_on_those_columns():
    from sklearn.datasets import make_blobs
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    from ml_studio.train import _plane

    features, target = make_blobs(
        n_samples=80, centers=3, n_features=2, random_state=_SEED
    )
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.25, random_state=_SEED, stratify=target
    )
    estimator = LogisticRegression(max_iter=200).fit(x_train, y_train)
    plane = _plane(
        estimator,
        x_train,
        x_test,
        y_test,
        estimator.predict(x_test),
        ["x", "y"],
        _SEED,
        "classification",
    )
    row = x_test[:1]
    assert plane.predict is not None
    assert plane.predict(row).tolist() == estimator.predict(row).tolist()


def test_linear_regression_reports_r2_and_residual_figures():
    result = fit_job(_regression_request())
    minimum_test_r2 = 0.9
    assert result.metrics["test_r2"] > minimum_test_r2
    assert result.metrics["test_mae"] > 0
    assert set(result.figures) >= {
        "scores",
        "predicted",
        "residuals",
        "projection",
        "importance",
    }
    assert result.figures["predicted"].startswith(_PNG_SIGNATURE)


def test_knn_fit_omits_feature_weights_when_the_model_has_none():
    request = _classification_request(
        estimator="knn",
        parameters={"n_neighbors": 3, "weights": "uniform"},
        dataset_parameters={"n_samples": 120, "cluster_std": 0.8},
    )
    result = fit_job(request)
    minimum_test_accuracy = 0.8
    assert result.metrics["test_accuracy"] > minimum_test_accuracy
    assert "importance" not in result.figures
    assert "confusion" in result.figures


def test_submit_returns_while_the_fit_is_still_running():
    started = threading.Event()
    release = threading.Event()

    def fit(request):
        started.set()
        assert release.wait(timeout=5)
        return _stub_result()

    runner = TaskRunner(max_workers=1, fit=fit)
    try:
        job_id = runner.submit(_classification_request())
        assert started.wait(timeout=5)
        assert runner.get(job_id)["status"] == "running"
        release.set()
        finished = runner.wait(job_id, timeout=5)
    finally:
        release.set()
        runner.shutdown()
    assert finished["status"] == "succeeded"
    assert finished["metrics"]["test_accuracy"] == 1.0


def test_cancel_queued_job_skips_the_fit():
    calls = []

    def fit(request):
        calls.append(request)
        return _stub_result()

    executor = _HoldingExecutor()
    runner = TaskRunner(executor=executor, fit=fit)
    job_id = runner.submit(_classification_request())
    assert runner.get(job_id)["status"] == "queued"
    runner.cancel(job_id)
    fn, args, kwargs = executor.submitted[0]
    fn(*args, **kwargs)
    assert calls == []
    assert runner.get(job_id)["status"] == "cancelled"
    runner.shutdown()


def test_failed_fit_records_the_error():
    def fit(request):
        raise RuntimeError("singular matrix")

    runner = TaskRunner(max_workers=1, fit=fit)
    try:
        job_id = runner.submit(_classification_request())
        finished = runner.wait(job_id, timeout=5)
    finally:
        runner.shutdown()
    assert finished["status"] == "failed"
    assert finished["error"] == "singular matrix"
    assert finished["figures"] == []


def test_runner_forgets_the_oldest_finished_job_to_make_room():
    runner = TaskRunner(max_workers=1, fit=lambda request: _stub_result(), max_jobs=2)
    try:
        first = runner.submit(_classification_request())
        runner.wait(first, timeout=5)
        second = runner.submit(_classification_request())
        runner.wait(second, timeout=5)
        third = runner.submit(_classification_request())
        runner.wait(third, timeout=5)
        ids = [job["id"] for job in runner.list_jobs()]
    finally:
        runner.shutdown()
    assert first not in ids
    assert ids[0] == third


def test_runner_rejects_a_job_when_every_slot_is_still_in_flight():
    runner = TaskRunner(
        executor=_HoldingExecutor(), fit=lambda request: _stub_result(), max_jobs=2
    )
    runner.submit(_classification_request())
    runner.submit(_classification_request())
    with pytest.raises(RuntimeError, match="in flight"):
        runner.submit(_classification_request())
    runner.shutdown()


def _http(port, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", data=data, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


@pytest.fixture
def bench_server():
    runner = TaskRunner(max_workers=2)
    server = make_server("127.0.0.1", 0, runner)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        server.server_close()
        runner.shutdown(wait=True)


def test_http_page_and_catalog_load(bench_server):
    status, body = _http(bench_server, "GET", "/")
    assert status == 200
    assert b"Learning bench" in body
    status, body = _http(bench_server, "GET", "/api/catalog")
    payload = json.loads(body)
    assert status == 200
    assert any(item["id"] == "iris" for item in payload["datasets"])


def test_http_job_returns_a_png(bench_server):
    status, body = _http(
        bench_server,
        "POST",
        "/api/jobs",
        {
            "dataset": "moons",
            "estimator": "gaussian_nb",
            "dataset_parameters": {"n_samples": 120, "noise": 0.2},
            "random_state": _SEED,
        },
    )
    assert status == 202
    job = json.loads(body)
    assert job["status"] in {"queued", "running"}
    finished = None
    started = time.monotonic()
    http_wait_seconds = 30
    while time.monotonic() - started < http_wait_seconds:
        status, body = _http(bench_server, "GET", f"/api/jobs/{job['id']}")
        assert status == 200
        finished = json.loads(body)
        if finished["status"] in {"succeeded", "failed", "cancelled"}:
            break
        time.sleep(0.05)
    assert finished["status"] == "succeeded"
    assert 0.0 <= finished["metrics"]["test_accuracy"] <= 1.0
    status, png = _http(
        bench_server, "GET", f"/api/jobs/{job['id']}/figures/scores.png"
    )
    assert status == 200
    assert png.startswith(_PNG_SIGNATURE)
    assert len(png) > _MINIMUM_PNG_BYTES


def test_http_rejects_an_unknown_dataset(bench_server):
    status, body = _http(
        bench_server,
        "POST",
        "/api/jobs",
        {"dataset": "missing", "estimator": "logistic_regression"},
    )
    assert status == 400
    assert "dataset" in json.loads(body)["error"]


def test_http_missing_job_is_not_found(bench_server):
    status, body = _http(bench_server, "GET", "/api/jobs/0123456789ab")
    assert status == 404
    assert b"error" in body


def test_http_static_escape_is_not_found(bench_server):
    status, _body = _http(bench_server, "GET", "/static/../catalog.py")
    assert status == 404
