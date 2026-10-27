---
name: run-matplotlib-regression
description: Run Matplotlib's pytest suite, or one test, to check a regression. Covers the local build on this fork, xvfb, leaving MPLBACKEND unset, tkinter, and comparing a failure with the last known good version. Use when the user asks to run tests, run the suite, or check a regression.
---

# Run a regression test

The testing guide is `doc/devel/testing.rst`. Writing a new test is `write-matplotlib-tests`. This skill is only for running tests that already exist.

The `Tests` and `Windows tests` workflows run only when `github.repository` is `matplotlib/matplotlib`. On this fork they do not start. Run pytest in the checkout.

## One test

From the repository root, with the editable install on `PATH`:

```bash
pytest lib/matplotlib/tests/test_simplification.py::test_clipping
```

Do not set `MPLBACKEND`. The `mpl_test_settings` fixture selects the backend. Forcing `Agg` makes `test_backends_interactive.py::test_lazy_auto_backend_selection` fail even when the library is fine.

`python -m pytest` needs `-P`, so the current directory is not on the import path.

## Full suite

```bash
xvfb-run -a pytest -n 2 --tb=line --timeout=180
```

A run on this machine collected 10,609 tests and finished in about two minutes: 9,000 passed, 1,579 skipped, 29 xfailed. Skips are optional GUI libraries and tests gated on `MPL_TEST_EXPENSIVE`. Set that variable only when the user asked for the expensive tests.

Report passed, failed, skipped, and xfailed, and list every failed node id with the first error line. Do not call the tree clean while a failure is unexplained.

## If import matplotlib fails

This machine's `c++` is clang and cannot link `libstdc++`. Use `g++`. Also install `libfreetype6-dev`, `libpng-dev`, `ninja-build`, `pkg-config`, `python3-tk`, and `xvfb`.

```bash
python3 -m venv /tmp/mpl-venv
/tmp/mpl-venv/bin/pip install -U pip
export PATH=/tmp/mpl-venv/bin:$PATH CC=gcc CXX=g++
pip install --group build --group test --group test-extra
pip install --no-build-isolation --editable .
```

`python3-tk` is required for `test_pickle.py::test_axeswidget_interactive`.

## Compare with the last good version

1. Run the node id on the current checkout and keep the traceback.
2. Use the last known good version the user named. If they did not name one, ask. Do not invent a version.
3. Check that tag or commit out in a second directory, install it the same way, and run the same node id. Do not set `MPLBACKEND` on either side.
4. Report which side fails. A regression fails now and passed then.

## After a code change

Run the new or affected test first. If it passes, run that test module. Run the full suite before calling the change free of regressions.
