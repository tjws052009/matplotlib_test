---
name: create-matplotlib-issue
description: Draft and open GitHub issues for this Matplotlib repository with a body that always includes Issue name, Issue type, Impact, and Description, then adds headings that change by issue type (bug, regression, feature, documentation, maintenance, tag). Use when the user asks to create, file, open, or draft a GitHub issue, bug report, regression, feature request, enhancement, documentation issue, maintenance task, or gallery tag proposal.
---

# Create a Matplotlib issue

File issues on the repository of the current checkout (`gh` default repo). Read [templates.md](templates.md) for the body to fill. Read [examples.md](examples.md) when the wording of a section is unclear.

This checkout's issue forms live in `.github/ISSUE_TEMPLATE/`. The body below is the markdown those forms ask for. `gh issue create` submits that markdown; it does not fill the YAML form widgets.

## Required headings

Every issue body starts with these headings, in this order, spelled exactly this way. Add the type-specific headings after them. Do not rename, drop, or reorder the four.

1. Issue name
2. Issue type
3. Impact
4. Description

`Issue name` is one line. It is the GitHub title after the prefix in the table below. Do not put the prefix inside `Issue name`.

## Issue types

| Issue type | Use when | Title prefix | Label to prefer | Extra headings |
|---|---|---|---|---|
| `bug` | Existing behavior is incorrect | `[Bug]: ` | `bug` | Code for reproduction, Actual outcome, Expected outcome, Environment, Affected component |
| `regression` | Behavior used to be correct and broke in a later version | `[Bug]: ` | `bug` | Same as `bug`, plus Last known good version |
| `feature` | The change adds behavior the library does not have | `[ENH]: ` | `enhancement`, else `New feature` | Problem, Proposed solution, Affected component |
| `documentation` | Docs, docstrings, or examples are wrong or missing | `[Doc]: ` | `documentation`, else `Documentation` | Documentation link, Problem, Suggested improvement |
| `maintenance` | Performance, naming, or internal structure should improve, and behavior is not wrong | `[MNT]: ` | `Maintenance` | Summary, Proposed fix, Affected component |
| `tag` | The example gallery needs a tag or subcategory | `[Tag]: ` | `Documentation: tags`, else `documentation` | Need, Proposed tag |

If the request fits none of these, set `Issue type` to a single specific word (for example `performance`) and use only the four required headings plus `Affected component`. Do not add a title prefix.

Run `gh label list --limit 100` and pass a label only when that exact name is listed. This fork often has the default set (`bug`, `enhancement`, `documentation`, `accessibility`) and not the upstream names (`New feature`, `Documentation`, `Maintenance`, `Documentation: tags`). Skip a missing label. Add `accessibility` as well when the issue is a barrier for people with disabilities.

`Affected component` is one of: `pyplot`, `axes`, `figure`, `artist`, `image`, `colors`, `colorbar`, `cm`, `animation`, `widgets`, `axis`, `ticker`, `dates`, `units`, `text`, `legend`, `contour`, `collections`, `patches`, `transforms`, `lines`, `markers`, `spines`, `scale`, `style`, `font_manager`, `mathtext`, `texmanager`, `path`, `quiver`, `streamplot`, `tri`, `table`, `inset`, `offsetbox`, `projections`, `rcsetup`, `backend`, `cbook`, `category`, `patheffects`, `hatch`, `testing`, `documentation`, `gallery`, `general`, `mpl_toolkits.mplot3d`, `mpl_toolkits.axes_grid1`, `mpl_toolkits.axisartist`.

`Proposed tag` contains a line `subcategory: tag`, for example `plot types: violin`.

`Installation` is one of: `pip`, `conda`, `pixi`, `uv`, `Linux package manager`, `from source (.tar.gz)`, `git checkout`, or `unknown`.

## Do not open an issue

- **Security.** Do not create a public GitHub issue. Direct the report to [Tidelift](https://tidelift.com/security), as `SECURITY.md` at the repository root describes.
- **Usage question.** Send it to [Discourse](https://discourse.matplotlib.org). A short question about contributing goes to the [dev chat](https://discourse.matplotlib.org/chat/c/matplotlib/2). Do not open an issue.
- **Feature with no concrete proposal.** A wishlist with no behavior or API shape does not get `gh issue create`. Return the filled template and tell the user to post it on Discourse.
- **Duplicate.** If an open issue already covers it, return that URL and stop.

## Workflow

1. Classify the issue type. Ask for a missing required fact (what breaks, who is affected, the reproduction, the Matplotlib version). Do not invent versions, tracebacks, figures, or reproduction code.
2. Search duplicates in this repo, then upstream:

```bash
gh issue list --state open --limit 20 --search "keywords from the issue name"
gh issue list --state closed --limit 10 --search "keywords from the issue name"
gh issue list --repo matplotlib/matplotlib --state open --limit 10 --search "keywords from the issue name"
```

If matplotlib/matplotlib already has the same report, link it and stop. File a local tracking issue only when the user explicitly asks for one on this fork.

3. Copy the matching skeleton from [templates.md](templates.md). Fill every heading. Strip the HTML guidance comments before filing.
4. For `bug` and `regression`, put a minimum self-contained Python script under Code for reproduction. The script must come from the user, or from a failure you actually ran in this checkout. A visual bug still includes the code, and Actual outcome describes the figure. Do not fabricate a screenshot.
5. If a model drafted the reproduction or the wording, say so under Additional information and follow the [generative AI restrictions](https://matplotlib.org/devdocs/devel/contribute.html#restrictions-on-generative-ai-usage). Do not file a report the user cannot explain.
6. Write Matplotlib version as `unknown` only after the user says they do not know it. Never invent a version number.
7. Write the body to a temp file and validate it. Fix every reported line and run it again. File only after it prints `OK`.

```bash
python3 .cursor/skills/create-matplotlib-issue/scripts/validate_issue.py /tmp/mpl-issue.md
```

8. Create the issue only when the user asked to file or open it. A draft request stops after the validated body.

```bash
gh issue create --title "[Bug]: <Issue name line>" --body-file /tmp/mpl-issue.md --label "<label>"
```

Use the prefix and label from the table. Omit `--label` when no listed label exists.

9. Reply with the issue URL, the issue type, and any duplicate you considered.

## Section rules

- **Issue name.** Specific symptom or change. Lead with the API when it is known: `Axes.bar drops a width sequence when align is edge`.
- **Impact.** Who is affected, what breaks or improves, whether a workaround exists.
- **Description.** What happens or what should change, in plain language. Name the module. Do not repeat Impact verbatim.
- **Alternatives considered.** Write `None.` when there are none. Do not leave that heading empty when you include it.
- **Additional information.** Write `None.` when there is nothing else. This heading is optional.
