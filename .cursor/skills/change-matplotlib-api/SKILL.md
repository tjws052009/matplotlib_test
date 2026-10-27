---
name: change-matplotlib-api
description: Change Matplotlib's public API using doc/devel/api_changes.rst. Covers private helpers, keyword-only parameters, rcParams, pyplot wrappers, colormaps, deprecation and expiry, and the release-note files. Use when adding, renaming, or removing a public function, parameter, attribute, rcParam, colormap, or when a figure would look different.
---

# Change the Matplotlib API

The source is `doc/devel/api_changes.rst`. If this skill and that file disagree, follow the file.

A change to what the figure looks like is an API change, whether the cause is semantic or aesthetic. Change the API only when the benefit is worth the migration.

## Add API

Prefix helpers and internal attributes with `_`. Match names already used nearby. Make new parameters keyword-only when that stays compatible.

A new rcParam needs all three of these:

- a validator in `_validators` and a `_Param` in `lib/matplotlib/rcsetup.py`
- a commented default in `lib/matplotlib/mpl-data/matplotlibrc`
- the key on `RcKeyType` in `lib/matplotlib/typing.py`

After a pyplot-wrapped signature change, run `lib/matplotlib/tests/test_pyplot.py::test_pyplot_up_to_date`. If the change is intentional, run `tools/boilerplate.py` and commit the wrappers.

Do not edit an existing colormap, color sequence, or style. A new one needs a new use case, distinct colors with colorblindness considered, evidence it is already used, and a BSD-compatible license.

## Deprecate

Introduce the warning in one meso release. Remove the old behavior two meso releases later. The old API stays fully functional until removal, and the replacement exists during that time.

| Change | Helper |
|---|---|
| Function, class, method, or property | `@_api.deprecated` |
| Free-form warning | `_api.warn_deprecated` |
| Attribute becomes private | `@_api.deprecate_privatize_attribute` |
| Signature | `@_api.delete_parameter`, `@_api.rename_parameter`, or `@_api.make_keyword_only` |

`since` is the next point release, such as `"3.x"`. A pending deprecation sets `pending=True` and leaves `removal` blank. It warns only in dev mode.

On expiry, delete the warning and the old behavior, and update the `.pyi` to the final signature.

## Announce

Put the directive at the end of the description block it belongs to.

| Kind | Directive | Folder |
|---|---|---|
| New feature | `.. versionadded:: 3.N` | `doc/release/next_whats_new/` |
| Behavior change | `.. versionchanged:: 3.N` | `doc/api/next_api_changes/` |
| Introduce a deprecation | deprecation notice | `doc/api/next_api_changes/deprecations/` |
| Expire a deprecation | removal or behavior note | `doc/api/next_api_changes/` |

Name the note file `<pr-number>-<initials>.rst`.
