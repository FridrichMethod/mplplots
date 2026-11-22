# Styles

mplplots packages its styles as ordinary, self-contained Matplotlib style files. This page lists
them, shows how to apply and combine them, and lists what each one changes from Matplotlib's
defaults.

## Packaged styles

| Style | Dotted name | What it is |
| --- | --- | --- |
| `Personal` | `mplplots.styles.Personal` | The default. Arial Regular 8 pt throughout, 0.8 pt axis lines and ticks with one minor tick halfway between major ticks, and no top or right spines. See [What the Personal style changes](#what-the-personal-style-changes). |
| `GraphPadPrism` | `mplplots.styles.GraphPadPrism` | The default graphs of GraphPad Prism 11, measured from the files Prism exports: Arial Bold text (11 pt tick labels, 12 pt axis labels and legend, 14 pt titles), 1.44 pt axis lines and outward ticks, 0.72 pt data lines and error bars, and no minor ticks. See [What the GraphPadPrism style changes](#what-the-graphpadprism-style-changes). |

`mplplots styles` prints the same list with the path of each style file. In Python,
`mplplots.STYLES` holds the names, `mplplots.DEFAULT_STYLE` is `"Personal"`, and
`mplplots.style_path(name)` returns a style's file.

## Applying a style

```python
import matplotlib.pyplot as plt

import mplplots as mpp

mpp.use()  # the Personal style, for the rest of the session
mpp.use("GraphPadPrism")  # another packaged style, by name

with mpp.context("GraphPadPrism"):  # a style for one block only
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
```

`mpp.use` and `mpp.context` raise `ValueError` for a name that is not in `mplplots.STYLES`. Both
first return every setting that any packaged style sets to Matplotlib's default, so switching from
one packaged style to another in a session gives the same settings as applying the second one
alone. Apply a style before you create the figure: Matplotlib reads the settings when it creates
an artist, so a figure made earlier keeps the old look.

`mplplots.STYLE_PATH` is the path of `GraphPadPrism.mplstyle`, and `mplplots.prism_style()` applies
it, as `mpp.use("GraphPadPrism")` does.

### Loading a style by its dotted name

Matplotlib also loads each style by its dotted package name, so a script can use one without
importing mplplots:

```python
import matplotlib.pyplot as plt

plt.style.use("mplplots.styles.Personal")  # for the rest of the session

with plt.style.context("mplplots.styles.GraphPadPrism"):  # for one block only
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
```

`plt.style.use` applies only the settings in the file, so a setting that only an earlier style
sets stays in effect. To switch between packaged styles this way, start from Matplotlib's
defaults: `plt.style.use(["default", "mplplots.styles.Personal"])`.

### Combining styles

Styles can be combined. Later entries override earlier ones, so put an mplplots style last to keep
its fonts, spines, and sizes on top of another style (here, seaborn's white grid):

```python
import matplotlib.pyplot as plt

plt.style.use(["seaborn-v0_8-whitegrid", "mplplots.styles.Personal"])
```

Seaborn plots draw under the style without any seaborn setup. If you call `sns.set_theme(...)`,
apply the style after it, because `set_theme` rewrites the same settings:

```python
import seaborn as sns

import mplplots as mpp

sns.set_theme(style="ticks")
mpp.use()
```

### Without installing mplplots

Each style is an ordinary, self-contained Matplotlib style file in
[`src/mplplots/styles/`](../src/mplplots/styles/). You can copy
[`Personal.mplstyle`](../src/mplplots/styles/Personal.mplstyle) anywhere and load it with
`plt.style.use("path/to/Personal.mplstyle")`. You can also put it in the `stylelib/` folder of your
Matplotlib config directory (`matplotlib.get_configdir()`) and use `plt.style.use("Personal")` from
any project.

## What the Personal style changes

| Area | Settings |
| --- | --- |
| Figure | No figure size is set. Saved at 600 dpi and shown on screen at 150 dpi. Saved files are not cropped, so they keep the figure's size; pass `bbox_inches="tight"` to `savefig` to crop to the drawn content. |
| Text | Arial Regular 8 pt (see [Fonts](#fonts)) for every text element: tick labels, axis labels, axes and figure titles, figure-level labels, and the legend and its title. Math text (`$...$`) uses the same font: variables such as `$x$` in Arial Italic, and function names such as `$\sin$`, numbers, and operators upright. Negative tick labels use the ASCII hyphen-minus. Axis labels sit 3 pt from the tick labels. |
| Vector output | PDF and PostScript embed fonts as TrueType (Type 42), so text stays editable and passes journal checks that reject Type 3 fonts. SVG stores glyphs as paths. |
| Axes | 0.8 pt axis lines, with the top and right spines removed. Autoscaled limits are rounded out to tick values. |
| Ticks | Major ticks 0.8 pt wide and 3.5 pt long, minor ticks 0.6 pt wide and 2 pt long, shown on both axes, one halfway between each pair of major ticks (see [Minor ticks of the styles](ticks.md#minor-ticks-of-the-styles)). |
| Lines & markers | 2 pt lines; give each curve its own width when several share a panel. 3 pt markers (`lines.markersize`; drawn 4 pt across with Matplotlib's 1 pt marker edge), black unless the call sets their colors. 0.5 pt patch edges. Error-bar caps are 6 pt long (`errorbar.capsize: 3`; a Matplotlib cap is twice `capsize` long). |
| Legend | No frame, placed in the upper right, with short handles (1.2 font sizes) and tight spacing. |

For every setting, see the [style file](../src/mplplots/styles/Personal.mplstyle).

## What the GraphPadPrism style changes

The style reproduces the default graphs of GraphPad Prism 11. Every value that comes from Prism
is measured from the SVG and PDF files that Prism 11 exports for its default XY, column, and
grouped graphs, at Prism's nominal size. Prism gives line thickness in its own points: its "1 pt"
renders 1.44 PostScript points wide (1/50 in) and its "1/2 pt" 0.72 pt. The style sets the
rendered widths, so a saved file looks like Prism's. Lengths and sizes below are in points.

| Setting | Value | What it reproduces |
| --- | --- | --- |
| `font.family`, `font.sans-serif` | `sans-serif`; Arial, Helvetica, Liberation Sans, Arimo, Nimbus Sans, DejaVu Sans, sans-serif | Prism's Arial, with fallbacks that resolve without warnings (see [Fonts](#fonts)) |
| `font.cursive` | Matplotlib's default cursive fonts, then DejaVu Sans and `cursive` | Not from Prism: `\mathcal` finds a font on every machine, without a missing-font warning (but see the weight notices below) |
| `font.size`, `font.weight` | 12, bold | Prism's bold Arial. Matplotlib has no weight setting for tick labels or legend text, so the base weight is bold |
| `xtick.labelsize`, `ytick.labelsize` | 11, 11 | Numbering: Arial Bold 11 pt |
| `axes.labelsize`, `axes.labelweight` | 12, bold | Axis titles: Arial Bold 12 pt |
| `figure.labelsize`, `figure.labelweight` | 12, bold | Figure-level axis labels (`supxlabel`, `supylabel`) like the axis titles |
| `axes.titlesize`, `axes.titleweight` | 14, bold | Graph title: Arial Bold 14 pt |
| `figure.titlesize`, `figure.titleweight` | 14, bold | Figure titles (`suptitle`) like the graph title |
| `legend.fontsize`, `legend.title_fontsize` | 12, 12 | Legend: Arial 12 pt, in bold where Prism uses regular |
| `mathtext.fontset`, `mathtext.rm`, `mathtext.sf`, `mathtext.it`, `mathtext.bf`, `mathtext.bfit` | `custom`, `sans:bold`, `sans:bold`, `sans:italic:bold`, `sans:bold`, `sans:italic:bold` | Math text in the bold text font: variables such as `$x$` in Arial Bold Italic, and function names such as `$\sin$`, numbers, and operators in Arial Bold. Each pattern names its weight, because Matplotlib before 3.11 caches a font lookup by its pattern alone and would otherwise keep the weight of the style that first rendered math in the session |
| `mathtext.cal`, `mathtext.tt` | `cursive:bold`, `monospace:bold` | Not from Prism: `\mathcal` and `\mathtt` in bold, like the rest of the math |
| `axes.linewidth` | 1.44 | Thickness of axes "Auto (1 pt)" |
| `axes.spines.top`, `axes.spines.right` | False, False | Frame style "No frame" |
| `xtick.direction`, `ytick.direction` | out, out | Outward ticks: the X axis ticks direction "Down" |
| `xtick.major.size`, `ytick.major.size` | 6.12, 6.12 | Ticks length "Normal": 5.4 pt beyond the axis line, since a Matplotlib tick starts at the axis centerline, 0.72 pt inside the line |
| `xtick.major.width`, `ytick.major.width` | 1.44, 1.44 | Ticks as thick as the axes |
| `xtick.minor.visible`, `ytick.minor.visible` | False, False | Minor ticks "Auto (0)": none |
| `xtick.minor.size`, `ytick.minor.size` | 3.42, 3.42 | Prism's minor ticks, for a figure that turns them on: 2.7 pt beyond the axis line |
| `xtick.minor.width`, `ytick.minor.width` | 1.44, 1.44 | Minor ticks as thick as the axes |
| `xtick.major.pad`, `ytick.major.pad` | 4.15, 2.15 | X tick labels with their baseline 18.28 pt below the axis centerline; Y tick labels ending 8.28 pt left of it |
| `xtick.minor.pad`, `ytick.minor.pad` | 6.85, 4.85 | Minor tick labels (log axes) in line with the major ones; Prism labels no minor ticks |
| `axes.labelpad` | 6.15 | X axis title with its baseline 35.48 pt below the axis centerline |
| `axes.titlepad` | 12.15 | Graph title with its baseline 12.15 pt above the plot area |
| `axes.autolimit_mode` | `round_numbers` | Not measured: autoscaled limits are rounded out to tick values |
| `lines.linewidth` | 0.72 | Connecting lines and error bars "Auto (1/2 pt)" |
| `lines.solid_capstyle` | round | Round ends of connecting lines |
| `lines.markersize`, `lines.markeredgewidth` | 5.04, 0.72 | Symbol size "Auto (4)": filled symbols 5.76 pt across, as a marker's edge is centered on its outline. Matplotlib draws error-bar caps with `lines.markeredgewidth`, so they are 0.72 pt thick, as in Prism |
| `errorbar.capsize` | 3.24 | Caps 6.48 pt long, as on Prism's XY graphs; a Matplotlib cap is twice `capsize` long |
| `patch.linewidth` | 2.16 | Bar borders, on bars given an edge color, such as `bar(..., edgecolor="black")` |
| `legend.frameon` | False | No legend frame |
| `legend.handlelength`, `legend.handletextpad` | 1.28, 0.72 | Legend lines and swatches 15.36 pt long and 8.64 pt from their text |
| `legend.labelspacing` | 0.742 | Legend rows 20.16 pt apart |
| `legend.handleheight` | 0.68 | Legend bar swatches 8.24 pt tall |
| `legend.loc` | upper right | Not from Prism, whose legend sits outside the plot on the right (see below) |
| `figure.dpi`, `savefig.dpi` | 300, 600 | Not from Prism: shown on screen at 300 dpi and saved at 600 dpi |
| `figure.frameon` | False | Not from Prism: no figure frame |
| `pdf.fonttype`, `ps.fonttype`, `svg.fonttype` | 42, 42, path | Not from Prism: PDF and PostScript embed fonts as TrueType (Type 42), so text stays editable and passes journal checks that reject Type 3 fonts; SVG stores glyphs as paths |

No figure size is set, and saved files are not cropped, so they keep the figure's size; pass
`bbox_inches="tight"` to `savefig` to crop to the drawn content. For every setting, see the
[style file](../src/mplplots/styles/GraphPadPrism.mplstyle).

### Where the style departs from Prism

- **Legend weight.** The legend is Arial Bold, where Prism uses Arial Regular, so its labels are
  slightly wider. The math fonts are bold, so math is bold even in a text set to
  `fontweight="normal"`, and `$\mathbf{...}$` looks like `$\mathrm{...}$`.
- **Legend placement.** Prism puts the legend outside the plot on the right, top-aligned: its
  legend keys (line handles and bar swatches) start about 0.46 in right of the plot, its symbols
  about 0.52 in. `mpp.legend_inches` with `loc="upper left"`, 0.4 in right of the plot area's top
  right corner, places it within about 0.7 pt of Prism's; the ocean, grouped bar, and error bar
  images of the [gallery](gallery.md#graphpadprism-style) do.
- **Legend handles.** One setting sets both the swatch height and the handle's height above the
  text, so line and symbol handles sit 0.16 pt higher than Prism's.
- **Hollow symbols.** Prism draws their border 1.44 pt wide. `lines.markeredgewidth` stays 0.72
  because Matplotlib draws error-bar caps with it; pass `markeredgewidth=1.44` for hollow symbols.
  On Matplotlib 3.11 and later, `errorbar.capthick` sets the caps apart:
  `plt.rc_context({"errorbar.capthick": 0.72, "lines.markeredgewidth": 1.44, "lines.markersize": 4.32})`
  gives hollow symbols Prism's 1.44 pt border and keeps 0.72 pt caps and 5.76 pt filled symbols.
  The style leaves that key out, because Matplotlib 3.8 to 3.10 log it as a bad key.
- **Bars.** Prism draws its border inside the bar and leaves the base open; Matplotlib centers the
  edge on the bar's outline, so an outlined bar reaches 1.08 pt past its width on each side and
  above its value, about 2 pt wider than Prism's. Prism makes bar-graph caps half the bar width:
  pass `capsize` there.
- **Column scatter.** Prism's column scatter uses 4.32 pt circles; the style draws every symbol
  5.76 pt across.
- **Scatter markers.** `patch.linewidth` is also the edge width of `scatter` markers, which
  makes filled markers 7.2 pt across; pass `linewidths=0.72` for Prism's 5.76 pt. The 2.16 pt
  width also applies to any other patch given an edge: step histograms, arrows, text boxes.
- **Letter spacing.** Prism sets its 12 and 14 pt text about 0.2 pt tighter per letter, so a
  long title comes out about 3% wider than Prism's. Tick labels match.
- **Axis ends.** Matplotlib's axis lines have projecting ends, so a category axis without a tick
  at its end reaches 0.72 pt past it.
- **Error-bar ends.** Prism rounds the ends of its error bars and caps. `lines.solid_capstyle`
  reaches only data lines, so Matplotlib's error bars and caps have flat ends: the caps are as
  long as Prism's, but an error bar without caps (`capsize=0`) ends 0.36 pt short at each end.
- **Font notices with math.** With bold math, Matplotlib looks up its bundled math fonts
  (Computer Modern, STIX) and the `\mathcal` font in bold. They come in one weight, so the
  first math text in a session logs about ten `findfont: Failed to find font weight bold for ...`
  warnings. They do not change the output.
  `logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)` silences them, along with
  Matplotlib's other font warnings.
- **Rotated category labels** and Prism's upward-only error bars on column bar graphs are set in
  the plotting call (`rotation=45`, and `yerr=[np.zeros_like(sd), sd]` for lower errors of 0).
- **Matplotlib version.** The values are calibrated on Matplotlib 3.11.2. On 3.8, widths and
  lengths are the same, but tick labels and axis labels sit up to about 0.4 pt elsewhere, and
  legend rows are 0.3 pt closer per row, so the sixth row of a legend sits about 1.5 pt higher.

## Fonts

Both styles ask for Arial. If Arial is not installed (common on Linux and HPC clusters), they fall
back without warnings to Helvetica or an Arial-compatible clone (Liberation Sans, Arimo, Nimbus
Sans), and finally to DejaVu Sans, which ships with Matplotlib. Math text follows the same chain.
In the GraphPadPrism style, the first math text also logs weight notices for Matplotlib's bundled
math fonts, which do not change the output (see
[Where the style departs from Prism](#where-the-style-departs-from-prism)).
On macOS, whose Apple Chancery font (the first `font.cursive` font, used for `\mathcal`) records
its weight as 0, the first math text in the Personal style, such as a log-axis tick label, logs one
`findfont: Failed to find font weight normal for Apple Chancery` notice, which does not change the
output. The styles also set `font.family` to `sans-serif`, so they use this list even if your
`matplotlibrc` picks another font family. For final figures, install Arial, or register the font
files at the start of your script or notebook, before plotting:

```python
from mplplots import add_custom_fonts

add_custom_fonts(
    "/path/to/Arial.ttf",
    "/path/to/Arial Italic.ttf",
    "/path/to/Arial Bold.ttf",
    "/path/to/Arial Bold Italic.ttf",
)
```

`add_custom_fonts` registers the files for the current Python session only. The Personal style
uses the regular face for text and the italic face for variables in math text, and the bold face
for bold text you add, such as `fontweight="bold"` or `$\mathbf{...}$`. The GraphPadPrism style
uses the bold face for text and the bold italic face for variables. Matplotlib caches its
font list. If you install Arial system-wide after Matplotlib has already run, delete the
`fontlist-*.json` file in `matplotlib.get_cachedir()` so the list is rebuilt. Without Arial,
[`check_figure`](checking.md) reports one `font-fallback` warning per figure.

### Math text

Write variables and formulas in labels, titles, and legends as math text, so they are set in
italic like an equation: `ax.set_xlabel("$x$")` and `label=r"$\sin(x)$"`, not `"x"` and `"sin(x)"`.
Math text uses Matplotlib's built-in TeX parser, so it needs no LaTeX installation.
