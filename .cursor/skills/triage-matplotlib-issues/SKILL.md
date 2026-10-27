---
name: triage-matplotlib-issues
description: Triage Matplotlib issues using doc/devel/triage.rst. Covers thanks, usage questions, missing versions, minimal reproductions, regressions, and duplicates. Use when curating, labeling, or closing an issue, or when the user asks to triage.
---

# Triage Matplotlib issues

The source is `doc/devel/triage.rst`. If this skill and that file disagree, follow the file. Do not close or relabel an issue when `gh` cannot. Leave the recommendation as a comment.

Thank the reporter first. Stay with the assumption that they acted in good faith.

1. A usage question is not an issue. Point to https://discourse.matplotlib.org and, when the label exists, `Community support`. Close it.
2. The report needs Python version, Matplotlib version, operating system, and backend. Ask when one is missing. Label `status: needs clarification` when that label exists.
3. A bug needs a minimal reproduction. Ask for a shorter one when the sample is larger than the failure. If you cannot reproduce it, say so and include your own versions. Wait at least a week before closing a report that cannot be reproduced.
4. A regression is code that used to work. Find the last good version. It belongs on the next micro release.
5. A duplicate gets a link to the older issue, a thank-you, and `status: duplicate` when that label exists. Copy a better example onto the original issue.
6. Rewrite a vague title so it states the failure. Add topic labels that `gh label list` actually shows. This fork often has only the default GitHub labels, not the upstream `status:` and `topic:` names. Skip a missing label.

`Good first issue` requires a known fix and maintainer agreement on the approach. Do not use an AI tool to solve a good-first issue. The label exists to bring a new contributor into the project.

Do not apply a label this repository does not have.
