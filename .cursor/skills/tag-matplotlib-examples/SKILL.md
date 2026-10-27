---
name: tag-matplotlib-examples
description: Tag Matplotlib gallery examples using doc/devel/tag_guidelines.rst and doc/devel/tag_glossary.rst. Covers the tags directive, content tags, subcategory form, and when to propose a new tag. Use when adding or editing an example, a tutorial tag, or a gallery tag proposal.
---

# Tag gallery examples

The sources are `doc/devel/tag_guidelines.rst` and the list in `doc/devel/tag_glossary.rst`. If this skill and those files disagree, follow the files.

Every gallery example gets at least one content tag. Add a structural, domain, or internal tag when it helps someone find the page. Repeating the folder name is fine. Also tag a strong side topic, such as `legend` on a colormap example, instead of retitling the example.

Put the directive at the bottom of the page:

```rst
.. tags::
   topic: tagging, purpose: reference
```

Before adding a tag, search the glossary for a near duplicate (`axes` versus `axis`). A new tag is `subcategory: tag`, one or two words, and it must fit more than one existing example. A niche example does not get its own tag.

Propose a missing tag with the `tag` issue type from the `create-matplotlib-issue` skill. Do not invent the tag only in one file.
