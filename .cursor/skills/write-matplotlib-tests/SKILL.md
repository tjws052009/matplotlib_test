---
name: write-matplotlib-tests
description: Write and review Matplotlib pytest tests to the testing guide at https://matplotlib.org/devdocs/devel/testing.html. Covers test file and function names, descriptive names, minimal explicit data, named tolerances instead of unexplained numbers, value assertions before image baselines, and the fixed random seed. Use when adding, editing, or reviewing tests, or when the user mentions test quality, naming conventions, or magic numbers.
---

# Write Matplotlib tests

Follow [the testing guide](https://matplotlib.org/devdocs/devel/testing.html). The copy in this checkout is `doc/devel/testing.rst`. If the page and the file disagree, follow the file.

## Place and names

Put a test for `lib/matplotlib/<module>.py` in `lib/matplotlib/tests/test_<module>.py`. Toolkit tests stay under that toolkit's `tests/` directory.

- Files start with `test_`.
- Functions start with `test_`.
- Classes start with `Test`. Prefer a function.
- The name states the behavior. A long name is fine: `test_to_rgba_array_accepts_color_alpha_tuple_with_multiple_colors`.
- Do not use `test_1`, `test_bar`, `test_ok`, or a name that only repeats the function under test.

## Data, and which numbers stay literal

Use the smallest explicit data that shows the behavior: `[1, 2, 3]`, `range(5)`, or `np.arange(5)`. Generate a longer series, for example `np.linspace` or a closed-form expression. Those literals are the sample. Leave them as literals.

Name a number when a reader cannot tell what it stands for. That includes tolerances, expected channel values, pixel `tol`, linewidths that are part of the contract, and indexes into a result.

```python
# ❌ BAD — 1e-12 and 0.4 are unexplained, and the name says nothing
def test_bar():
    bars = ax.bar([0, 1], [1, 2], width=[0.2, 0.4], align="edge")
    assert abs(bars[1].get_width() - 0.4) < 1e-12

# ✅ GOOD — the name is the behavior; the sample stays literal; the tolerance is named
def test_bar_keeps_each_width_when_align_is_edge():
    widths = [0.2, 0.4]
    absolute_tolerance = 1e-12
    bars = ax.bar([0, 1], [1, 2], width=widths, align="edge")
    assert [bar.get_width() for bar in bars] == pytest.approx(widths, abs=absolute_tolerance)
```

Use random numbers only when a formula cannot build the data. Then use one generator and this seed (John Hunter's birthday):

```python
rng = np.random.default_rng(19680801)
```

Do not call `np.random.seed` or the global `np.random` functions.

## What to assert

Arrange, act, assert. Related checks may share one figure: create it once, then add more act-assert blocks. Creating a figure costs more than 100 ms, so do not make extras.

Create figures with `plt.figure()` or `plt.subplots()`. Do not call `plt.close()`. The `mpl_test_settings` fixture already cleans figures and `rcParams`.

Assert the value when the behavior is a value. Compare images only when the picture is the behavior.

```python
def test_savefig_preserve_layout_engine():
    fig = plt.figure(layout="compressed")
    fig.savefig(io.BytesIO(), bbox_inches="tight")
    assert fig.get_layout_engine()._compress
```

Cover the edge that would hide a regression: empty input, a sequence where a scalar used to be assumed, and the failure path. `pytest.raises` and `pytest.warns` must include a `match`. A deprecated call is allowed only inside `pytest.warns(mpl.MatplotlibDeprecationWarning, ...)`.

## Images

Prefer `@check_figures_equal` when two drawing methods should match. The test takes `fig_test` and `fig_ref`. That avoids a new baseline file.

Use `@image_comparison` only for a new picture. New tests pass `style="mpl20"`. Pass `remove_text=True`, or use the `text_placeholders` fixture, when text is not the subject.

```python
@image_comparison(baseline_images=["line_dashes.png"], remove_text=True, style="mpl20")
def test_line_dashes():
    fig, ax = plt.subplots()
    ax.plot(range(10), linestyle=(0, (3, 3)), lw=5)
```

The first run fails because the baseline is missing. Copy `result_images/<test module>/<name>.png` to `lib/matplotlib/tests/baseline_images/<test module>/` and `git add` it. For more than one format, omit the extension and pass `extensions`.

`tol` is the mean per-pixel color difference. 255 is the maximum difference. The default is 0. A non-default `tol` is a named decision: set the name next to the decorator and say why in a comment.

## Run the test you added

From the repository root:

```bash
pytest lib/matplotlib/tests/test_simplification.py::test_clipping
```

`python -m pytest` needs `-P` so the current directory is not on the import path. Do not add `--import-mode prepend` unless `-P` is unavailable. It turns off assertion rewriting.

## Before finishing

- [ ] File, function, and class names follow the prefixes above, and the function name states the behavior.
- [ ] Sample data is short and explicit. Tolerances and other unexplained numbers have names.
- [ ] The test asserts an outcome, including the failure or warning path when that is the change.
- [ ] A value is asserted directly. An image comparison is used only for a picture, with `style="mpl20"` and a committed baseline, or `@check_figures_equal` compares two methods.
- [ ] Random data uses `np.random.default_rng(19680801)`.
- [ ] The new test was run and passed.
