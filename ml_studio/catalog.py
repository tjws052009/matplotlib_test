"""Datasets and estimators the learning bench can fit."""

from __future__ import annotations

import copy
from typing import Any

# John Hunter's birthday, the seed Matplotlib tests use.
_DEFAULT_SEED = 19680801


def _int(name: str, label: str, default: int, low: int, high: int) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "type": "int",
        "default": default,
        "min": low,
        "max": high,
    }


def _optional_int(
    name: str, label: str, default: int, low: int, high: int
) -> dict[str, Any]:
    spec = _int(name, label, default, low, high)
    spec["nullable"] = True
    return spec


def _float(
    name: str,
    label: str,
    default: float,
    low: float,
    high: float,
    *,
    step: float,
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "type": "float",
        "default": default,
        "min": low,
        "max": high,
        "step": step,
    }


def _bool(name: str, label: str, default: bool) -> dict[str, Any]:
    return {"name": name, "label": label, "type": "bool", "default": default}


def _choice(
    name: str, label: str, default: str, choices: list[str]
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "type": "choice",
        "default": default,
        "choices": list(choices),
    }


_CATALOG: dict[str, Any] = {
    "tasks": [
        {"id": "classification", "label": "Classification"},
        {"id": "regression", "label": "Regression"},
    ],
    "shared_parameters": [
        _float("test_size", "Test fraction", 0.25, 0.1, 0.5, step=0.05),
        _int("random_state", "Random seed", _DEFAULT_SEED, 0, 2_147_483_647),
    ],
    "datasets": [
        {
            "id": "iris",
            "label": "Iris",
            "task": "classification",
            "description": "Three iris species and four measurements.",
            "parameters": [],
        },
        {
            "id": "wine",
            "label": "Wine",
            "task": "classification",
            "description": "Chemical analysis of wines from three cultivars.",
            "parameters": [],
        },
        {
            "id": "breast_cancer",
            "label": "Breast cancer",
            "task": "classification",
            "description": "Diagnostic features labeled benign or malignant.",
            "parameters": [],
        },
        {
            "id": "digits",
            "label": "Digits",
            "task": "classification",
            "description": "8×8 images of handwritten digits.",
            "parameters": [],
        },
        {
            "id": "moons",
            "label": "Two moons",
            "task": "classification",
            "description": "Two interlocking crescents in a plane.",
            "parameters": [
                _int("n_samples", "Samples", 300, 80, 800),
                _float("noise", "Noise", 0.15, 0.0, 0.5, step=0.01),
            ],
        },
        {
            "id": "circles",
            "label": "Circles",
            "task": "classification",
            "description": "One class as a ring around the other.",
            "parameters": [
                _int("n_samples", "Samples", 300, 80, 800),
                _float("noise", "Noise", 0.08, 0.0, 0.3, step=0.01),
            ],
        },
        {
            "id": "blobs",
            "label": "Blobs",
            "task": "classification",
            "description": "Round clusters. A clear decision boundary.",
            "parameters": [
                _int("n_samples", "Samples", 240, 80, 800),
                _float("cluster_std", "Cluster spread", 1.2, 0.3, 3.0, step=0.1),
            ],
        },
        {
            "id": "diabetes",
            "label": "Diabetes",
            "task": "regression",
            "description": "Baseline measurements and a progression score.",
            "parameters": [],
        },
        {
            "id": "synthetic_regression",
            "label": "Synthetic regression",
            "task": "regression",
            "description": "A linear target plus noise, four informative features.",
            "parameters": [
                _int("n_samples", "Samples", 240, 80, 800),
                _float("noise", "Noise", 8.0, 0.0, 40.0, step=0.5),
            ],
        },
    ],
    "estimators": [
        {
            "id": "logistic_regression",
            "label": "Logistic regression",
            "task": "classification",
            "description": "Linear decision boundary with an L2 penalty.",
            "parameters": [
                _float("C", "Inverse regularization", 1.0, 0.001, 100.0, step=0.001),
                _int("max_iter", "Maximum iterations", 200, 50, 500),
            ],
        },
        {
            "id": "linear_svc",
            "label": "Linear SVM",
            "task": "classification",
            "description": "Support vectors with a linear kernel.",
            "parameters": [
                _float("C", "Penalty", 1.0, 0.001, 100.0, step=0.001),
                _int("max_iter", "Maximum iterations", 200, 50, 500),
            ],
        },
        {
            "id": "knn",
            "label": "k-nearest neighbors",
            "task": "classification",
            "description": "Label a point from the nearest training rows.",
            "parameters": [
                _int("n_neighbors", "Neighbors", 5, 1, 30),
                _choice("weights", "Weights", "uniform", ["uniform", "distance"]),
            ],
        },
        {
            "id": "decision_tree",
            "label": "Decision tree",
            "task": "classification",
            "description": "Axis-aligned splits. Depth limits overfitting.",
            "parameters": [
                _optional_int("max_depth", "Maximum depth", 4, 1, 20),
                _int("min_samples_leaf", "Minimum leaf size", 1, 1, 20),
            ],
        },
        {
            "id": "random_forest",
            "label": "Random forest",
            "task": "classification",
            "description": "A vote across many shallow trees.",
            "parameters": [
                _int("n_estimators", "Trees", 40, 10, 200),
                _optional_int("max_depth", "Maximum depth", 6, 1, 20),
            ],
        },
        {
            "id": "gradient_boosting",
            "label": "Gradient boosting",
            "task": "classification",
            "description": "Trees added to correct the current residual.",
            "parameters": [
                _int("n_estimators", "Trees", 50, 10, 200),
                _float("learning_rate", "Learning rate", 0.1, 0.01, 1.0, step=0.01),
                _int("max_depth", "Maximum depth", 3, 1, 8),
            ],
        },
        {
            "id": "gaussian_nb",
            "label": "Gaussian naive Bayes",
            "task": "classification",
            "description": "Each class is a Gaussian, features treated as independent.",
            "parameters": [
                _float(
                    "var_smoothing",
                    "Variance smoothing",
                    1e-9,
                    1e-12,
                    1e-6,
                    step=1e-12,
                ),
            ],
        },
        {
            "id": "linear_regression",
            "label": "Linear regression",
            "task": "regression",
            "description": "Ordinary least squares.",
            "parameters": [
                _bool("fit_intercept", "Fit intercept", True),
            ],
        },
        {
            "id": "ridge",
            "label": "Ridge regression",
            "task": "regression",
            "description": "Least squares with an L2 penalty.",
            "parameters": [
                _float("alpha", "Penalty", 1.0, 0.001, 100.0, step=0.001),
            ],
        },
        {
            "id": "knn_regressor",
            "label": "k-nearest neighbors",
            "task": "regression",
            "description": "Average the targets of the nearest training rows.",
            "parameters": [
                _int("n_neighbors", "Neighbors", 5, 1, 30),
                _choice("weights", "Weights", "uniform", ["uniform", "distance"]),
            ],
        },
        {
            "id": "decision_tree_regressor",
            "label": "Decision tree",
            "task": "regression",
            "description": "Predict with the mean of the leaf.",
            "parameters": [
                _optional_int("max_depth", "Maximum depth", 4, 1, 20),
                _int("min_samples_leaf", "Minimum leaf size", 1, 1, 20),
            ],
        },
        {
            "id": "random_forest_regressor",
            "label": "Random forest",
            "task": "regression",
            "description": "Average many trees grown on resampled rows.",
            "parameters": [
                _int("n_estimators", "Trees", 40, 10, 200),
                _optional_int("max_depth", "Maximum depth", 6, 1, 20),
            ],
        },
        {
            "id": "gradient_boosting_regressor",
            "label": "Gradient boosting",
            "task": "regression",
            "description": "Trees fit to the remaining error.",
            "parameters": [
                _int("n_estimators", "Trees", 50, 10, 200),
                _float("learning_rate", "Learning rate", 0.1, 0.01, 1.0, step=0.01),
                _int("max_depth", "Maximum depth", 3, 1, 8),
            ],
        },
    ],
}


def catalog() -> dict[str, Any]:
    """
    Return datasets, estimators, and the parameters the bench accepts.

    Returns
    -------
    dict
        A copy of the catalog. Callers can edit it without changing later calls.
    """
    return copy.deepcopy(_CATALOG)


def validate_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Check a learning-job request and fill omitted parameters.

    Parameters
    ----------
    payload : dict
        Dataset, estimator, and parameter values from the page or a caller.

    Returns
    -------
    dict
        The request the runner stores and fits. Labels are taken from the
        catalog, not from the payload.
    """
    if not isinstance(payload, dict):
        raise ValueError("A learning job must be a JSON object.")
    unknown = sorted(set(payload) - _INPUT_KEYS)
    if unknown:
        names = ", ".join(unknown)
        raise ValueError(f"Unknown field: {names}.")
    dataset_id = payload.get("dataset")
    estimator_id = payload.get("estimator")
    if not isinstance(dataset_id, str) or not dataset_id:
        raise ValueError("A dataset is required.")
    if not isinstance(estimator_id, str) or not estimator_id:
        raise ValueError("An estimator is required.")
    dataset = dataset_by_id(dataset_id)
    estimator = estimator_by_id(estimator_id)
    if dataset is None:
        raise ValueError(f"Unknown dataset '{dataset_id}'.")
    if estimator is None:
        raise ValueError(f"Unknown estimator '{estimator_id}'.")
    if estimator["task"] != dataset["task"]:
        raise ValueError(
            f"Estimator '{estimator_id}' is a {estimator['task']} model and "
            f"cannot fit dataset '{dataset_id}'."
        )
    shared = {item["name"]: item for item in _CATALOG["shared_parameters"]}
    return {
        "dataset": dataset_id,
        "dataset_label": dataset["label"],
        "estimator": estimator_id,
        "estimator_label": estimator["label"],
        "task": dataset["task"],
        "dataset_parameters": _parameters(
            payload.get("dataset_parameters"), dataset["parameters"], "dataset"
        ),
        "parameters": _parameters(
            payload.get("parameters"), estimator["parameters"], "estimator"
        ),
        "test_size": _one(
            payload.get("test_size", shared["test_size"]["default"]),
            shared["test_size"],
        ),
        "random_state": _one(
            payload.get("random_state", shared["random_state"]["default"]),
            shared["random_state"],
        ),
    }


def dataset_by_id(dataset_id: str) -> dict[str, Any] | None:
    """Return one dataset record, or None when the id is not in the catalog."""
    for item in _CATALOG["datasets"]:
        if item["id"] == dataset_id:
            return item
    return None


def estimator_by_id(estimator_id: str) -> dict[str, Any] | None:
    """Return one estimator record, or None when the id is not in the catalog."""
    for item in _CATALOG["estimators"]:
        if item["id"] == estimator_id:
            return item
    return None


def _parameters(raw: Any, specs: list[dict[str, Any]], owner: str) -> dict[str, Any]:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{owner} parameters must be an object.")
    known = {spec["name"]: spec for spec in specs}
    unknown = sorted(set(raw) - set(known))
    if unknown:
        names = ", ".join(unknown)
        raise ValueError(f"Unknown {owner} parameter: {names}.")
    values = {}
    for name, spec in known.items():
        values[name] = _one(raw.get(name, spec["default"]), spec)
    return values


def _one(value: Any, spec: dict[str, Any]) -> Any:
    kind = spec["type"]
    if kind == "int":
        return _as_int(value, spec)
    if kind == "float":
        return _as_float(value, spec)
    if kind == "bool":
        if not isinstance(value, bool):
            raise ValueError(f"{spec['name']} must be true or false.")
        return value
    if kind == "choice":
        if value not in spec["choices"]:
            choices = ", ".join(spec["choices"])
            raise ValueError(f"{spec['name']} must be one of: {choices}.")
        return value
    raise ValueError(f"{spec['name']} has an unsupported type.")


def _as_int(value: Any, spec: dict[str, Any]) -> int | None:
    if value is None and spec.get("nullable"):
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{spec['name']} must be an integer.")
    if value < spec["min"] or value > spec["max"]:
        raise ValueError(
            f"{spec['name']} must be between {spec['min']} and {spec['max']}."
        )
    return value


def _as_float(value: Any, spec: dict[str, Any]) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{spec['name']} must be a number.")
    number = float(value)
    if number < spec["min"] or number > spec["max"]:
        raise ValueError(
            f"{spec['name']} must be between {spec['min']} and {spec['max']}."
        )
    return number


_INPUT_KEYS = {
    "dataset",
    "dataset_label",
    "dataset_parameters",
    "estimator",
    "estimator_label",
    "parameters",
    "random_state",
    "task",
    "test_size",
}
