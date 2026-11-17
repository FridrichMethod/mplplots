"""Demonstrate mplplots styles with palettes and auto_ticks."""

import matplotlib.pyplot as plt
import numpy as np
from _common import STYLE, add_axes, legend, require_arial, save
from matplotlib import ticker

import mplplots.palettes as palettes
from mplplots.palettes import BLUES, REDS
from mplplots.utils import auto_ticks

require_arial()

x = np.linspace(0, 10, 50)

# ---------------------------------------------------------------------------
# 1. Default matplotlib vs GraphPadPrism
# ---------------------------------------------------------------------------
fig, ax = plt.subplots()
ax.plot(x, np.sin(x), color=BLUES[4], linewidth=2, label="sin(x)")
ax.plot(x, np.cos(x), color=REDS[4], linewidth=2, label="cos(x)")
ax.set_title("Default matplotlib")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
save(fig, "default_style")

plt.style.use(STYLE)

fig = plt.figure(figsize=(3, 2.25))
ax = add_axes(fig, 0.5, 0.4, 2.25, 1.5)
ax.plot(x, np.sin(x), color=BLUES[4], label="sin(x)")
ax.plot(x, np.cos(x), color=REDS[4], label="cos(x)")
auto_ticks(ax, left=0, right=10)
ax.set_title("GraphPadPrism + auto_ticks")
ax.set_xlabel("x")
ax.set_ylabel("y")
legend(fig, ax, 2.75, 1.9, loc="upper right", ncols=2)
save(fig, "graphpadprism_style")

# ---------------------------------------------------------------------------
# 2. Bar chart with GraphPadPrism
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(2.75, 2.25))
ax = add_axes(fig, 0.5, 0.4, 2, 1.5)
categories = ["A", "B", "C", "D", "E"]
values = [23, 45, 12, 67, 34]
ax.bar(categories, values, color=BLUES[:5])
auto_ticks(ax, bottom=0, top=80)
ax.set_xlabel("Category")
ax.set_ylabel("Value")
ax.set_title("Bar chart")
save(fig, "graphpadprism_bar")

# ---------------------------------------------------------------------------
# 3. Multi-line with GraphPadPrism + OCEAN palette
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(4, 2.25))
ax = add_axes(fig, 0.5, 0.4, 2.5, 1.5)
ocean = palettes.OCEAN
for i in range(6):
    ax.plot(x, np.sin(x + i * 0.4) * (1 - i * 0.1), color=ocean[i], label=f"Wave {i}")
auto_ticks(ax, left=0, right=10)
ax.set_xlabel("Time")
ax.set_ylabel("Amplitude")
ax.set_title("OCEAN palette + GraphPadPrism")
legend(fig, ax, 3.1, 1.9)
save(fig, "graphpadprism_ocean")

# ---------------------------------------------------------------------------
# 4. Grouped bar chart with GraphPadPrism + AUTUMN palette
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(4, 2.25))
ax = add_axes(fig, 0.5, 0.4, 2.5, 1.5)
autumn = palettes.AUTUMN
groups = ["Q1", "Q2", "Q3", "Q4"]
x_pos = np.arange(len(groups))
width = 0.25
for i, label in enumerate(["Revenue", "Costs", "Profit"]):
    rng = np.random.default_rng(i + 10)
    vals = rng.integers(20, 80, len(groups))
    ax.bar(x_pos + i * width, vals, width, color=autumn[i * 3], label=label)
auto_ticks(ax, bottom=0, top=100)
# Set the group labels after auto_ticks, which replaces the major tick locators.
ax.set_xticks(x_pos + width, groups)
ax.xaxis.set_minor_locator(ticker.NullLocator())
ax.set_xlim(x_pos[0] + width - 0.5, x_pos[-1] + width + 0.5)
ax.set_ylabel("Value")
ax.set_title("AUTUMN palette — grouped bar chart")
legend(fig, ax, 3.1, 1.9)
save(fig, "graphpadprism_grouped_bar")

# ---------------------------------------------------------------------------
# 5. Scatter with error bars + GraphPadPrism + CORAL palette
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(4, 2.25))
ax = add_axes(fig, 0.5, 0.4, 2.5, 1.5)
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
        markersize=8,
        capsize=4,
        label=f"Group {i + 1}",
    )
auto_ticks(ax)
ax.set_xlabel("X measure")
ax.set_ylabel("Y measure")
ax.set_title("CORAL palette — error bars")
legend(fig, ax, 3.1, 1.9)
save(fig, "graphpadprism_errorbar")

print("All style examples saved to examples/")
