# Examples

Sample wording for the validator. These are not reports to file as-is.

## bug

Title: `[Bug]: Axes.bar drops a width sequence when align is edge`

~~~~markdown
### Issue name

Axes.bar drops a width sequence when align is edge

### Issue type

bug

### Impact

Callers who pass one width per bar with `align="edge"` get a single shared width. Passing `align="center"` keeps the sequence, so center alignment is a workaround when edge alignment is not required.

### Description

`Axes.bar` documents that `width` may be a scalar or a sequence. With `align="edge"` and a sequence of widths, every bar is drawn with the first width.

### Code for reproduction

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
bars = ax.bar([0, 1, 2], [1, 2, 3], width=[0.2, 0.4, 0.8], align="edge")
print([bar.get_width() for bar in bars])
```

### Actual outcome

`[0.2, 0.2, 0.2]`

### Expected outcome

`[0.2, 0.4, 0.8]`

### Environment

**Operating system**: Ubuntu 24.04
**Matplotlib version**: 3.10.1
**Matplotlib backend**: Agg
**Python version**: 3.12.3
**Jupyter version**: n/a
**Installation**: pip

### Affected component

axes

### Additional information

None.
~~~~

## regression

Title: `[Bug]: colorbar steals space from a constrained layout that used to fit`

~~~~markdown
### Issue name

colorbar steals space from a constrained layout that used to fit

### Issue type

regression

### Impact

Figures that place a vertical colorbar beside a constrained-layout axes now clip the colorbar label. The same script on the last good release leaves a gap for the label.

### Description

Adding a colorbar to a constrained-layout figure no longer reserves room for the colorbar's y label.

### Code for reproduction

```python
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(layout="constrained")
mesh = ax.pcolormesh(np.arange(12).reshape(3, 4))
cbar = fig.colorbar(mesh, ax=ax)
cbar.set_label("counts")
print(fig.get_constrained_layout())
```

### Actual outcome

The colorbar label is clipped by the figure edge.

### Expected outcome

The label sits fully inside the figure, with a gap between the colorbar and the edge.

### Last known good version

3.9.2

### Environment

**Operating system**: macOS 15
**Matplotlib version**: 3.10.1
**Matplotlib backend**: Agg
**Python version**: 3.12.7
**Jupyter version**: n/a
**Installation**: conda

### Affected component

colorbar

### Additional information

None.
~~~~

## feature

Title: `[ENH]: Axes.bar accepts a hatch sequence`

A request with no proposed behavior does not become an issue. This one names the API, so it can be filed when the user asked for a GitHub issue. Otherwise post the same body on [Discourse](https://discourse.matplotlib.org).

~~~~markdown
### Issue name

Axes.bar accepts a hatch sequence

### Issue type

feature

### Impact

Grouped bar charts that need a different hatch per bar set the hatch in a loop after `bar` returns. There is no way to pass that sequence into `bar` itself.

### Description

Accept a sequence of hatch patterns in `Axes.bar`, one entry per bar, in addition to the existing scalar hatch.

### Problem

`bar` already broadcasts a width sequence and a color sequence. Hatch is scalar only, so a chart with one hatch per category needs a follow-up loop that is easy to get out of sync with the data.

### Proposed solution

When `hatch` is a sequence the same length as `x`, assign `patches[i].set_hatch(hatch[i])` inside `bar`. A scalar hatch keeps today's behavior. A length mismatch raises `ValueError` with the two lengths.

### Alternatives considered

Keep the loop in user code. Rejected because width and color already broadcast and hatch is the odd one out.

### Affected component

axes
~~~~

## documentation

Title: `[Doc]: bar_label example never shows the padding argument`

~~~~markdown
### Issue name

bar_label example never shows the padding argument

### Issue type

documentation

### Impact

Readers of the bar label example can see labels drawn on the bars, but they cannot tell that `padding` moves the text off the bar end. They find the argument only in the docstring.

### Description

The `bar_label` gallery example should pass `padding` once and say what it changes.

### Documentation link

https://matplotlib.org/devdocs/gallery/lines_bars_and_markers/bar_label_demo.html

### Problem

Every call in the example uses the default padding. The parameter list in `Axes.bar_label` documents `padding`, and the example never sets it.

### Suggested improvement

Add one call, `ax.bar_label(bars, padding=6)`, and one sentence: padding is the distance in points from the bar end to the text.
~~~~

## maintenance

Title: `[MNT]: pyplot.install_repl_displayhook repeats its pyplot import`

~~~~markdown
### Issue name

pyplot.install_repl_displayhook repeats its pyplot import

### Issue type

maintenance

### Impact

The displayhook setup imports `matplotlib.pyplot` a second time on every IPython start. Behavior stays the same. The extra import shows up in startup profiles of short scripts that only wanted the hook.

### Description

`install_repl_displayhook` imports pyplot at function scope even though the caller already imported it to reach this function.

### Summary

Use the package already being initialized instead of importing pyplot again inside the displayhook installer.

### Proposed fix

Drop the inner `import matplotlib.pyplot as plt` and call the displayhook helpers on the current module.

### Affected component

pyplot
~~~~

## tag

Title: `[Tag]: add a plot-types tag for violin plots`

~~~~markdown
### Issue name

add a plot-types tag for violin plots

### Issue type

tag

### Impact

Violin examples are filed under statistics and under box plots. Someone looking for violins has to open both tags.

### Description

Give violin plots their own gallery tag under the existing plot-types subcategory.

### Need

`plot types: box plot` is the closest tag, and it does not match a search for violin. Current pages that would carry the new tag include the violin plot demo and the violin plot customization example. The subcategory already exists.

### Proposed tag

plot types: violin
~~~~
