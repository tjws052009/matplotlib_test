"""Background runner for learning jobs.

A call to :meth:`TaskRunner.submit` returns as soon as the job is queued.
The fit runs on a worker thread, and the page polls for status and figures.
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from concurrent.futures import Executor, ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from ml_studio.catalog import validate_request
from ml_studio.train import TrainResult, fit_job

_MAX_WORKERS = 4
_DEFAULT_MAX_JOBS = 24
_TERMINAL = {"succeeded", "failed", "cancelled"}


class TaskRunner:
    """Queue learning jobs and run them off the request thread."""

    def __init__(
        self,
        max_workers: int = 2,
        *,
        max_jobs: int = _DEFAULT_MAX_JOBS,
        executor: Executor | None = None,
        fit: Callable[[dict[str, Any]], TrainResult] | None = None,
    ) -> None:
        if max_workers < 1 or max_workers > _MAX_WORKERS:
            raise ValueError(f"workers must be from 1 to {_MAX_WORKERS}.")
        if max_jobs < 1:
            raise ValueError("max_jobs must be at least 1.")
        self._fit = fit or fit_job
        self._max_jobs = max_jobs
        self._executor = executor or ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="ml-studio"
        )
        self._lock = threading.Lock()
        self._jobs: dict[str, dict[str, Any]] = {}
        self._order: list[str] = []

    def submit(self, payload: dict[str, Any]) -> str:
        """
        Validate a request, queue it, and return the job id.

        Parameters
        ----------
        payload : dict
            Dataset, estimator, and parameters from the page.

        Returns
        -------
        str
            Id used to poll status and fetch figures.

        Raises
        ------
        ValueError
            The request is not in the catalog or a parameter is out of range.
        RuntimeError
            Every retained job is still queued or running.
        """
        request = validate_request(payload)
        job_id = uuid.uuid4().hex[:12]
        job = {
            "id": job_id,
            "status": "queued",
            "stage": "queued",
            "created_at": _now(),
            "started_at": None,
            "finished_at": None,
            "request": request,
            "metrics": None,
            "figures": [],
            "_figures": {},
            "error": None,
            "cancel_event": threading.Event(),
            "done": threading.Event(),
        }
        with self._lock:
            self._make_room()
            self._jobs[job_id] = job
            self._order.append(job_id)
        self._executor.submit(self._run, job_id)
        return job_id

    def get(self, job_id: str) -> dict[str, Any]:
        """Return a JSON-safe snapshot of one job."""
        with self._lock:
            return self._public(self._jobs[job_id])

    def list_jobs(self) -> list[dict[str, Any]]:
        """Return snapshots, newest job first."""
        with self._lock:
            ordered = reversed(self._order)
            return [self._public(self._jobs[job_id]) for job_id in ordered]

    def figure(self, job_id: str, name: str) -> bytes:
        """Return PNG bytes for one named figure."""
        with self._lock:
            job = self._jobs[job_id]
            try:
                return job["_figures"][name]
            except KeyError as exc:
                raise KeyError(name) from exc

    def cancel(self, job_id: str) -> dict[str, Any]:
        """
        Cancel a job that has not finished.

        A queued job never starts its fit. A job that is already inside
        ``fit`` finishes that call, then discards the figures.
        """
        with self._lock:
            job = self._jobs[job_id]
            if job["status"] not in _TERMINAL:
                job["cancel_event"].set()
                if job["status"] == "queued":
                    self._finish(job, "cancelled", error=None)
            return self._public(job)

    def wait(self, job_id: str, timeout: float) -> dict[str, Any]:
        """Block until the job reaches a terminal status, then return it."""
        with self._lock:
            done = self._jobs[job_id]["done"]
        if not done.wait(timeout):
            raise TimeoutError(f"job {job_id} did not finish")
        return self.get(job_id)

    def shutdown(self, wait: bool = True) -> None:
        """Stop the worker pool. Queued jobs are not started after this."""
        self._executor.shutdown(wait=wait)

    def _run(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            if job["cancel_event"].is_set():
                self._finish(job, "cancelled", error=None)
                return
            request = job["request"]
            job["status"] = "running"
            job["stage"] = "fitting"
            job["started_at"] = _now()
        try:
            result = self._fit(request)
        except Exception as exc:
            with self._lock:
                job = self._jobs[job_id]
                if job["cancel_event"].is_set():
                    self._finish(job, "cancelled", error=None)
                else:
                    self._finish(job, "failed", error=str(exc))
            return
        with self._lock:
            job = self._jobs[job_id]
            if job["cancel_event"].is_set():
                self._finish(job, "cancelled", error=None)
                return
            job["metrics"] = result.metrics
            job["_figures"] = dict(result.figures)
            job["figures"] = list(result.figures)
            self._finish(job, "succeeded", error=None)

    def _make_room(self) -> None:
        """Drop oldest finished jobs, or refuse when every slot is still active."""
        while len(self._order) >= self._max_jobs:
            finished = [
                job_id
                for job_id in self._order
                if self._jobs[job_id]["status"] in _TERMINAL
            ]
            if not finished:
                raise RuntimeError(
                    "Too many learning jobs are in flight. "
                    "Wait for one to finish or cancel it."
                )
            oldest = finished[0]
            del self._jobs[oldest]
            self._order.remove(oldest)

    def _finish(self, job: dict[str, Any], status: str, error: str | None) -> None:
        if job["done"].is_set():
            return
        job["status"] = status
        job["stage"] = status
        job["error"] = error
        job["finished_at"] = _now()
        job["done"].set()

    def _public(self, job: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": job["id"],
            "status": job["status"],
            "stage": job["stage"],
            "created_at": job["created_at"],
            "started_at": job["started_at"],
            "finished_at": job["finished_at"],
            "request": job["request"],
            "metrics": job["metrics"],
            "figures": list(job["figures"]),
            "error": job["error"],
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
