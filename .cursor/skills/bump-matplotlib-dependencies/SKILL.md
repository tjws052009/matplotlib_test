---
name: bump-matplotlib-dependencies
description: Choose and record Matplotlib dependency versions using doc/devel/min_dep_policy.rst. Covers NEP 29 windows for Python, NumPy, and other libraries, and the files a version bump must touch. Use when adding a library, raising a minimum version, or editing pyproject.toml dependencies.
---

# Bump Matplotlib dependencies

The source is `doc/devel/min_dep_policy.rst`. If this skill and that file disagree, follow the file. Also follow `new-dependencies` when that rule is present: the PR summary names the library, the minimum version, and why.

Matplotlib follows NEP 29. "Minor version" here includes major releases. A date-based version counts every release as a minor version.

## How old a dependency may be

| Dependency | Support |
|---|---|
| Python | 42 months of minor releases, and at least the two newest |
| NumPy | 24 months of minor releases, and at least the three newest |
| Other library with compiled extensions | 24 months, or the oldest that supports the minimum Python and NumPy |
| Pure-Python library | 12 months, or the oldest that supports the minimum Python |
| Test and doc dependencies | 12 months, without dropping what downstream packagers still run |
| FreeType, GUI, LaTeX, Ghostscript, FFmpeg | as old as is still practical |

Raise Python and NumPy on a meso release, never on a patch release. Bump anything else only when the new feature is needed or the old release cannot run on the minimum Python or NumPy. Work around a dependency bug when that is practical. Do not raise a minimum because of a security advisory. A vulnerability Matplotlib itself makes exploitable is a Matplotlib bug.

Using a new feature, or deleting a workaround for a dropped version, is a follow-up PR. The bump PR only changes the pins.

## Files

Python minimum:

- `pyproject.toml` classifiers, `requires-python`, and the ruff `target-version`
- `environment.yml`
- `doc/install/dependencies.rst`
- `doc/devel/min_dep_policy.rst`
- CI workflow files
- `tox.ini`

NumPy minimum, in addition to the shared docs and environment files:

- `pyproject.toml`
- `lib/matplotlib/__init__.py` `_check_versions()`
- `ci/minver-requirements.txt`

The policy text also names `requirements/testing/minver.txt`. This checkout keeps that list in `ci/minver-requirements.txt`. Update the file that exists.

Add a development API note with the old and new minimums for Python and NumPy, and say the bump matches this policy.
