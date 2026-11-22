# Ticks

The styles set how ticks look, and Matplotlib's locators choose where they go; the Personal style
also sets how many minor ticks the default minor locator places. This page covers the minor ticks
that each style draws by default, and `auto_ticks`, which gives both axes of a plot Prism-like
ticks and ends each axis on a major tick. The widths and lengths of the ticks of each style are
listed in [What the Personal style changes](styles.md#what-the-personal-style-changes) and
[What the GraphPadPrism style changes](styles.md#what-the-graphpadprism-style-changes).

## Minor ticks of the styles

The Personal style shows minor ticks on both axes and sets `xtick.minor.ndivs` and
`ytick.minor.ndivs` to 2. Wherever Matplotlib's default minor locator (`AutoMinorLocator`) places
minor ticks, as on a linear axis of numbers, there is one minor tick halfway between each pair of
major ticks, instead of Matplotlib's 3 or 4. Log axes keep their own minor ticks. On linear
numeric axes `auto_ticks` sets its own minor ticks, and on categorical axes it removes them, so the
setting does not change them there (see [`auto_ticks`](#auto_ticks)).

The GraphPadPrism style keeps minor ticks off, as Prism draws none, and does not set
`xtick.minor.ndivs` or `ytick.minor.ndivs`. Applied with `mpp.use` or `mpp.context`, which first
return them to Matplotlib's default, a figure that turns minor ticks on, for example with
`ax.minorticks_on()`, gets Matplotlib's 3 or 4. `plt.style.use` keeps a value an earlier style set
(see [Loading a style by its dotted name](styles.md#loading-a-style-by-its-dotted-name)).

To give one axis another number of minor ticks, set its minor locator:

```python
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

import mplplots as mpp

mpp.use()

fig, ax = plt.subplots()
ax.plot([0, 10], [0, 1])
ax.xaxis.set_minor_locator(AutoMinorLocator(5))  # 4 minor ticks per major interval on x
```

## `auto_ticks`

```python
import matplotlib.pyplot as plt

import mplplots as mpp

mpp.use()

fig, ax = plt.subplots()
ax.bar(["A", "B", "C"], [23, 45, 12])
mpp.auto_ticks(ax, bottom=0)  # call after plotting; keep the y-axis starting at 0
```

`auto_ticks(ax, left=..., right=..., bottom=..., top=...)` gives both axes Prism-like ticks. On a
linear axis of numbers:

- **Major ticks:** about six, spaced 1, 2, 2.5, or 5 times a power of 10 (the same spacings as
  Matplotlib's default ticks).
- **Minor ticks:** fewer major ticks get more minor ticks. Six or more visible major ticks get 1
  minor tick halfway between. Five visible major ticks get 3 minor ticks per interval and four or
  fewer get 4, but a spacing of 2.5 or 5 always gets 4 (every 1 between 0 and 5) and a spacing of
  2 always gets 3 (every 0.5 between 0 and 2), so minor ticks stay on round values. A spacing of 1
  gets every 0.25 with five visible major ticks and every 0.2 with four or fewer.
- **Limits:** each axis starts and ends on a major tick, never on a bare stretch of axis line.
  - A limit you leave unset moves out to the nearest major tick.
  - A limit you pass (`left`, `right`, `bottom`, or `top`, for example `bottom=0` for bar charts)
    is kept exactly, and the tick spacing is chosen so that it is a major tick too: `right=7`
    gives a tick every 1. If no round spacing with at most 10 intervals fits (for example
    `bottom=-1.2`), that end stays between ticks.
  - Inverted axes stay inverted. The limits mean the same as in `ax.set_xlim(left, right)` and
    `ax.set_ylim(bottom, top)`, so on an inverted y-axis `bottom` is the larger value.

Other axes keep Matplotlib's own tick positions:

- **Log and other non-linear scales, dates, and other units:** unset limits also move out to the
  nearest major tick, so a log axis runs from one labeled decade to another.
- **Categorical axes** (string data, such as the `"A"`, `"B"`, `"C"` above) keep one tick per
  category and lose their minor ticks. Their limits are not changed, so the axis line extends
  half a category past the outer bars.

A limit you pass is applied to every kind of axis.

Call it **after** plotting your data, because it works from the limits the data produce. It
replaces the major tick locators of linear numeric axes. If you set custom tick positions or
labels on such an axis (for example, the group labels of a grouped bar chart with numeric bar
positions), set them after calling `auto_ticks`.

### Choosing limits

Six or more visible major ticks give the look of the Personal style, one minor tick between major
ticks. When an axis comes out with fewer, pass limits that leave five or more intervals: data
from 0 to 35 with `bottom=0` come out as 0 to 40 every 10, four intervals with three minor ticks
each; `top=35` gives seven intervals of 5 and `top=50` five of 10, each with one minor tick. Up to
about eight
intervals read well while the tick labels keep clear of each other. On an axis shorter than about
1 in, six intervals crowd the labels; Matplotlib's own ticks, which follow the length of the axis,
or a `MultipleLocator` spacing fit better there. The Personal gallery figures choose their limits
this way, and rule L2 of the
[style guide](../src/mplplots/data/skills/mplplots/references/style-guide.md) asks the same of
coding agents.
