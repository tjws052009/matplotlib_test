# Issue body skeletons

Copy one skeleton. Keep the headings. Delete the HTML comments before `gh issue create`.

`Issue name` is one line and does not include the title prefix. `Issue type` is exactly one of `bug`, `regression`, `feature`, `documentation`, `maintenance`, `tag`, or a single more specific word.

## bug

GitHub title: `[Bug]: ` plus the issue name. Label: `bug`.

~~~~markdown
### Issue name

<!-- one line, no [Bug]: prefix -->

### Issue type

bug

### Impact

<!-- who hits this, and whether a workaround exists -->

### Description

<!-- what goes wrong, in plain language -->

### Code for reproduction

```python
# minimum script that shows the bug
```

### Actual outcome

<!-- console text, or a description of the figure -->

### Expected outcome

<!-- what the script should do instead -->

### Environment

**Operating system**:
**Matplotlib version**:
**Matplotlib backend**:
**Python version**:
**Jupyter version**:
**Installation**:

### Affected component

<!-- one value from the skill's component list -->

### Additional information

<!-- None. when there is nothing else. Mention generative AI here when it was used. -->
~~~~

## regression

Same title prefix and label as `bug`.

~~~~markdown
### Issue name

### Issue type

regression

### Impact

### Description

### Code for reproduction

```python
# minimum script that shows the regression
```

### Actual outcome

### Expected outcome

### Last known good version

<!-- Matplotlib version that still behaved correctly -->

### Environment

**Operating system**:
**Matplotlib version**:
**Matplotlib backend**:
**Python version**:
**Jupyter version**:
**Installation**:

### Affected component

### Additional information

None.
~~~~

## feature

GitHub title: `[ENH]: ` plus the issue name. Label: `enhancement` when that label exists, otherwise `New feature` when that label exists.

~~~~markdown
### Issue name

### Issue type

feature

### Impact

### Description

### Problem

<!-- the concrete gap, in 2-4 sentences -->

### Proposed solution

<!-- API or behavior that would close the gap -->

### Alternatives considered

None.

### Affected component
~~~~

## documentation

GitHub title: `[Doc]: ` plus the issue name. Label: `documentation` when that label exists, otherwise `Documentation`.

~~~~markdown
### Issue name

### Issue type

documentation

### Impact

### Description

### Documentation link

<!-- https://matplotlib.org/devdocs/... or a repo path. None. if there is no page yet. -->

### Problem

<!-- what is missing, unclear, or wrong -->

### Suggested improvement

<!-- the replacement wording, example, or figure -->
~~~~

## maintenance

GitHub title: `[MNT]: ` plus the issue name. Label: `Maintenance` only when `gh label list` shows it.

~~~~markdown
### Issue name

### Issue type

maintenance

### Impact

### Description

### Summary

<!-- 1-2 sentences -->

### Proposed fix

<!-- what should change in the library -->

### Affected component
~~~~

## tag

GitHub title: `[Tag]: ` plus the issue name. Label: `Documentation: tags` when that label exists, otherwise `documentation`.

~~~~markdown
### Issue name

### Issue type

tag

### Impact

### Description

### Need

<!-- which examples are hard to find, and which existing tags fail them -->

### Proposed tag

<!-- subcategory: tag -->
~~~~

## other

Use this when the issue type is a single word that is not listed above. Put that word under Issue type. Do not add a title prefix.

~~~~markdown
### Issue name

### Issue type

### Impact

### Description

### Affected component
~~~~
