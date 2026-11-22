# Style guide

The rules for figures in the Personal style, the default style of mplplots, each with an id
(T1, L1, ...). The guide names a value where a rule needs it; `Personal.mplstyle` holds every
value, from fonts and line widths to export settings (`mplplots styles` prints its path).

Every `python` block below runs as written, in order, in one session that starts with
`import matplotlib.pyplot as plt`, `import numpy as np` and `import mplplots as mpp`.

## Applying the style

Apply the style once, before the first figure is created: Matplotlib reads its settings when it
creates an artist, so a figure made earlier keeps the old look.

```python
mpp.use()  # the Personal style; mpp.use("GraphPadPrism") applies another packaged style

# Stand-ins for two roles of a project palette (see "A project palette").
GREEN = mpp.ColorPair(fill="#c7e9c0", edge="#4f9d58")
GRAY = mpp.ColorPair(fill="#cccccc", edge="#7a7a7a")

x = np.linspace(0.0, 10.0, 101)
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)
ax.plot(x, np.exp(-x / 4.0), color=GREEN.edge, linewidth=1.2, label="Treated")
ax.set(xlim=(0.0, 10.0), xlabel="Time (s)", ylabel="Signal (a.u.)")
ax.legend()
mpp.assert_figure(fig)
mpp.save_figure(fig, "quick_start", caption="Signal after the pulse.")
```

`with mpp.context():` applies the style inside a block only, and
`plt.style.use("mplplots.styles.Personal")` loads it without importing mplplots. Final figures
need Arial Regular and Italic; without them the style falls back silently to Helvetica, an
Arial-compatible clone or DejaVu Sans. `mpp.add_custom_fonts(path)` registers font files.

## Typography

- **T1.** Every text element is Arial Regular 8 pt: tick labels, axis labels, titles, legends
  and annotations. Figure code passes no `fontsize` or `fontweight`. If text does not fit, the
  panel or the figure grows: shrinking text to make it fit is how a figure becomes unreadable.
- **T2.** Titles are short and in sentence case ("Signal after washout", not "Signal After
  Washout"). The caption carries the detail.
- **T3.** A Greek letter that is part of a name (the alpha of a C-alpha atom, the beta of a
  beta-hairpin) and the angstrom sign are upright literal characters, written as escapes so the
  source stays ASCII: `"C\u03b1 RMSF (\u00c5)"`. Math text sets `$\alpha$` in italic, and an
  italic letter reads as a variable.
- **T4.** Variables and formulas are math text (`"$x$"`, `r"$\sin(x)$"`). Upright words inside
  math use `\mathrm{}`. The style sets math in the text font: variables in italic, function
  names, numbers and operators upright.
- **T5.** Exponents and subscripts are math text (`"\u00c5$^2$"`, `"kJ mol$^{-1}$"`), never
  precomposed characters such as U+00B2. A precomposed glyph has the font's fixed size and
  baseline, so it does not match a real superscript; Arial also lacks a superscript minus.
- **T6.** Minus signs are the ASCII hyphen-minus in tick labels and in hand-written text alike.
  The style sets `axes.unicode_minus: False`, so a tick label `-2` matches a label such as
  `"Contrast (A - B)"`. Never paste U+2212 into a label.
- **T7.** A statistics annotation is one `$...$` per line with upright metric names
  (`rf"$\mathrm{{Cohen's}}\ d = {d:.2f}$"`, `rf"$n = {n}$"`), `linespacing=1.35`, placed in a
  panel corner in axes coordinates, without a frame.

```python
d, n = 0.82, 6
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5, top=0.35)  # 0.35 in above for the title
ax.plot(x, 40.0 * np.exp(-x / 3.0), color=GREEN.edge, linewidth=1.2)
ax.set_title("Energy after the pulse")
ax.set(xlim=(0.0, 10.0), ylim=(0.0, 40.0), xlabel="Time $t$ (s)", ylabel="Energy (kJ mol$^{-1}$)")
stats = "\n".join([rf"$\mathrm{{Cohen's}}\ d = {d:.2f}$", rf"$n = {n}$"])
ax.text(0.97, 0.95, stats, transform=ax.transAxes, ha="right", va="top", linespacing=1.35)
mpp.assert_figure(fig)
plt.close(fig)
```

```text
# What these rules exclude:
ax.set_title("Title", fontsize=10)    # a second type size (T1)
ax.set_ylabel(r"C$\alpha$ RMSF")      # an italic alpha reads as a variable (T3)
ax.set_xlabel("sin(x)")               # a formula as upright text (T4)
ax.set_ylabel("Area (\u00c5\u00b2)")  # a precomposed superscript two (T5)
```

## Lines and marks

- **L1.** Axis lines are 0.8 pt. Major ticks are 0.8 pt wide and 3.5 pt long, minor ticks
  0.6 pt and 2 pt. The top and right spines are off. The style sets all of this, so figure code
  leaves spines and ticks alone. A marginal or strip panel shows only its bottom spine. A full
  box is an explicit exception: `mpp.box_axes(ax)`.
- **L2.** Minor ticks are on by default. Turn them off on dense and categorical axes
  (`ax.xaxis.set_minor_locator(NullLocator())`). Set the tick spacing per figure with
  `MultipleLocator` or `mpp.auto_ticks(ax)`; the style sets only visibility, size and width.
- **L3.** No grid. If one is needed: alpha 0.18, 0.4 pt, `zorder=0`.
- **L4.** Give a line width when several curves share a panel: 1.2 pt for mean curves, 1.8 pt
  for the one emphasized state, 1.0 pt for distribution outlines, 1.4 pt for regression lines.
  A bare `ax.plot` draws the style's 2 pt.
- **L5.** Reference and threshold lines (y = x, a cutoff) are dashed, gray 0.55, 0.8 pt:
  `**mpp.REFERENCE_LINE`. A region or domain is a shaded span (`ax.axvspan`), not a line.
- **L6.** When series overlap, the reference series is drawn last, with the highest `zorder`, so
  no other series hides it.
- **L7.** Scatter: `s=22`, fill face, edge-color edge 0.5 pt wide, `alpha=mpp.SCATTER_ALPHA`.
- **L8.** Bars set their edge line width explicitly. A legend proxy copies the plotted artist's
  face, edge, line width, line style, alpha, marker and hatch; `mpp.plot_distribution` returns
  such a proxy.
- **L9.** Legends have no frame and sit in the upper right by default. `mpp.legend_inches`
  anchors one in inches, for example beside the axes; `mpp.align_legends_left` gives a stack of
  panel legends one left edge.
- **L10.** A color bar has its own axes, placed in inches and passed as `cax`, not space taken
  from the panel (`fig.colorbar(ax=...)`). Its outline is 0.6 pt, the minor tick width, and its
  ticks are 2.5 pt long, so it reads lighter than the panel's axis lines.
- **L11.** An artist with thousands of marks (an embedding, a dense scatter) is drawn with
  `rasterized=True`: the PDF and SVG hold it as a 600 dpi image, and the axes and text stay
  vector. Data are never thinned to shrink a file.

```python
from matplotlib.ticker import MultipleLocator

rng = np.random.default_rng(0)
measured = rng.uniform(0.5, 9.5, 40)
predicted = measured + rng.normal(0.0, 0.6, 40)
slope, intercept = np.polyfit(measured, predicted, 1)
dots = {"s": 22, "linewidths": 0.5, "alpha": mpp.SCATTER_ALPHA}  # the scatter recipe (L7)
fig, (ax,) = mpp.grid_inches(width=2.0, height=2.0)
ax.axline((0.0, 0.0), slope=1.0, zorder=0, **mpp.REFERENCE_LINE)  # under the data
ax.scatter(measured, predicted, facecolor=GREEN.fill, edgecolor=GREEN.edge, **dots)
ax.plot(x, slope * x + intercept, color=GREEN.edge, linewidth=1.4, alpha=mpp.LINE_ALPHA)
ax.set(xlim=(0.0, 10.0), ylim=(0.0, 12.0), xlabel="Measured (a.u.)", ylabel="Predicted (a.u.)")
ax.yaxis.set_major_locator(MultipleLocator(4.0))  # tick spacing set per figure (L2)
mpp.assert_figure(fig)
plt.close(fig)

fig, (ax, cax) = mpp.grid_inches(1, 2, width=[2.0, 0.1], height=2.0, wspace=0.1, right=0.6)
cloud = rng.normal(0.0, 1.0, (2, 5000))
dense = {"s": 4, "linewidths": 0, "rasterized": True}  # one image in the PDF and SVG (L11)
points = ax.scatter(*cloud, c=np.hypot(*cloud), **dense)
ax.set(xlim=(-4.0, 4.0), ylim=(-4.0, 4.0), xlabel="Component 1", ylabel="Component 2")
colorbar = fig.colorbar(points, cax=cax)  # in its own 0.1 in wide axes (L10)
colorbar.set_label("Distance from the center")
colorbar.outline.set_linewidth(0.6)
colorbar.ax.tick_params(length=2.5)
mpp.assert_figure(fig)
plt.close(fig)
```

## Color

- **C1.** A project defines one palette module that maps each role to a `ColorPair(fill, edge)`.
  Figure code takes colors from it, never from Matplotlib's default cycle, which the style
  keeps: a curve drawn without a color gets a cycle color, and `check_figure` reports it.
- **C2.** The edge carries identity: lines, marker edges, bar borders. The fill is its pale
  partner, drawn under alpha: bands, bar faces, scatter faces. An edge is darker than its fill.
- **C3.** Alphas: `SCATTER_ALPHA` 0.6 for dots, histogram and density fills; `BAND_ALPHA` 0.5 for
  mean +/- SEM and confidence bands; `LINE_ALPHA` 0.95 for curves. Judge a fill at its alpha: one
  that looks right at full opacity can vanish at 0.5.
- **C4.** A hue has at most two lightness levels, each a fill and edge pair. A further member of
  a family is derived with `lighten()`, not given a new constant. A third level would compress
  the contrast between the two that the comparison rests on.
- **C5.** A second variable within one hue uses a channel other than color: the dash pattern
  `SECONDARY_LINESTYLE`, hollow markers (`facecolor="white"`), hollow bars (`facecolor="none"`).
- **C6.** Series that share an axis stay distinguishable without color: keep a marker, line
  style, hatch, direct label or position cue. Grayscale prints and color-vision deficiency
  remove hue first.
- **C7.** An edge drawn at `LINE_ALPHA` on white has a contrast ratio of at least 3. A lighter
  warm hue (yellow, orange) is a per-role exception with its own floor and a non-color cue
  (`check_palette(floors=...)`). The ratio is a screening floor, not a replacement for looking
  at the thin lines at print size.
- **C8.** An identity hue anchors a color map only when that end of the map denotes the
  identity, and the label or caption states the direction. A magnitude uses its own sequential
  map (the style's default, `viridis`) or diverging map (`RdBu_r` for values around zero).
- **C9.** A role keeps its color in every figure of a project, and a hue is not reused for an
  unrelated role within a figure.

```python
mean, sem = 1.0 + 0.5 * np.sin(x), np.full_like(x, 0.12)
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5, right=1.1)
dashed = mpp.SECONDARY_LINESTYLE  # a second variable within the green hue (C5)
mpp.plot_mean_sem(ax, x, mean, sem, fill=GREEN.fill, edge=GREEN.edge, label="Resting")
mpp.plot_mean_sem(
    ax, x, mean + 0.6, sem, fill=GREEN.fill, edge=GREEN.edge, linestyle=dashed, label="Stimulated"
)
mpp.plot_mean_sem(
    ax, x, mean - 0.4, sem, fill=GRAY.fill, edge=GRAY.edge, label="Reference", zorder=5.0
)  # the reference on top (L6)
ax.set(xlim=(0.0, 10.0), xlabel="Time (s)", ylabel="Signal (a.u.)")
mpp.legend_inches(ax, 3.2, 1.9)  # beside the axes, level with their top
mpp.assert_figure(fig)
plt.close(fig)

assert mpp.contrast_ratio(GREEN.edge, alpha=mpp.LINE_ALPHA) >= 3.0  # C7
lighter_edge = mpp.lighten(GREEN.edge, 0.3)  # a further member of the green family (C4)
```

## Layout and size

- **S1.** A figure's width is a column preset (`mpp.COLUMN_WIDTHS`: single 3.5, onehalf 5.0,
  double 7.0 in; `mpp.figure_size`) or follows from its axis lengths (`mpp.grid_inches`).
- **S2.** Figure size, axis lengths and margins are chosen on a 0.1 or 0.25 in grid; gaps may
  use 0.05 in. They are named inch constants, placed with `grid_inches` or `add_axes_inches`,
  not with `tight_layout`, constrained layout, `subplots_adjust` or a cropped save, which
  resize the axes to fit the labels and give the same plot a different size in every figure.
- **S3.** A dimension derived from a physical scale stays exact and unrounded, with its
  derivation beside the constant (`FULL_WIDTH = 2.5 * 143 / 100  # 100 units per 2.5 in`).
  Its figure passes `ignore={"round-inches"}` to the checker, with the derivation as reason.
- **S4.** Figures meant to be read against each other keep the same physical data scale, data
  units per inch, even when they show different windows.
- **S5.** Margins for 8 pt text: 0.6 in on the left for tick labels and a y label, 0.4 in below,
  0.1 in on top (0.35 in above for a title) and 0.2 in on the right, where the label of the
  tick at the end of the x-axis overhangs the axes by half its width; 0.1 in is enough there
  for a label of up to three characters. `grid_inches` defaults to them, with `top=0.35` passed
  for a title. Stacked panels that share x need a 0.05 to 0.2 in gap; panels with their own
  tick labels need at least 0.22 in, which is 0.25 in on the grid.
- **S6.** No panel letters in the figure. They are added when the manuscript is assembled, in
  the journal's style, and captions refer to panels by position ("top", "left to right").
- **S7.** A shared x label is the bottom panel's `set_xlabel`, never `supxlabel`, which pins the
  label to the figure's bottom edge instead of the ticks. A shared y label is
  `add_shared_ylabel`, called once the panels are drawn: it measures the tick labels and keeps
  the style's label gap from them.
- **S8.** No text overlaps another: tick labels, axis labels, titles, annotations and legend
  entries keep clear of each other. When two collide, thin the ticks, lengthen the axis or move
  the annotation or the legend; the text keeps its size (T1).

```python
fig, axes = mpp.grid_inches(3, 1, width=3.0, height=0.8, hspace=0.2, sharex=True)
rows = [(GRAY, "-", "Reference", 2), (GREEN, "-", "Resting", 3), (GREEN, dashed, "Stimulated", 4)]
for ax, (pair, linestyle, label, tau) in zip(axes, rows):
    ax.plot(x, np.exp(-x / tau), color=pair.edge, linestyle=linestyle, linewidth=1.2, label=label)
    ax.set_ylim(0.0, 1.0)
    ax.legend()
axes[-1].set(xlim=(0.0, 10.0), xlabel="Time (s)")  # the shared x label (S7)
mpp.add_shared_ylabel(fig, axes, "Signal (a.u.)")
mpp.align_legends_left(axes)  # one left edge for the three legends
mpp.assert_figure(fig)
plt.close(fig)

fig = plt.figure(figsize=mpp.figure_size("double", height=2.5))  # 7.0 by 2.5 in
ax = mpp.add_axes_inches(fig, left=0.6, bottom=0.4, width=6.3, height=2.0)
plt.close(fig)
```

## Statistics

- **E1.** A 95% confidence interval goes on a panel that compares a few discrete groups, which
  readers judge by whether the intervals overlap. A +/-1 SEM band is only for a dense profile, and
  its caption says it is not a confidence interval. At small n a 95% interval is wider than
  +/-1.96 SEM: with n = 6 its half-width is 2.571 SEM.
- **E2.** The unit of replication is the independent replicate, never the frame, cell or pixel.
  Reduce each replicate to one value first, or resample whole replicates. Samples within one
  replicate are correlated, so an interval over them is spuriously narrow.
- **E3.** A published interval at small n is a BCa bootstrap interval with at least 10,000
  resamples. A plain percentile bootstrap undercovers at small n.
- **E4.** With few replicates, the individual values are overlaid: a summary hides a bimodal set.
- **E5.** Significance stars come from the multiplicity-corrected value of a comparison family
  (`significance_stars`: `***` below 0.001, `**` below 0.01, `*` below 0.05, otherwise `n.s.`),
  and only comparisons discussed in the text are annotated.
- **E6.** A shift within one group is shown as two dashed median levels and one bare signed
  value, such as `+0.37 nm`; the interval, effect size and q value go in the caption. The levels
  and the value come from the same estimator, so the gap never disagrees with the number.
- **E7.** A distribution is drawn from pre-binned counts as a curve through the bin centers,
  filled to zero, in percent of samples per bin (`plot_distribution`): no staircase, no kernel
  density, which read as a ladder and flatten sharp peaks. The bin width and the denominator go
  in the caption, and panels that share y share a bin grid.

```python
from matplotlib.ticker import NullLocator

# One value per replicate and 95% BCa intervals (10,000 resamples) from the analysis (E2, E3).
groups, pairs = ["Reference", "Treated"], [GRAY, GREEN]
replicates = [np.array([1.0, 1.2, 0.9, 1.1, 1.05, 0.95]), np.array([1.8, 2.1, 1.6, 2.0, 1.9, 2.2])]
means = np.array([values.mean() for values in replicates])
ci_low, ci_high = np.array([0.96, 1.79]), np.array([1.11, 2.07])
q = 0.004  # corrected over the comparison family (E5)
positions, yerr = np.arange(len(groups)), [means - ci_low, ci_high - means]
fills, borders = [pair.fill for pair in pairs], [pair.edge for pair in pairs]
hollow = {"s": 12, "facecolor": "white", "linewidths": 0.5, "zorder": 3}  # above the error bars
fig, (ax,) = mpp.grid_inches(width=1.5, height=1.5)
ax.bar(positions, means, 0.6, color=fills, edgecolor=borders, linewidth=1.0)  # edge width (L8)
ax.errorbar(positions, means, yerr=yerr, fmt="none", ecolor="black", elinewidth=0.8, capthick=0.8)
for position, values, pair in zip(positions, replicates, pairs):  # the replicates (E4)
    ax.scatter(np.full(values.size, position), values, edgecolor=pair.edge, **hollow)
ax.plot([0.0, 0.0, 1.0, 1.0], [2.4, 2.45, 2.45, 2.4], color="black", linewidth=0.8)
ax.text(0.5, 2.48, mpp.significance_stars(q), ha="center", va="bottom")
ax.set_xticks(positions, groups)
ax.xaxis.set_minor_locator(NullLocator())  # a categorical axis has no minor ticks (L2)
ax.set(ylim=(0.0, 3.0), ylabel="Activity (a.u.)")
mpp.assert_figure(fig)
plt.close(fig)

# Binning belongs to the analysis; the figure reads edges and counts (E7, X5).
edges = np.linspace(0.0, 6.0, 31)  # a 0.2 bin grid shared by both series
sample_a, sample_b = rng.normal(2.5, 0.6, 5000), rng.normal(3.5, 0.7, 4000)
(counts_a, _), (counts_b, _) = np.histogram(sample_a, edges), np.histogram(sample_b, edges)
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)
handles = [
    mpp.plot_distribution(ax, edges, counts_a, sample_a.size, fill=GRAY.fill, edge=GRAY.edge),
    mpp.plot_distribution(ax, edges, counts_b, sample_b.size, fill=GREEN.fill, edge=GREEN.edge),
]
ax.legend(handles, ["Reference", "Treated"])
ax.set(xlim=(0.0, 6.0), ylim=(0.0, 15.0), xlabel="Distance (\u00c5)", ylabel="Percent of samples")
mpp.assert_figure(fig)
plt.close(fig)
```

## Export

- **X1.** Every figure is saved with `save_figure` as PNG at 600 dpi, PDF and SVG, uncropped.
  The file has the figure's exact size whatever `savefig.bbox` a local matplotlibrc sets;
  `crop=True` trims to the drawn content and so breaks the inch layout.
- **X2.** The PDF keeps text editable (TrueType) for Illustrator and Inkscape. The SVG stores
  text as paths for PowerPoint and Keynote, which then show it as drawn on a machine without
  Arial; `editable_svg_text=True` keeps SVG text as text.
- **X3.** Output is deterministic: rerunning unchanged code reproduces the files byte for byte,
  so a file that changes under version control is a figure that changed.
- **X4.** A caption draft is saved beside the figure: `caption=` writes `<path>_caption.txt`.
- **X5.** Figure code reads precomputed results. It does not rerun an analysis.

```python
fig, (ax,) = mpp.grid_inches(width=2.5, height=1.5)
mpp.plot_mean_sem(ax, x, mean, sem, fill=GREEN.fill, edge=GREEN.edge)
ax.set(xlim=(0.0, 10.0), xlabel="Time (s)", ylabel="Signal (a.u.)")
mpp.assert_figure(fig)
caption = "Mean of n = 6 replicates; the band is 1 SEM either side, not a confidence interval."
paths = mpp.save_figure(fig, "figures/signal", caption=caption)  # creates figures/
assert [path.name for path in paths][-1] == "signal_caption.txt"  # after the PNG, PDF and SVG
```

## Checking a figure

`mpp.check_figure(fig)` returns an `Issue(rule, severity, message)` per problem among the drawn
artists, with the expected values read from the style file (`style=` names another style).
`mpp.assert_figure(fig)` raises `StyleError` listing the errors and emits a `StyleWarning` per
warning (`warnings_as_errors=True` fails on those too). Run one before every save, fix what it
reports, and pass `ignore`, `allow_font_sizes` or `allow_font_weights` (a bold callout that a
figure emphasizes on purpose) only with the reason in a comment.

| Rule id | Severity | Enforces |
| --- | --- | --- |
| `font-size` | error | T1 |
| `font-weight` | error | T1 |
| `font-family` | error | T1 |
| `font-fallback` | warning | T1 (Arial is not installed; reported once per figure) |
| `script-glyph` | error | T5 |
| `unicode-minus` | warning | T6 |
| `spine-width` | error | L1, L10 (a color bar outline) |
| `open-spines` | warning | L1 |
| `legend-frame` | error | L9 |
| `layout-engine` | error | S2 |
| `round-inches` | warning | S2, S3 (an exact derived size is a stated exception) |
| `off-canvas` | error | S5, X1 (an uncropped file cuts off what lies outside) |
| `text-overlap` | warning | S8 (texts at an angle other than a quarter turn are not compared) |
| `panel-letter` | warning | S6 |
| `default-color` | warning | C1 |

The other rules are judgment: what a color means, which interval a panel shows, whether a
legend covers data. Check those by reading the rule and looking at the saved PNG at print size.

```python
fig, (ax,) = mpp.grid_inches(width=2.0, height=1.5)
mpp.box_axes(ax)
ax.plot(x, np.cos(x), color=GREEN.edge, linewidth=1.2)
ax.set_xlim(0.0, 10.0)
# A boxed panel is a requested exception to L1, so its top and right spines are not an issue.
mpp.assert_figure(fig, ignore={"open-spines"})
assert {issue.rule for issue in mpp.check_figure(fig, ignore={"open-spines"})} <= {"font-fallback"}
plt.close(fig)
```

## A project palette

A project keeps its colors in one module (C1), with neutral role names and at most two
lightness levels per hue (C4):

```python
"""Colors for every figure of the project: one fill and edge pair per role."""

from mplplots import ColorPair

REFERENCE = ColorPair(fill="#cccccc", edge="#7a7a7a")
TREATED = ColorPair(fill="#c7e9c0", edge="#4f9d58")
TREATED_STRONG = ColorPair(fill="#41ab5d", edge="#006d2c")  # second level of the green hue
CONTROL = ColorPair(fill="#c6dbef", edge="#3182bd")
VARIANT = ColorPair(fill="#c7c5dc", edge="#634895")
# A warm hue below the 3:1 edge contrast, kept bright on purpose; every panel that shows it
# also gives it a marker, label or position cue (C6, C7).
LIGAND = ColorPair(fill="#fff0a6", edge="#e6b800")

PALETTE: dict[str, ColorPair] = {
    "reference": REFERENCE,
    "treated": TREATED,
    "treated_strong": TREATED_STRONG,
    "control": CONTROL,
    "variant": VARIANT,
    "ligand": LIGAND,
}
EDGE_FLOORS: dict[str, float] = {"ligand": 1.8}
```

Its test asserts that `check_palette` finds no violation: every edge is darker than its fill,
unique, and at or above its contrast floor (C2, C7). Here the last line runs it, not pytest.

```python
from mplplots import check_palette


def test_palette_is_sound() -> None:
    assert check_palette(PALETTE, floors=EDGE_FLOORS) == []


test_palette_is_sound()
```

## Checklist

- `mpp.use()` runs before the first figure; no `fontsize` or `fontweight` in figure code (T1).
- Greek letters in names and the angstrom sign are escaped upright characters; variables are math text (T3, T4).
- Exponents and subscripts are math text, and minus signs are ASCII hyphen-minus (T5, T6).
- Curves sharing a panel have explicit widths, bars explicit edges; proxies copy them (L4, L8).
- Reference lines use `REFERENCE_LINE`, and the reference series has the highest `zorder` (L5, L6).
- Colors come from the tested project palette; series on one axis differ without color (C1-C7).
- Figure size, axis lengths and margins are named inch constants on the grid (S1, S2).
- No panel letters, no `supxlabel`, and a shared y label from `add_shared_ylabel` (S6, S7).
- Intervals are 95% BCa over replicates, or a SEM band that the caption names (E1 to E3).
- Few replicates are shown individually; stars come from corrected values (E4, E5).
- Distributions use `plot_distribution`, and the caption gives the bin width and denominator (E7).
- `mpp.assert_figure(fig)` passes, and each `ignore` has a stated reason.
- Saved with `save_figure` and a caption; the PNG was looked at; a rerun changes no file (X1-X4).
