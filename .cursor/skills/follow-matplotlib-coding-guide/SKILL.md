---
name: follow-matplotlib-coding-guide
description: Apply Matplotlib's coding guidelines from doc/devel/coding_guide.rst when editing library code. Covers ruff and the 88-character line length, import names, fig and ax variable names, type stubs, keyword-only arguments, logging, and C or C++ extensions. Use when writing or reviewing Python or extension code in lib/ or src/.
---

# Follow the coding guide

The source is `doc/devel/coding_guide.rst`. If this skill and that file disagree, follow the file.

## Style

PEP 8, enforced by ruff, with a line length of 88. Do not run black. Check with:

```bash
ruff check path/to/module.py
```

## Imports and names

```python
import numpy as np
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.patches as mpatches
```

Read rcParams as `mpl.rcParams`. Do not `from matplotlib import rcParams`.

Name a `FigureBase` `fig` and an `Axes` `ax`. Name a `Transform` `trans`, or `trans_<source>_<target>`. Add a suffix when there is more than one of the same class.

## Public API shape

New or changed public functions get type hints. Store them in the matching `*.pyi` stub. `pyplot.py` is hinted inline. `tox -e stubtest` checks the stubs.

Reserve `**kwargs` for arguments that pass through to another function. Name arguments the function itself uses. Consume a few keys locally by declaring them keyword-only, and pass the rest on:

```python
def plot(self, *args, scalex=True, scaley=True, **kwargs):
    ...
```

Mark helpers private with a leading underscore. A new module must be listed in the `meson.build` of its directory.

## Logging

Use a module logger, not `print`. Do not pre-format the message.

```python
_log = logging.getLogger(__name__)
_log.debug("layout skipped for %s", name)
```

Use `_api.warn_external` when the caller must change their code. Use `logging.warning` for a condition that can persist. `logging.info` explains odd behavior. `logging.debug` is for expected steps.

## C and C++

`src/` follows PEP 7 as far as it applies to C++. Keep the Python/C boundary in `FOO_wrap.cpp` or `FOO_wrapper.cpp`. Header docs use numpydoc. Do not restyle `extern/`. Run `python tools/run_clang_tidy.py` when you change `src/`. A suppression is a narrow `NOLINT` comment that says why.
