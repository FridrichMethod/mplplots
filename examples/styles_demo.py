"""Demonstrate mplplots styles with palettes and auto_ticks."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker

import mplplots.palettes as palettes
from mplplots.palettes import BLUES, REDS
from mplplots.utils import auto_ticks

STYLE = "mplplots.styles.GraphPadPrism"
OUT = Path(__file__).resolve().parent

x = np.linspace(0, 10, 50)

# ---------------------------------------------------------------------------
# 1. Default matplotlib vs GraphPadPrism
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 4))
ax.plot(x, np.sin(x), color=BLUES[4], linewidth=2, label="sin(x)")
ax.plot(x, np.cos(x), color=REDS[4], linewidth=2, label="cos(x)")
ax.set_title("Default matplotlib")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
fig.savefig(f"{OUT}/default_style.png", dpi=150, bbox_inches="tight")
plt.close(fig)

with plt.style.context(STYLE):
    fig, ax = plt.subplots()
    ax.plot(x, np.sin(x), color=BLUES[4], linewidth=2, label="sin(x)")
    ax.plot(x, np.cos(x), color=REDS[4], linewidth=2, label="cos(x)")
    auto_ticks(ax, left=0, right=10, bottom=-1.2, top=1.2)
    ax.set_title("GraphPadPrism + auto_ticks")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    fig.savefig(f"{OUT}/graphpadprism_style.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

# ---------------------------------------------------------------------------
# 2. Bar chart with GraphPadPrism
# ---------------------------------------------------------------------------
with plt.style.context(STYLE):
    fig, ax = plt.subplots()
    categories = ["A", "B", "C", "D", "E"]
    values = [23, 45, 12, 67, 34]
    ax.bar(categories, values, color=BLUES[:5])
    auto_ticks(ax, bottom=0, top=80)
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    ax.set_title("Bar chart")
    fig.savefig(f"{OUT}/graphpadprism_bar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

# ---------------------------------------------------------------------------
# 3. Multi-line with GraphPadPrism + OCEAN palette
# ---------------------------------------------------------------------------
with plt.style.context(STYLE):
    fig, ax = plt.subplots(figsize=(6, 4))
    ocean = palettes.OCEAN
    for i in range(6):
        ax.plot(x, np.sin(x + i * 0.4) * (1 - i * 0.1), color=ocean[i], label=f"Wave {i}")
    auto_ticks(ax, left=0, right=10)
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_title("OCEAN palette + GraphPadPrism")
    ax.legend(fontsize=7, ncol=2)
    fig.savefig(f"{OUT}/graphpadprism_ocean.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

# ---------------------------------------------------------------------------
# 4. Grouped bar chart with GraphPadPrism + AUTUMN palette
# ---------------------------------------------------------------------------
with plt.style.context(STYLE):
    fig, ax = plt.subplots(figsize=(7, 4))
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
    ax.legend()
    fig.savefig(f"{OUT}/graphpadprism_grouped_bar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

# ---------------------------------------------------------------------------
# 5. Scatter with error bars + GraphPadPrism + CORAL palette
# ---------------------------------------------------------------------------
with plt.style.context(STYLE):
    fig, ax = plt.subplots()
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
    ax.legend(fontsize=7)
    fig.savefig(f"{OUT}/graphpadprism_errorbar.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

print("All style examples saved to examples/")
