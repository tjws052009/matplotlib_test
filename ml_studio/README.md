# Learning bench

A local page for fitting a scikit-learn model and reading the result as Matplotlib figures. The HTTP request returns as soon as the job is queued. A worker thread runs the fit, and the page polls until the figures are ready.

## Run

From the repository root:

```bash
pip install -r ml_studio/requirements.txt
python -m ml_studio
```

Open http://127.0.0.1:47321. Use `--host` and `--port` to bind somewhere else. `--workers` is how many fits may run at once (1 to 4).

scikit-learn >= 1.4 is required to run the bench. Importing Matplotlib does not import scikit-learn.

## Tests

```bash
pytest ml_studio/tests/test_learning_bench.py
```
