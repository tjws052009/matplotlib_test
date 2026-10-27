---
name: write-matplotlib-docs
description: Write Matplotlib documentation using doc/devel/document.rst and doc/devel/style_guide.rst. Covers numpydoc, parameter types, gallery examples, Figure versus figure, Axes versus Axis, and reStructuredText formatting. Use when editing docstrings, galleries, tutorials, or prose docs.
---

# Write Matplotlib documentation

Follow `doc/devel/document.rst` and `doc/devel/style_guide.rst`. If this skill and those files disagree, follow the files. Where existing docstrings are older than the guide, follow the guide.

Do not edit generated pages. Sphinx rebuilds `doc/plot_types`, `doc/gallery`, `doc/tutorials`, `doc/users/explain`, and `doc/api` except `doc/api/next_api_changes/`.

## Docstrings

Use numpydoc. One-line docstrings keep the quotes on the same line. Multi-line docstrings put the quotes on their own lines.

Refer to a parameter as `*linestyles*`. Do not use `` `linestyles` `` or ``` ``linestyles`` ```. Quote a string value with plain quotes: `'tight'`.

Types are prose, not annotations: `list of str`, `int or str`, `float`, `(float, float)`, `(M, N) array-like`. Use `array-like` for input sequences and `array` when the return value is a NumPy array.

```rst
colors : list of colors, default: :rc:`lines.color`
interval : int, default: 1000ms
norm : `~matplotlib.colors.Normalize`, optional
    A `.Normalize` instance scales data to 0, 1.
```

If `None` only means "not passed", document the real default or mark the parameter optional. Do not write `default: None` for that case.

`See Also` entries are plain names. Sphinx links them. A setter's `Parameters` block is what `plt.setp` prints. Use `.. ACCEPTS:` only when that block cannot say the values.

## Terms

Use the class name for the object, and the lowercase word for ordinary English.

| Write | Do not write for the Matplotlib object |
|---|---|
| Figure, Axes, Artist, Axis | figure, axes, artist, axis |
| Axes interface | explicit interface, OO-style, OOP |
| pyplot interface | implicit interface, MATLAB-like |

Headings are sentence case. Prefer a noun phrase for a section title. Comments sit above the line or at its end, never on the following line. Gallery scripts call `plt.show()` or `fig.show()` and do not print Python reprs.

Bullets are unordered items. Numbers are steps. Tables are reStructuredText grid or simple tables, not Markdown or `csv-table`.

## Examples

Gallery sources live in `galleries/`, not in `doc/gallery`. The module docstring is the title and the first paragraph. Later prose sections start with `# %%`. Put `sgskip` in the filename to skip a plot.

Cite public sample data. Inline small data. Larger files go through `cbook.get_sample_data` and live in `lib/matplotlib/mpl-data/sample_data/`.

End an example with a References admonition only for functions the example is about. Name both the Axes method and the pyplot function, pyplot second. Do not list `pyplot.subplots` unless the example is about subplot layout.

```python
# %%
#
# .. admonition:: References
#
#    The use of the following functions, methods, classes and modules is shown
#    in this example:
#
#    - `matplotlib.axes.Axes.fill` / `matplotlib.pyplot.fill`
```

Order inside a section is `gallery_order.txt`. A `*` marks where unlisted names sort. Without `*`, every example must be listed.
