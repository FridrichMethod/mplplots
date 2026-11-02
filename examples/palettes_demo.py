"""Demonstrate mplplots color palettes."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

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

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Multi-line plot using CUSTOM palette
# ---------------------------------------------------------------------------
x = np.linspace(0, 2 * np.pi, 100)
fig, ax = plt.subplots(figsize=(8, 4))
for i, color in enumerate(CUSTOM):
    ax.plot(x, np.sin(x + i * 0.3), color=color, linewidth=2, label=f"Line {i}")
ax.set_title("CUSTOM palette — multi-line plot")
ax.legend(fontsize=7, ncol=3)
fig.savefig(f"{OUT}/custom_multiline.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 2. Colormap-derived family swatches
# ---------------------------------------------------------------------------
families = {"BLUES": BLUES, "GREENS": GREENS, "REDS": REDS, "PURPLES": PURPLES, "ORANGES": ORANGES}
fig, axes = plt.subplots(len(families), 1, figsize=(8, 4))
for ax, (name, colors) in zip(axes, families.items()):
    for i, c in enumerate(colors):
        ax.barh(0, 1, left=i, color=c, edgecolor="none")
    ax.set_xlim(0, len(colors))
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=10)
    ax.set_frame_on(False)
fig.suptitle("Colormap-derived families", fontsize=14)
fig.tight_layout()
fig.savefig(f"{OUT}/color_families.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 3. get_colors() with different colormaps
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(10, 4))
for ax, cmap_name in zip(axes, ["coolwarm", "viridis", "YlGnBu"]):
    colors = get_colors(cmap_name, 6, 0.15, 0.85)
    ax.bar(range(len(colors)), [3 + i * 0.5 for i in range(len(colors))], color=colors)
    ax.set_title(f'get_colors("{cmap_name}", 6)')
    ax.set_xticks([])
fig.tight_layout()
fig.savefig(f"{OUT}/get_colors_demo.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 4. Full catalogue — all 25 custom-style palettes as swatches
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

fig, axes = plt.subplots(len(ALL_NAMES), 1, figsize=(12, 18))
for ax, name in zip(axes, ALL_NAMES):
    colors = getattr(palettes, name)
    for i, c in enumerate(colors):
        ax.barh(0, 1, left=i, color=c, edgecolor="none")
    ax.set_xlim(0, len(colors))
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=9, fontweight="bold")
    ax.set_frame_on(False)
fig.suptitle("All 25 custom-style palettes", fontsize=14, fontweight="bold", y=0.995)
fig.tight_layout()
fig.savefig(f"{OUT}/all_palettes.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 5. Scatter plot — comparing three palette styles
# ---------------------------------------------------------------------------
rng = np.random.default_rng(42)
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, (name, pal_name) in zip(axes, [("OCEAN", "OCEAN"), ("ROSE", "ROSE"), ("FOREST", "FOREST")]):
    pal = getattr(palettes, pal_name)
    for i, c in enumerate(pal):
        xs = rng.normal(i, 0.3, 20)
        ys = rng.normal(i * 0.5, 0.4, 20)
        ax.scatter(xs, ys, color=c, s=40, alpha=0.8, edgecolors="none")
    ax.set_title(f"{name} — scatter")
    ax.set_xticks([])
    ax.set_yticks([])
fig.tight_layout()
fig.savefig(f"{OUT}/scatter_comparison.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 6. Area chart with SPRING palette
# ---------------------------------------------------------------------------
x = np.linspace(0, 4, 80)
fig, ax = plt.subplots(figsize=(8, 4))
spring = palettes.SPRING
base = np.zeros_like(x)
for i in range(6):
    y = np.abs(np.sin(x + i * 0.5)) * (1 + 0.3 * i)
    ax.fill_between(x, base, base + y, color=spring[i], alpha=0.85, label=f"Layer {i}")
    base += y
ax.set_title("SPRING palette — stacked area chart")
ax.legend(fontsize=8, ncol=3)
fig.savefig(f"{OUT}/spring_area.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 7. Pie chart with CANDY palette
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(5, 5))
candy = palettes.CANDY
sizes = [22, 18, 15, 13, 10, 8, 7, 4, 2, 1]
ax.pie(sizes, colors=candy[:10], startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
ax.set_title("CANDY palette — pie chart")
fig.savefig(f"{OUT}/candy_pie.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------
# 8. Horizontal bar chart with DUSK palette
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 5))
dusk = palettes.DUSK
categories = [f"Item {chr(65 + i)}" for i in range(11)]
values = [45, 38, 35, 30, 28, 24, 20, 18, 14, 10, 6]
ax.barh(categories, values, color=dusk)
ax.set_title("DUSK palette — horizontal bar chart")
ax.invert_yaxis()
fig.tight_layout()
fig.savefig(f"{OUT}/dusk_hbar.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print("All palette examples saved to examples/")
