"""Matplotlib figures for one finished learning job."""

from __future__ import annotations

import io
from typing import Any

import numpy as np

import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

INK = "#1c1915"
TRAIN = "#0f4c5c"
TEST = "#c4491d"
PAPER = "#fbf8f3"
_MAX_IMPORTANCE_ROWS = 15


def render_figures(
    *,
    task: str,
    metrics: dict[str, Any],
    estimator: Any,
    plane: Any,
    y_test: np.ndarray,
    y_test_pred: np.ndarray,
    feature_names: list[str],
    class_names: list[str] | None,
) -> dict[str, bytes]:
    """
    Draw the figures for a fitted model.

    Parameters
    ----------
    task : str
        ``'classification'`` or ``'regression'``.
    metrics : dict
        Scores already computed on the train and test splits.
    estimator : estimator
        Fitted scikit-learn estimator. Used for feature weights.
    plane : plane or None
        Two-dimensional coordinates and a callable that predicts on that plane.
    y_test, y_test_pred : array
        Held-out targets and the model's predictions.
    feature_names : list of str
        Names parallel to the training columns.
    class_names : list of str or None
        Class labels for a classifier. None for regression.

    Returns
    -------
    dict
        Figure name to PNG bytes.
    """
    figures = {"scores": _scores(task, metrics)}
    if task == "classification":
        figures["confusion"] = _confusion(y_test, y_test_pred, class_names or [])
    else:
        figures["predicted"] = _predicted(y_test, y_test_pred)
        figures["residuals"] = _residuals(y_test, y_test_pred)
    if plane is not None:
        figures["projection"] = _projection(
            task, plane, y_test, class_names
        )
    weights = _weights(estimator, feature_names)
    if weights is not None:
        figures["importance"] = _importance(*weights)
    return figures


def _new_figure(height: float = 4.0, *, width: float = 6.4) -> Figure:
    fig = Figure(figsize=(width, height), dpi=110, layout="constrained")
    FigureCanvasAgg(fig)
    fig.patch.set_facecolor(PAPER)
    return fig


def _png(fig: Figure) -> bytes:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    return buffer.getvalue()


def _style(ax: Any) -> None:
    ax.set_facecolor("#fffdf9")
    ax.grid(True, color="#e4ddd2", linewidth=0.6)
    ax.tick_params(colors=INK, labelsize=8)
    ax.title.set_color(INK)
    ax.xaxis.label.set_color(INK)
    ax.yaxis.label.set_color(INK)
    for spine in ax.spines.values():
        spine.set_color("#d9d0c4")


def _scores(task: str, metrics: dict[str, Any]) -> bytes:
    return _png(_scores_figure(task, metrics))


def _scores_figure(task: str, metrics: dict[str, Any]) -> Figure:
    if task == "classification":
        # Accuracy and F1 are both fractions, so they share one 0–1 axis.
        fig = _new_figure()
        ax = fig.add_subplot(1, 1, 1)
        _paired_bars(
            ax,
            ["Accuracy", "F1 (macro)"],
            [metrics["train_accuracy"], metrics["train_f1_macro"]],
            [metrics["test_accuracy"], metrics["test_f1_macro"]],
        )
        ax.set_ylim(0.0, 1.0)
        ax.set_title(f"Test accuracy {metrics['test_accuracy']:.3f}")
        _style(ax)
        return fig
    # R² and mean absolute error do not share a unit, so each has its own axis.
    fig = _new_figure(width=7.2)
    ax_r2 = fig.add_subplot(1, 2, 1)
    ax_mae = fig.add_subplot(1, 2, 2)
    _paired_bars(
        ax_r2,
        ["R²"],
        [metrics["train_r2"]],
        [metrics["test_r2"]],
    )
    _paired_bars(
        ax_mae,
        ["Mean absolute error"],
        [metrics["train_mae"]],
        [metrics["test_mae"]],
    )
    ax_r2.set_title("R²")
    ax_mae.set_title("Mean absolute error")
    _style(ax_r2)
    _style(ax_mae)
    return fig


def _paired_bars(
    ax: Any, labels: list[str], train: list[float], test: list[float]
) -> None:
    positions = np.arange(len(labels))
    width = 0.36
    ax.bar(positions - width / 2, train, width=width, color=TRAIN, label="Train")
    ax.bar(positions + width / 2, test, width=width, color=TEST, label="Test")
    ax.set_xticks(positions, labels)
    ax.legend(frameon=False)


def _confusion(
    y_test: np.ndarray, y_pred: np.ndarray, class_names: list[str]
) -> bytes:
    classes = np.unique(np.concatenate([y_test, y_pred]))
    index = {label: position for position, label in enumerate(classes)}
    matrix = np.zeros((len(classes), len(classes)), dtype=int)
    for actual, predicted in zip(y_test, y_pred):
        matrix[index[actual], index[predicted]] += 1
    names = [
        class_names[int(label)] if int(label) < len(class_names) else str(label)
        for label in classes
    ]
    fig = _new_figure()
    ax = fig.add_subplot(1, 1, 1)
    image = ax.imshow(matrix, cmap=mpl.colormaps["Blues"])
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    ax.set_xticks(range(len(names)), names, rotation=45, ha="right")
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion matrix")
    peak = max(int(matrix.max()), 1)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            count = int(matrix[row, column])
            color = "white" if count > peak / 2 else INK
            ax.text(
                column,
                row,
                str(count),
                ha="center",
                va="center",
                color=color,
                fontsize=8,
            )
    _style(ax)
    ax.grid(False)
    return _png(fig)


def _predicted(y_test: np.ndarray, y_pred: np.ndarray) -> bytes:
    fig = _new_figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(
        y_test,
        y_pred,
        s=22,
        color=TRAIN,
        alpha=0.85,
        edgecolor="white",
        linewidth=0.4,
    )
    low = float(min(np.min(y_test), np.min(y_pred)))
    high = float(max(np.max(y_test), np.max(y_pred)))
    ax.plot([low, high], [low, high], color=TEST, linewidth=1.2)
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title("Predicted against actual")
    _style(ax)
    return _png(fig)


def _residuals(y_test: np.ndarray, y_pred: np.ndarray) -> bytes:
    fig = _new_figure()
    ax = fig.add_subplot(1, 1, 1)
    residual = y_test - y_pred
    ax.hist(residual, bins=18, color=TEST, edgecolor="white")
    ax.axvline(0.0, color=INK, linewidth=1.0)
    ax.set_xlabel("Actual − predicted")
    ax.set_ylabel("Count")
    ax.set_title("Test residuals")
    _style(ax)
    return _png(fig)


def _projection(
    task: str, plane: Any, y_test: np.ndarray, class_names: list[str] | None
) -> bytes:
    fig = _new_figure()
    ax = fig.add_subplot(1, 1, 1)
    xy = plane.test_xy
    if task == "classification" and plane.predict is not None:
        _classification_plane(ax, plane, y_test, class_names or [])
    elif task == "classification":
        # A projection has no grid in the original columns. Color the true class.
        _class_scatter(ax, xy, y_test, class_names or [])
        ax.set_title("Test rows on two components")
    else:
        residual = np.abs(plane.y_residual)
        points = ax.scatter(
            xy[:, 0],
            xy[:, 1],
            c=residual,
            s=28,
            cmap=mpl.colormaps["cividis"],
            edgecolor="white",
            linewidth=0.3,
        )
        fig.colorbar(points, ax=ax, fraction=0.046, pad=0.04, label="|residual|")
        if plane.predict is None:
            ax.set_title("Test rows on two components")
        else:
            ax.set_title("Test rows")
    ax.set_xlabel(plane.xlabel)
    ax.set_ylabel(plane.ylabel)
    _style(ax)
    return _png(fig)


def _classification_plane(
    ax: Any, plane: Any, y_test: np.ndarray, class_names: list[str]
) -> None:
    xy = plane.test_xy
    pad = 0.08
    x_min, x_max = _padded_limits(xy[:, 0], pad)
    y_min, y_max = _padded_limits(xy[:, 1], pad)
    steps = 120
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, steps),
        np.linspace(y_min, y_max, steps),
    )
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    # predict is the model on these same two columns, not a reconstruction.
    predicted = np.asarray(plane.predict(grid))
    classes = np.unique(np.concatenate([y_test, predicted]))
    zz = np.searchsorted(classes, predicted).reshape(xx.shape)
    colors = _class_colors(len(classes))
    cmap = mpl.colors.ListedColormap(colors)
    ax.contourf(
        xx,
        yy,
        zz,
        levels=np.arange(len(classes) + 1) - 0.5,
        cmap=cmap,
        alpha=0.45,
    )
    _class_scatter(ax, xy, y_test, class_names, classes=classes, colors=colors)
    ax.set_title("Decision regions and test rows")


def _class_scatter(
    ax: Any,
    xy: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str],
    classes: np.ndarray | None = None,
    colors: list[Any] | None = None,
) -> None:
    if classes is None:
        classes = np.unique(y_test)
    if colors is None:
        colors = _class_colors(len(classes))
    show_legend = len(classes) <= 6
    for position, label in enumerate(classes):
        mask = y_test == label
        name = class_names[int(label)] if int(label) < len(class_names) else str(label)
        ax.scatter(
            xy[mask, 0],
            xy[mask, 1],
            s=22,
            color=colors[position],
            edgecolor="white",
            linewidth=0.4,
            label=name if show_legend else None,
            zorder=3,
        )
    if show_legend:
        ax.legend(frameon=False, fontsize=8)


def _padded_limits(values: np.ndarray, fraction: float) -> tuple[float, float]:
    low = float(np.min(values))
    high = float(np.max(values))
    span = high - low
    if span == 0:
        span = 1.0
    return low - fraction * span, high + fraction * span


def _class_colors(count: int) -> list[Any]:
    if count <= 10:
        cmap = mpl.colormaps["tab10"]
        return [cmap(index) for index in range(count)]
    cmap = mpl.colormaps["viridis"]
    return [cmap(index / max(count - 1, 1)) for index in range(count)]


def _weights(
    estimator: Any, feature_names: list[str]
) -> tuple[list[str], np.ndarray, str] | None:
    if hasattr(estimator, "feature_importances_"):
        values = np.asarray(estimator.feature_importances_, dtype=float)
        title = "Feature importance"
    elif hasattr(estimator, "coef_"):
        coef = np.asarray(estimator.coef_, dtype=float)
        values = np.mean(np.abs(coef), axis=0) if coef.ndim == 2 else np.abs(coef)
        title = "Mean |coefficient|"
    else:
        return None
    if values.shape != (len(feature_names),):
        return None
    names = list(feature_names)
    if len(values) > _MAX_IMPORTANCE_ROWS:
        keep = np.argsort(values)[-_MAX_IMPORTANCE_ROWS:]
        values = values[keep]
        names = [names[int(index)] for index in keep]
        title = f"Largest {_MAX_IMPORTANCE_ROWS} feature weights"
    return names, values, title


def _importance(names: list[str], values: np.ndarray, title: str) -> bytes:
    order = np.argsort(values)
    height = max(4.0, 0.32 * len(names) + 1.1)
    fig = _new_figure(height)
    ax = fig.add_subplot(1, 1, 1)
    ordered_names = [names[int(index)] for index in order]
    ax.barh(ordered_names, values[order], color=TRAIN)
    ax.set_xlabel("Weight")
    ax.set_title(title)
    _style(ax)
    return _png(fig)
