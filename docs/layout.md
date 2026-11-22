# Layout in inches

GraphPad Prism sets the length of each axis directly, instead of deriving it from the figure size
and margins. `add_axes_inches` does the same: it places axes at a position and size given in
inches from the figure's lower-left corner, so the x- and y-axes are exactly as long as you ask.
`legend_inches` and `suptitle_inches` place a legend and a figure title in inches too. All three
keep their place when the figure is resized and at any dpi, and because the styles do not crop
saved figures, the saved file has exactly the figure's size.

## Axes, legends, and titles

```python
import matplotlib.pyplot as plt
import numpy as np

import mplplots as mpp
from mplplots.palettes import BLUES, REDS

mpp.use()

x = np.linspace(0, 10, 50)
fig = plt.figure(figsize=(3, 2.25))  # the saved file is 3 by 2.25 in
ax = mpp.add_axes_inches(fig, left=0.5, bottom=0.4, width=2.25, height=1.5)  # 2.25 by 1.5 in axes
ax.plot(x, np.sin(x), color=BLUES[4], linewidth=1.2, label=r"$\sin(x)$")
ax.plot(x, np.cos(x), color=REDS[4], linewidth=1.2, label=r"$\cos(x)$")
mpp.auto_ticks(ax, left=0, right=10)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
mpp.legend_inches(ax, 2.75, 1.9, loc="upper right", ncols=2)  # upper-right corner at (2.75, 1.9) in
fig.savefig("figure.pdf")
```

- `add_axes_inches(fig, left, bottom, width, height, **kwargs)` adds axes whose x-axis is
  `width` and y-axis `height` inches long, meeting at (`left`, `bottom`). Other keyword arguments
  go to `fig.add_axes`.
- `legend_inches(ax, x, y, loc="upper left", **kwargs)` places the point of the legend box that
  `loc` names at (`x`, `y`): a corner (`"upper left"`), the middle of an edge (`"center left"`),
  or `"center"`. Other keyword arguments, such as `ncols` or `title`, go to `ax.legend`.
- `suptitle_inches(fig, t, top=0.1, **kwargs)` adds a centered figure title whose top edge is
  `top` inches below the figure's top edge.

The Personal image of the [style comparison](gallery.md#style-comparison) uses this layout, plus a
title.

## Grids of panels

`mplplots.layout` builds whole figures this way. `grid_inches` makes a figure and a grid of axes
from axis lengths, margins, and gaps, all in inches, and derives the figure size from them:

```python
import numpy as np

import mplplots as mpp

mpp.use()

# Three stacked panels with 2.5 by 0.8 in axes, 0.2 in apart and sharing both axes:
# a 3.3 by 3.3 in figure.
fig, axes = mpp.grid_inches(3, 1, width=2.5, height=0.8, hspace=0.2, sharex=True, sharey=True)
t = np.linspace(0, 10, 201)
series = [("Slow", 1, "#7a7a7a"), ("Intermediate", 2, "#4f9d58"), ("Fast", 4, "#3182bd")]
for ax, (label, k, color) in zip(axes, series):
    ax.plot(t, np.sin(k * t), color=color, linewidth=1.2, label=label)
    ax.legend()
axes[0].set(xlim=(0, 10), ylim=(-1, 2))  # shared: headroom for the legends above the curves
axes[-1].set_xlabel("Time (s)")
mpp.add_shared_ylabel(fig, axes, "Signal (a.u.)")
mpp.align_legends_left(axes)  # the three legends start at the same x
```

- `grid_inches(nrows=1, ncols=1, *, width, height, left=0.6, right=0.2, top=0.1, bottom=0.4,
  wspace=0.6, hspace=0.5, sharex=False, sharey=False, **figure_kwargs)` returns the figure and its
  axes as a flat list, top row first. `width` is the x-axis length of each column and `height` the
  y-axis length of each row; a number applies to all, a sequence gives one per column or row, and
  so do `wspace` and `hspace` for the gaps. The figure is `left + sum(width) + sum(wspace) + right`
  wide and `top + sum(height) + sum(hspace) + bottom` tall. `sharex` and `sharey` keep tick labels
  on the bottom row and the left column only, as `plt.subplots` does.
- `figure_size(width="single", *, height=None, aspect=None)` returns a figure size for a journal
  column preset (`COLUMN_WIDTHS`: `"single"` 3.5 in, `"onehalf"` 5 in, `"double"` 7 in) or a
  width in inches. `height` wins over `aspect`, which defaults to 0.7: `figure_size()` is
  `(3.5, 2.45)` and `figure_size("double", aspect=0.5)` is `(7.0, 3.5)`.
- `add_shared_ylabel(fig, axes, text)` adds one y label for a stack or grid of panels, at the gap
  an ordinary `ax.set_ylabel` would leave from the leftmost tick labels. For a shared x label, use
  the bottom panel's `set_xlabel`.
- `align_legends_left(axes, *, right=0.985, y=0.97)` gives the legends of several panels a common
  left edge, so legends of different widths line up. Call it after the legends are drawn.

## Margins

With 8 pt text, 0.5 to 0.6 in to the left of the axes fits the tick labels and a y-axis label,
0.4 in below fits the tick labels and an x-axis label, 0.2 in to the right holds the label of a
tick at the end of the x-axis, and 0.35 in above fits an axes title. These are the defaults of
`grid_inches`, apart from the title space (`top=0.35`). The GraphPadPrism style's 11 to 14 pt
text needs 0.8 in on the left, 0.6 in below, and 0.4 in above for a title.

## Fixed positions and colorbars

The axes keep their position through an axes locator, so `tight_layout`, constrained layout,
`ax.set_position`, and the space `fig.colorbar(..., ax=ax)` takes do not move them. For a
colorbar, add its axes with `add_axes_inches` and pass them as `cax`, and give its outline the
minor tick width (`colorbar.outline.set_linewidth(0.6)` in the Personal style).
