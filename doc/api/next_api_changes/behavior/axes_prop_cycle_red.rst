Default x-y color cycle is red-based
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default :rc:`axes.prop_cycle` is no longer the tab10 palette. An x-y
artist that does not set a color, including `~.Axes.plot`, takes its color
from this cycle. The first series is ``#a50f15``, then ``#e31a1c``,
``#fb6a4a``, ``#7f0000``, ``#fc9272``, ``#cb181d``, ``#fd8d3c``, ``#99000d``,
``#fdbb84``, and ``#67000d``.

``image.cmap`` is still ``viridis``. Spine, tick, and label colors are
unchanged. The previous cycle is still available as ``cycler(color='tab10')``.

.. versionchanged:: 3.12
   The default ``axes.prop_cycle`` is a red-based sequence instead of tab10.
