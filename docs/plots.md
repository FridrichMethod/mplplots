# Plot helpers

`mplplots.plots` draws the elements that the Personal
[style guide](../src/mplplots/data/skills/mplplots/references/style-guide.md) asks for in a fixed
form. `plot_mean_sem` and `plot_distribution` take the fill and edge of a
[color pair](colors.md#color-pairs).

## Functions

- `plot_mean_sem(ax, x, mean, sem, *, fill, edge, label=None, linewidth=1.2, linestyle="-", ...)`
  draws a borderless `mean +/- sem` band in `fill` under the mean curve in `edge`, and returns the
  curve. A second state of the same role takes `linestyle=mpp.SECONDARY_LINESTYLE`.
- `plot_distribution(ax, edges, counts, n_total, *, fill, edge, ...)` draws pre-binned counts as a
  curve through the bin centers, filled to zero, in percent of all `n_total` samples per bin. It
  returns a legend proxy with the same face, edge, and line width.
- `significance_stars(p)` returns `"***"` below 0.001, `"**"` below 0.01, `"*"` below 0.05, and
  `"n.s."` otherwise, also for NaN. Pass the multiplicity-corrected value.
- `box_axes(ax)` shows all four spines with ticks on the left and bottom only, for a panel that is
  meant to be boxed.

## Example

```python
import numpy as np

import mplplots as mpp

mpp.use()
REFERENCE = mpp.ColorPair(fill="#cccccc", edge="#7a7a7a")
TREATED = mpp.ColorPair(fill="#c7e9c0", edge="#4f9d58")

rng = np.random.default_rng(0)
edges = np.linspace(0, 6, 31)  # one bin grid for both series
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)
proxies = []
# The reference is drawn on top of the series it overlaps (zorder 4 over 2).
for loc, n, pair, zorder in [(2.2, 5000, REFERENCE, 4), (3.6, 4000, TREATED, 2)]:
    counts, _ = np.histogram(rng.normal(loc, 0.6, n), edges)
    proxies.append(
        mpp.plot_distribution(ax, edges, counts, n, fill=pair.fill, edge=pair.edge, zorder=zorder)
    )
ax.legend(proxies, ["Reference", "Treated"])
ax.set(xlim=(0, 6), ylim=(0, 20), xlabel="Distance (\u00c5)", ylabel="Percent of samples")
```
