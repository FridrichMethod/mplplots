"""Demonstrate mplplots color palettes with the Personal style."""

from collections.abc import Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
from _common import PERSONAL, require_arial, save
from matplotlib.figure import Figure

import mplplots.palettes as palettes
from mplplots.palettes import (
    BLUES,
    CUSTOM,
    GREENS,
    ORANGES,
    PURPLES,
    REDS,
    get_colors,
)
from mplplots.utils import add_axes_inches, auto_ticks, legend_inches, suptitle_inches

require_arial()
plt.style.use(PERSONAL)


def swatches(
    fig: Figure,
    rows: Mapping[str, Sequence[str]],
    left: float,
    bottom: float,
    cell: tuple[float, float],
    gap: float,
) -> None:
    """Draw one labeled row of color swatches per palette, top to bottom.

    Args:
        fig: The figure to draw on.
        rows: Palette name -> colors, in the order the rows are drawn from the top.
        left: Distance from the figure's left edge to the swatches, in inches.
        bottom: Distance from the figure's bottom edge to the lowest row, in inches.
        cell: Width and height of one swatch, in inches.
        gap: Vertical space between rows, in inches.
    """
    cell_width, cell_height = cell
    for row, (name, colors) in enumerate(reversed(list(rows.items()))):
        ax = add_axes_inches(
            fig, left, bottom + row * (cell_height + gap), len(colors) * cell_width, cell_height
        )
        for i, c in enumerate(colors):
            ax.barh(0, 1, left=i, height=1, color=c, edgecolor="none")
        ax.set_xlim(0, len(colors))
        ax.set_ylim(-0.5, 0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylabel(name, rotation=0, ha="right", va="center")
        ax.set_frame_on(False)


# ---------------------------------------------------------------------------
# 1. Multi-line plot using CUSTOM palette
# ---------------------------------------------------------------------------
x = np.linspace(0, 2 * np.pi, 100)
fig = plt.figure(figsize=(4.5, 2.75))
ax = add_axes_inches(fig, 0.5, 0.4, 3, 2)
# Curves that share a panel set their width (rule L4 of the style guide).
for i, color in enumerate(CUSTOM):
    ax.plot(x, np.sin(x + i * 0.3), color=color, linewidth=1.2, label=f"Line {i}")
auto_ticks(ax, left=0)
ax.set_title("CUSTOM palette \u2014 multi-line plot")
legend_inches(ax, 3.6, 2.4)
save(fig, "custom_multiline")

# ---------------------------------------------------------------------------
# 2. Colormap-derived family swatches
# ---------------------------------------------------------------------------
families = {"BLUES": BLUES, "GREENS": GREENS, "REDS": REDS, "PURPLES": PURPLES, "ORANGES": ORANGES}
fig = plt.figure(figsize=(4, 1.9))
swatches(fig, families, left=0.75, bottom=0.1, cell=(0.4, 0.2), gap=0.1)
suptitle_inches(fig, "Colormap-derived families")
save(fig, "color_families")

# ---------------------------------------------------------------------------
# 3. get_colors() with different colormaps
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(6, 1.8))
for i, cmap_name in enumerate(["coolwarm", "viridis", "YlGnBu"]):
    ax = add_axes_inches(fig, 0.4 + i * 2, 0.2, 1.5, 1.25)
    colors = get_colors(cmap_name, 6, 0.15, 0.85)
    ax.bar(range(len(colors)), [3 + i * 0.5 for i in range(len(colors))], color=colors)
    ax.set_title(f'get_colors("{cmap_name}", 6)')
    ax.set_xticks([])
save(fig, "get_colors_demo")

# ---------------------------------------------------------------------------
# 4. Full catalog: all 25 custom-style palettes as swatches
# ---------------------------------------------------------------------------
ALL_NAMES = [
    "CUSTOM",
    "PASTEL",
    "WARM",
    "COOL",
    "EARTH",
    "OCEAN",
    "ROSE",
    "FOREST",
    "LAVENDER",
    "SUNSET",
    "COASTAL",
    "SPRING",
    "SUMMER",
    "AUTUMN",
    "WINTER",
    "DAWN",
    "DUSK",
    "CANDY",
    "SMOKE",
    "VINTAGE",
    "NORDIC",
    "MEADOW",
    "CORAL",
    "TROPICAL",
    "POWDER",
]

fig = plt.figure(figsize=(4.25, 5.5))
swatches(
    fig,
    {name: getattr(palettes, name) for name in ALL_NAMES},
    left=0.75,
    bottom=0.1,
    cell=(0.3, 0.15),
    gap=0.05,
)
suptitle_inches(fig, "All 25 custom-style palettes")
save(fig, "all_palettes")

# ---------------------------------------------------------------------------
# 5. Scatter plot: comparing three palette styles
# ---------------------------------------------------------------------------
rng = np.random.default_rng(42)
fig = plt.figure(figsize=(5.5, 1.7))
for i, name in enumerate(["OCEAN", "ROSE", "FOREST"]):
    ax = add_axes_inches(fig, 0.25 + i * 1.75, 0.1, 1.5, 1.25)
    pal = getattr(palettes, name)
    for j, c in enumerate(pal):
        xs = rng.normal(j, 0.3, 20)
        ys = rng.normal(j * 0.5, 0.4, 20)
        ax.scatter(xs, ys, color=c, s=10, alpha=0.8, edgecolors="none")
    ax.set_title(f"{name} \u2014 scatter")
    ax.set_xticks([])
    ax.set_yticks([])
save(fig, "scatter_comparison")

# ---------------------------------------------------------------------------
# 6. Area chart with SPRING palette
# ---------------------------------------------------------------------------
x = np.linspace(0, 4, 80)
fig = plt.figure(figsize=(4.5, 2.5))
ax = add_axes_inches(fig, 0.5, 0.4, 3, 1.75)
spring = palettes.SPRING
base = np.zeros_like(x)
for i in range(6):
    y = np.abs(np.sin(x + i * 0.5)) * (1 + 0.3 * i)
    ax.fill_between(x, base, base + y, color=spring[i], alpha=0.85, label=f"Layer {i}")
    base += y
auto_ticks(ax, left=0, right=4, bottom=0)
ax.set_title("SPRING palette \u2014 stacked area chart")
legend_inches(ax, 3.6, 2.15)
save(fig, "spring_area")

# ---------------------------------------------------------------------------
# 7. Pie chart with CANDY palette
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(2.5, 2.5))
ax = add_axes_inches(fig, 0.25, 0.1, 2, 2)
candy = palettes.CANDY
sizes = [22, 18, 15, 13, 10, 8, 7, 4, 2, 1]
ax.pie(sizes, colors=candy[:10], startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("CANDY palette \u2014 pie chart")
save(fig, "candy_pie")

# ---------------------------------------------------------------------------
# 8. Horizontal bar chart with DUSK palette
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(3.5, 3))
ax = add_axes_inches(fig, 0.6, 0.4, 2.6, 2.25)
dusk = palettes.DUSK
categories = [f"Item {chr(65 + i)}" for i in range(11)]
values = [45, 38, 35, 30, 28, 24, 20, 18, 14, 10, 6]
ax.barh(categories, values, color=dusk)
ax.set_title("DUSK palette \u2014 horizontal bar chart")
ax.invert_yaxis()
auto_ticks(ax, left=0)
save(fig, "dusk_hbar")

print("All palette examples saved to examples/")
