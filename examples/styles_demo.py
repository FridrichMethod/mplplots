"""Demonstrate mplplots styles with palettes and auto_ticks.

The GraphPadPrism figures use GraphPad Prism's default plot area, 3 by 2 in (2 by 2 in for the
five-bar chart), with 0.8 in for the y tick labels and label, 0.6 in for the x tick labels and
label, and 0.4 in for the title. A legend beside the plot starts 0.4 in to its right at its top,
within about 0.7 pt of where Prism puts it. Each figure passes ``assert_figure`` against the style
before it is saved.
"""

import matplotlib.pyplot as plt
import numpy as np
from _common import PRISM, require_arial, save
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import mplplots.palettes as palettes
from mplplots import assert_figure
from mplplots.palettes import BLUES, REDS
from mplplots.utils import add_axes_inches, auto_ticks, legend_inches

require_arial(bold=True)

x = np.linspace(0, 10, 50)

# ---------------------------------------------------------------------------
# 1. Default matplotlib vs GraphPadPrism
# ---------------------------------------------------------------------------
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), color=BLUES[4], linewidth=2, label=r"$\sin(x)$")
ax.plot(x, np.cos(x), color=REDS[4], linewidth=2, label=r"$\cos(x)$")
ax.set_title("Default matplotlib")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
ax.legend()
save(fig, "default_style")

plt.style.use(PRISM)

# Margins around a plot area, in inches, for the style's 11 to 14 pt text.
LEFT, BOTTOM, TOP = 0.8, 0.6, 0.4
# A legend beside the plot starts this far to its right, close to Prism's placement.
LEGEND_GAP = 0.4


def prism_figure(width: float, height: float, right: float) -> tuple[Figure, Axes]:
    """Return a figure and its axes: a ``width`` by ``height`` in plot area and its margins.

    Args:
        width: The x-axis length in inches.
        height: The y-axis length in inches.
        right: The space to the right of the plot area in inches.

    Returns:
        The figure and the axes.
    """
    fig = plt.figure(figsize=(LEFT + width + right, BOTTOM + height + TOP))
    return fig, add_axes_inches(fig, LEFT, BOTTOM, width, height)


def legend_beside(ax: Axes, width: float, height: float) -> None:
    """Add the legend to the right of a plot area placed by ``prism_figure``, top-aligned."""
    legend_inches(ax, LEFT + width + LEGEND_GAP, BOTTOM + height)


fig, ax = prism_figure(3, 2, right=0.2)
ax.plot(x, np.sin(x), color=BLUES[4], label=r"$\sin(x)$")
ax.plot(x, np.cos(x), color=REDS[4], label=r"$\cos(x)$")
auto_ticks(ax, left=0, right=10)
ax.set_title("GraphPadPrism + auto_ticks")
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
legend_inches(ax, LEFT + 3, BOTTOM + 2, loc="upper right", ncols=2)
assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)
save(fig, "graphpadprism_style")

# ---------------------------------------------------------------------------
# 2. Bar chart with GraphPadPrism
# ---------------------------------------------------------------------------
fig, ax = prism_figure(2, 2, right=0.2)
categories = ["A", "B", "C", "D", "E"]
values = [23, 45, 12, 67, 34]
ax.bar(categories, values, color=BLUES[:5], edgecolor="black")
auto_ticks(ax, bottom=0, top=80)
ax.set_xlabel("Category")
ax.set_ylabel("Value")
ax.set_title("Bar chart")
assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)
save(fig, "graphpadprism_bar")

# ---------------------------------------------------------------------------
# 3. Multi-line with GraphPadPrism + OCEAN palette
# ---------------------------------------------------------------------------
fig, ax = prism_figure(3, 2, right=1.7)
ocean = palettes.OCEAN
for i in range(6):
    ax.plot(x, np.sin(x + i * 0.4) * (1 - i * 0.1), color=ocean[i], label=f"Wave {i}")
auto_ticks(ax, left=0, right=10)
ax.set_xlabel("Time")
ax.set_ylabel("Amplitude")
ax.set_title("OCEAN palette + GraphPadPrism")
legend_beside(ax, 3, 2)
assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)
save(fig, "graphpadprism_ocean")

# ---------------------------------------------------------------------------
# 4. Grouped bar chart with GraphPadPrism + AUTUMN palette
# ---------------------------------------------------------------------------
fig, ax = prism_figure(3, 2, right=1.7)
autumn = palettes.AUTUMN
groups = ["Q1", "Q2", "Q3", "Q4"]
x_pos = np.arange(len(groups))
width = 0.25
for i, label in enumerate(["Revenue", "Costs", "Profit"]):
    rng = np.random.default_rng(i + 10)
    vals = rng.integers(20, 80, len(groups))
    ax.bar(x_pos + i * width, vals, width, color=autumn[i * 3], edgecolor="black", label=label)
auto_ticks(ax, bottom=0, top=100)
# Set the group labels after auto_ticks, which replaces the major tick locators.
ax.set_xticks(x_pos + width, groups)
ax.xaxis.set_minor_locator(ticker.NullLocator())
ax.set_xlim(x_pos[0] + width - 0.5, x_pos[-1] + width + 0.5)
ax.set_ylabel("Value")
ax.set_title("AUTUMN palette \u2014 grouped bar chart")
legend_beside(ax, 3, 2)
assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)
save(fig, "graphpadprism_grouped_bar")

# ---------------------------------------------------------------------------
# 5. Scatter with error bars + GraphPadPrism + CORAL palette
# ---------------------------------------------------------------------------
fig, ax = prism_figure(3, 2, right=1.7)
coral = palettes.CORAL
rng = np.random.default_rng(7)
for i in range(5):
    xc = rng.normal(2 + i * 1.5, 0.4, 12)
    yc = rng.normal(10 + i * 5, 2, 12)
    ax.errorbar(
        xc.mean(),
        yc.mean(),
        xerr=xc.std(),
        yerr=yc.std(),
        fmt="o",
        color=coral[i * 2],
        label=f"Group {i + 1}",
    )
auto_ticks(ax)
ax.set_xlabel("$X$ measure")
ax.set_ylabel("$Y$ measure")
ax.set_title("CORAL palette \u2014 error bars")
legend_beside(ax, 3, 2)
assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)
save(fig, "graphpadprism_errorbar")

print("All style examples saved to examples/")
