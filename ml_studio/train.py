"""Fit one scikit-learn estimator and draw its Matplotlib figures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.datasets import (
    load_breast_cancer,
    load_diabetes,
    load_digits,
    load_iris,
    load_wine,
    make_blobs,
    make_circles,
    make_moons,
    make_regression,
)
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from ml_studio.catalog import validate_request
from ml_studio.plots import render_figures


@dataclass
class TrainResult:
    """Metrics and PNG figures from one fit."""

    metrics: dict[str, Any]
    figures: dict[str, bytes]


@dataclass
class _Plane:
    train_xy: np.ndarray
    test_xy: np.ndarray
    xlabel: str
    ylabel: str
    predict: Any
    y_residual: np.ndarray | None = None


def fit_job(request: dict[str, Any]) -> TrainResult:
    """
    Fit the requested estimator and return scores plus PNG figures.

    Parameters
    ----------
    request : dict
        A learning-job payload. It is validated again here so a direct caller
        cannot skip the catalog limits.

    Returns
    -------
    TrainResult
        JSON-safe metrics and the figure bytes keyed by name.
    """
    request = validate_request(request)
    features, target, feature_names, class_names = _load(request)
    x_train, x_test, y_train, y_test = _split(request, features, target)
    estimator = _estimator(request)
    estimator.fit(x_train, y_train)
    train_pred = estimator.predict(x_train)
    test_pred = estimator.predict(x_test)
    metrics = _metrics(
        request["task"], y_train, train_pred, y_test, test_pred, class_names
    )
    metrics["n_train"] = int(len(y_train))
    metrics["n_test"] = int(len(y_test))
    metrics["n_features"] = int(features.shape[1])
    plane = _plane(
        estimator,
        x_train,
        x_test,
        y_test,
        test_pred,
        feature_names,
        request["random_state"],
        request["task"],
    )
    figures = render_figures(
        task=request["task"],
        metrics=metrics,
        estimator=estimator,
        plane=plane,
        y_test=y_test,
        y_test_pred=test_pred,
        feature_names=feature_names,
        class_names=class_names,
    )
    return TrainResult(metrics=metrics, figures=figures)


def _load(
    request: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, list[str], list[str] | None]:
    dataset_id = request["dataset"]
    options = request["dataset_parameters"]
    seed = request["random_state"]
    if dataset_id == "iris":
        bunch = load_iris()
        return _loaded(bunch)
    if dataset_id == "wine":
        bunch = load_wine()
        return _loaded(bunch)
    if dataset_id == "breast_cancer":
        bunch = load_breast_cancer()
        return _loaded(bunch)
    if dataset_id == "digits":
        bunch = load_digits()
        names = [f"pixel {index}" for index in range(bunch.data.shape[1])]
        classes = [str(name) for name in bunch.target_names]
        return _arrays(bunch.data, bunch.target, names, classes)
    if dataset_id == "diabetes":
        bunch = load_diabetes()
        return _arrays(bunch.data, bunch.target, list(bunch.feature_names), None)
    if dataset_id == "moons":
        features, target = make_moons(
            n_samples=options["n_samples"], noise=options["noise"], random_state=seed
        )
        return _arrays(features, target, ["x", "y"], ["Class 0", "Class 1"])
    if dataset_id == "circles":
        features, target = make_circles(
            n_samples=options["n_samples"],
            noise=options["noise"],
            factor=0.5,
            random_state=seed,
        )
        return _arrays(features, target, ["x", "y"], ["Class 0", "Class 1"])
    if dataset_id == "blobs":
        features, target = make_blobs(
            n_samples=options["n_samples"],
            centers=3,
            n_features=2,
            cluster_std=options["cluster_std"],
            random_state=seed,
        )
        return _arrays(features, target, ["x", "y"], ["Class 0", "Class 1", "Class 2"])
    if dataset_id == "synthetic_regression":
        features, target = make_regression(
            n_samples=options["n_samples"],
            n_features=4,
            n_informative=4,
            noise=options["noise"],
            random_state=seed,
        )
        return _arrays(features, target, ["x0", "x1", "x2", "x3"], None)
    raise ValueError(f"Unknown dataset '{dataset_id}'.")


def _arrays(
    features: Any,
    target: Any,
    feature_names: list[str],
    class_names: list[str] | None,
) -> tuple[np.ndarray, np.ndarray, list[str], list[str] | None]:
    return (
        np.asarray(features, dtype=float),
        np.asarray(target),
        feature_names,
        class_names,
    )


def _loaded(bunch: Any) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    return _arrays(
        bunch.data,
        bunch.target,
        list(bunch.feature_names),
        list(bunch.target_names),
    )


def _split(
    request: dict[str, Any], features: np.ndarray, target: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    kwargs: dict[str, Any] = {
        "test_size": request["test_size"],
        "random_state": request["random_state"],
    }
    if request["task"] == "classification":
        kwargs["stratify"] = target
    try:
        return train_test_split(features, target, **kwargs)
    except ValueError:
        kwargs.pop("stratify", None)
        return train_test_split(features, target, **kwargs)


def _estimator(request: dict[str, Any]) -> Any:
    parameters = request["parameters"]
    seed = request["random_state"]
    estimator_id = request["estimator"]
    if estimator_id == "logistic_regression":
        return LogisticRegression(
            C=parameters["C"], max_iter=parameters["max_iter"], solver="lbfgs"
        )
    if estimator_id == "linear_svc":
        return LinearSVC(C=parameters["C"], max_iter=parameters["max_iter"])
    if estimator_id == "knn":
        return KNeighborsClassifier(
            n_neighbors=parameters["n_neighbors"], weights=parameters["weights"]
        )
    if estimator_id == "decision_tree":
        return DecisionTreeClassifier(
            max_depth=parameters["max_depth"],
            min_samples_leaf=parameters["min_samples_leaf"],
            random_state=seed,
        )
    if estimator_id == "random_forest":
        return RandomForestClassifier(
            n_estimators=parameters["n_estimators"],
            max_depth=parameters["max_depth"],
            random_state=seed,
            n_jobs=1,
        )
    if estimator_id == "gradient_boosting":
        return GradientBoostingClassifier(
            n_estimators=parameters["n_estimators"],
            learning_rate=parameters["learning_rate"],
            max_depth=parameters["max_depth"],
            random_state=seed,
        )
    if estimator_id == "gaussian_nb":
        return GaussianNB(var_smoothing=parameters["var_smoothing"])
    if estimator_id == "linear_regression":
        return LinearRegression(fit_intercept=parameters["fit_intercept"])
    if estimator_id == "ridge":
        return Ridge(alpha=parameters["alpha"])
    if estimator_id == "knn_regressor":
        return KNeighborsRegressor(
            n_neighbors=parameters["n_neighbors"], weights=parameters["weights"]
        )
    if estimator_id == "decision_tree_regressor":
        return DecisionTreeRegressor(
            max_depth=parameters["max_depth"],
            min_samples_leaf=parameters["min_samples_leaf"],
            random_state=seed,
        )
    if estimator_id == "random_forest_regressor":
        return RandomForestRegressor(
            n_estimators=parameters["n_estimators"],
            max_depth=parameters["max_depth"],
            random_state=seed,
            n_jobs=1,
        )
    if estimator_id == "gradient_boosting_regressor":
        return GradientBoostingRegressor(
            n_estimators=parameters["n_estimators"],
            learning_rate=parameters["learning_rate"],
            max_depth=parameters["max_depth"],
            random_state=seed,
        )
    raise ValueError(f"Unknown estimator '{estimator_id}'.")


def _metrics(
    task: str,
    y_train: np.ndarray,
    train_pred: np.ndarray,
    y_test: np.ndarray,
    test_pred: np.ndarray,
    class_names: list[str] | None,
) -> dict[str, Any]:
    if task == "classification":
        classes = [str(name) for name in class_names] if class_names else []
        return {
            "task": task,
            "train_accuracy": float(accuracy_score(y_train, train_pred)),
            "test_accuracy": float(accuracy_score(y_test, test_pred)),
            "train_f1_macro": float(f1_score(y_train, train_pred, average="macro")),
            "test_f1_macro": float(f1_score(y_test, test_pred, average="macro")),
            "classes": classes,
        }
    return {
        "task": task,
        "train_r2": float(r2_score(y_train, train_pred)),
        "test_r2": float(r2_score(y_test, test_pred)),
        "train_mae": float(mean_absolute_error(y_train, train_pred)),
        "test_mae": float(mean_absolute_error(y_test, test_pred)),
    }


def _plane(
    estimator: Any,
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    test_pred: np.ndarray,
    feature_names: list[str],
    random_state: int,
    task: str,
) -> _Plane | None:
    residual = np.abs(y_test - test_pred) if task == "regression" else None
    if x_train.shape[1] == 2:
        return _Plane(
            train_xy=x_train,
            test_xy=x_test,
            xlabel=feature_names[0],
            ylabel=feature_names[1],
            predict=estimator.predict,
            y_residual=residual,
        )
    if x_train.shape[1] < 2:
        return None
    pca = PCA(n_components=2, random_state=random_state)
    train_xy = pca.fit_transform(x_train)
    test_xy = pca.transform(x_test)

    def predict(coordinates: np.ndarray) -> np.ndarray:
        return estimator.predict(pca.inverse_transform(coordinates))

    return _Plane(
        train_xy=train_xy,
        test_xy=test_xy,
        xlabel="Component 1",
        ylabel="Component 2",
        predict=predict,
        y_residual=residual,
    )
