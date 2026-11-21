---
name: mplplots
description: Use when creating, restyling or reviewing Matplotlib or Seaborn figures in a project that has mplplots installed, including publication figures, multi-panel layouts, colour choices, statistics panels and figure export to PNG, PDF or SVG.
---

# mplplots

mplplots holds the Personal figure style: a Matplotlib style file, a toolkit that lays figures
out in inches and saves them, and a checker that turns the style rules into code. A figure is
done when `mpp.assert_figure(fig)` passes and its saved PNG looks right at print size.

The rules behind each step, each with an id (T1, L4, C7, S5, ...), are in
`references/style-guide.md` beside this file. Read its section for the kind of panel at hand
(typography, lines and marks, colour, layout, statistics, export) before drawing it.

## When to use

- Creating a figure or a multi-panel figure for a paper, a poster or a report.
- Restyling an existing Matplotlib or Seaborn figure, or its script, to the Personal style.
- Reviewing a figure or a figure script against the style rules.

Not for interactive or web plots (Plotly, Bokeh, Altair), which the style does not reach.

## Setup check

```bash
python -m mplplots --version  # "mplplots X.Y.Z"; "No module named mplplots": not installed here
python -c "import matplotlib.font_manager as fm; print({f.style for f in fm.fontManager.ttflist if f.name == 'Arial'})"
```

The second command prints a set with `'normal'` and `'italic'` when Arial Regular and Italic are
installed. Without them the text falls back to an Arial-like font and `check_figure` reports
`font-fallback`: acceptable for a draft, not for a final figure. After installing fonts, delete
Matplotlib's cache directory (`matplotlib.get_cachedir()`) so it finds them.
`mplplots install-skill --project . --check` reports a copy of this skill that is out of date.

## Workflow

1. `import mplplots as mpp` and `mpp.use()`, before the first figure is created.
2. Take colours from the project's palette module of `ColorPair` roles. If the project has none,
   create one with a `check_palette` test (guide: "A project palette").
3. Lay the figure out in round inches with `mpp.grid_inches` or `mpp.add_axes_inches`.
4. Draw, following the text and mark rules: no `fontsize` or `fontweight`, variables as math
   text, explicit line widths when curves share a panel, reference lines with `REFERENCE_LINE`.
5. `mpp.assert_figure(fig)`; fix what it reports, and pass `ignore` only with a stated reason.
6. `mpp.save_figure(fig, path, caption=...)`, then look at the PNG.

```python
import numpy as np

import mplplots as mpp

mpp.use()  # 1

# 2: in a project this is `from <package>.palette import PALETTE`; two stand-in roles here.
PALETTE = {
    "reference": mpp.ColorPair(fill="#cccccc", edge="#7a7a7a"),
    "treated": mpp.ColorPair(fill="#c7e9c0", edge="#4f9d58"),
}
assert mpp.check_palette(PALETTE) == []
reference, treated = PALETTE["reference"], PALETTE["treated"]

fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)  # 3: 2.5 by 1.5 in axes, default margins

t = np.linspace(0.0, 10.0, 101)  # 4
slow, fast, sem = np.exp(-t / 4.0), np.exp(-t / 2.0), np.full_like(t, 0.04)
mpp.plot_mean_sem(ax, t, slow, sem, fill=treated.fill, edge=treated.edge, label="Treated")
mpp.plot_mean_sem(
    ax, t, fast, sem, fill=reference.fill, edge=reference.edge, label="Reference", zorder=5.0
)  # the reference series last and on top (L6)
ax.set(xlim=(0.0, 10.0), ylim=(0.0, 1.0), xlabel="Time $t$ (s)", ylabel="Signal (a.u.)")
ax.legend()

mpp.assert_figure(fig)  # 5
caption = "Mean of n = 4 replicates; bands are 1 SEM either side, not a confidence interval."
paths = mpp.save_figure(fig, "figures/decay", caption=caption)  # 6: PNG, PDF, SVG, caption
```

`paths[0]` is the PNG. Open it and look at it at print size: text that collides or is cut off, a
legend over the data, series that cannot be told apart without colour.

## API by task

Every name is importable from `mplplots`; `help(mpp.<name>)` gives the arguments.

| Task | Names |
| --- | --- |
| Apply a style | `use`, `context`, `STYLES`, `DEFAULT_STYLE`, `style_path` |
| Colours | `ColorPair`, `lighten`, `darken`, `contrast_ratio`, `check_palette` |
| Alphas and line presets | `SCATTER_ALPHA`, `BAND_ALPHA`, `LINE_ALPHA`, `REFERENCE_LINE`, `SECONDARY_LINESTYLE` |
| Figure and axes size | `grid_inches`, `figure_size`, `COLUMN_WIDTHS`, `add_axes_inches` |
| Labels, legends, ticks | `add_shared_ylabel`, `legend_inches`, `align_legends_left`, `suptitle_inches`, `auto_ticks` |
| Plot elements | `plot_mean_sem`, `plot_distribution`, `significance_stars`, `box_axes` |
| Check a figure | `check_figure`, `assert_figure`, `Issue`, `StyleError`, `StyleWarning` |
| Save | `save_figure` |
| Fonts | `add_custom_fonts` |

`plt.style.use("mplplots.styles.Personal")` applies the style without importing mplplots. On the
command line, `mplplots styles` lists the packaged styles and their files, `mplplots guide`
prints the style guide and `mplplots rules` prints the snippet for a project's `AGENTS.md`.

## Common mistakes

| Mistake | Result | Instead |
| --- | --- | --- |
| `mpp.use()` after the figure exists | The figure keeps the old look | Apply the style first |
| `sns.set_theme()` or `sns.set_style()` | Seaborn replaces the style's settings | Call neither; Seaborn plots draw under the style |
| `fontsize=` so that text fits | `font-size` error | Grow the axes or the figure (T1) |
| `layout="tight"` or `layout="constrained"` | `layout-engine` error; axis lengths differ between figures | Margins in `grid_inches` (S2, S5) |
| `fig.tight_layout()` | No `layout-engine` error, as the call leaves no engine behind; a `round-inches` warning, as the axes move off the inch grid | Margins in `grid_inches` (S2, S5) |
| `fig.savefig` instead of `save_figure` | One format, a date stamp in the PDF and SVG, a crop under a local `savefig.bbox: tight` | `mpp.save_figure` (X1 to X4) |
| A colour left to Matplotlib | `default-color` warning | A role of the project palette (C1) |
| A panel letter such as `"a"` or `"(b)"` | `panel-letter` warning | Letters go in at manuscript assembly (S6) |
| `fig.supxlabel` for a shared x label | The label sits at the figure edge, far from the ticks | The bottom panel's `set_xlabel` (S7) |
| A pasted superscript or U+2212 minus | `script-glyph` error, `unicode-minus` warning | `"$^2$"` math text and the ASCII `-` (T5, T6) |
| `ignore=` without a comment | The next reader cannot tell a waiver from a bug | State the reason beside it (S3) |
