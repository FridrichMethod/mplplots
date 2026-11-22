# Changelog

All notable changes to mplplots are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- GraphPadPrism style: reproduces the default graphs of GraphPad Prism 11, with every value that
  comes from Prism measured from the SVG and PDF files that Prism 11 exports. Figures look
  different: text is Arial Bold, with 11 pt tick labels, 12 pt axis labels, figure-level labels
  and legend, and 14 pt axes and figure titles (the legend is bold, where Prism draws it
  regular); axis lines and ticks are 1.44 pt wide (Prism's "1 pt"), with outward ticks reaching
  5.4 pt beyond the axis line; minor ticks are off, and 2.7 pt long when turned on; data lines,
  error bars, and caps are 0.72 pt (Prism's "1/2 pt"), data lines have round ends, and caps are
  6.48 pt long; symbols are 5.76 pt across; bars given an edge color get a 2.16 pt border; tick
  labels, axis labels, the title, and legend rows sit at Prism's distances. `docs/styles.md`
  lists where the style departs from Prism, such as Prism's legend outside the plot on the right.
- Personal style: minor ticks split each major interval in two (`xtick.minor.ndivs` and
  `ytick.minor.ndivs` 2), one minor tick between major ticks instead of Matplotlib's three or
  four. `auto_ticks` sets its own minor ticks on linear numeric axes as before. Other axes in the
  Personal style look different, including axes that do not use `auto_ticks` and date or other
  unit axes.
- `check_figure` and `assert_figure` read every text size and weight from the style file: the
  `font-size` rule accepts each size the style sets for a kind of text (`font.size`,
  `axes.labelsize`, `axes.titlesize`, the tick label, legend, and figure text sizes), and
  `font-weight` each weight it sets, in place of `font.size` and regular alone. A figure in the
  GraphPadPrism style passes with the style's 11, 12, and 14 pt bold text. The Personal style
  checks as before.
- The `graphpadprism_*` gallery images use Prism's 3 by 2 in plot area (2 by 2 in for the bar
  chart) and black bar borders, and pass `assert_figure` against the style; the ocean, grouped
  bar, and error bar images place their legend beside the plot, close to where Prism puts it.
- Style guide: rule L2 asks for `auto_ticks` on each panel after plotting, with limits that leave
  five or more major intervals, so one minor tick falls between major ticks; a panel with an axis
  shorter than about 1 in, and a color bar, keep Matplotlib's ticks. Rule L10 gives a color bar's
  major ticks the 2.5 pt length and leaves its minor ticks as the style draws them. Step 4 of the
  skill's workflow and of the rules snippet calls `auto_ticks`, and so do the examples of the
  style guide and the skill.
- Style guide: rule E3 asks for the t interval, mean +/- t(0.975, n - 1) SEM, for every mean, in
  place of a BCa bootstrap interval, which covers only about 85% at n = 5 or 6 and is no better
  than the t interval at larger n, even for skewed data. A BCa interval with at least 10,000
  resamples serves a statistic other than the mean, such as a median or a ratio, from 20
  replicates on; below that, such a statistic is shown by its individual values. The
  `personal_bars` gallery image draws t intervals, and its captions name them.
- The Personal gallery images and the palette figures with numeric axes set their ticks with
  `auto_ticks`, with limits that leave five or more major intervals.
- The README is a short introduction; the reference documentation (styles, ticks, layout, colors,
  plot helpers, saving, checking, coding agents, gallery, development) lives in `docs/`.

### Fixed

- `mpp.use`, `mpp.context`, and `prism_style` first return every setting that any packaged style
  sets to Matplotlib's default, then apply the style. Switching from one packaged style to another
  in a session kept the settings that only the earlier style sets, such as the Personal style's
  black markers and hyphen-minus in a GraphPadPrism figure.

## [0.4.0] - 2026-11-21

The style checker reports overlapping texts, accepts text that a figure emphasizes on purpose, and
checks the outline of a color bar; the style guide gains rules for color bars, dense marks, and
overlapping text. Figures look the same as in 0.3.0, but `check_figure` now reports a color bar
with Matplotlib's default 0.8 pt outline and texts that overlap.

### Added

- `check_figure` and `assert_figure` take `allow_font_weights`: the font weights accepted besides
  regular, as names or numbers, for text that a figure emphasizes on purpose.
- The `text-overlap` rule, a warning: texts whose drawn boxes overlap each other, such as crowded
  tick labels or an annotation over a legend entry. An annotation counts by its text without its
  arrow, and a text at an angle other than a multiple of 90 degrees is not compared.
- Style guide rules for color bars (L10: their own axes passed as `cax`, a 0.6 pt outline, 2.5 pt
  ticks), for artists with thousands of marks (L11: rasterized, never thinned), and against
  overlapping text (S8).

### Changed

- `spine-width` checks the outline of a color bar against the style's minor tick width, 0.6 pt in
  the Personal style, in place of the axis line width: a 0.6 pt outline passes, and Matplotlib's
  default 0.8 pt outline is reported.

## [0.3.0] - 2026-11-21

Adds the Personal style as the default of `mplplots.use()`, a figure toolkit (layout in inches,
color pairs, saving, plot helpers, and a style checker), and an agent skill with its style guide.
Figures made with the GraphPadPrism style look the same as in 0.2.0.

### Added

- The Personal style, `mplplots.styles.Personal`, the default of `mplplots.use()`: Arial Regular
  8 pt for every text element, 0.8 pt axis lines and ticks with minor ticks, no top or right
  spines, ASCII hyphen-minus in tick labels, and files saved uncropped at 600 dpi.
- A style registry in `mplplots.styles`: `DEFAULT_STYLE`, `STYLES`, `style_path`, `use`, and
  `context` apply any packaged style by name. `mplplots.__version__` gives the installed version.
- `mplplots.colors`: `ColorPair` (a role's fill and edge colors), `lighten`, `darken`,
  `relative_luminance`, `contrast_ratio`, `check_palette` (edges darker than fills, unique, and
  above a contrast floor), and the constants `SCATTER_ALPHA`, `BAND_ALPHA`, `LINE_ALPHA`,
  `REFERENCE_LINE`, and `SECONDARY_LINESTYLE`.
- `mplplots.layout`: `grid_inches` lays out a grid of axes from axis lengths, margins, and gaps
  in inches; `figure_size` and `COLUMN_WIDTHS` give journal column widths; `add_shared_ylabel`
  and `align_legends_left` finish multi-panel figures. It also exports the inch helpers of
  `mplplots.utils`.
- `mplplots.export.save_figure` writes PNG, PDF, and SVG at the figure's exact size, byte for
  byte reproducibly, with an optional caption file.
- `mplplots.plots`: `plot_mean_sem`, `plot_distribution`, `significance_stars`, and `box_axes`.
- `mplplots.check`: `check_figure` reports the ways a figure departs from a style as `Issue`s,
  under 14 rules (`RULES`) whose expected values come from the style file; `assert_figure`
  raises `StyleError` on errors and emits a `StyleWarning` per warning.
- The `mplplots` command (also `python -m mplplots`): `styles`, `rules`, `guide`, and
  `install-skill`, which copies the packaged agent skill and its style guide into a project for
  Claude Code and Codex, with `--rules` for the rules snippet and `--check` for stale copies.
- Every public name of the styles and the toolkit is importable from the top-level package
  (`import mplplots as mpp`).
- A Personal gallery: `examples/personal_demo.py` and its five figures in the README.

### Changed

- The README palette images use the Personal style, and the comparison at the top of the README
  shows the Personal style beside Matplotlib's defaults.
- The README describes GraphPadPrism as a style inspired by GraphPad Prism whose values are
  chosen by eye, not measured from Prism's defaults.

## [0.2.0] - 2026-11-16

First tagged release. Figures made with the GraphPadPrism style look different from 0.1.0:
smaller regular text, thinner lines, and saved files that are neither resized nor cropped.

### Changed

- GraphPadPrism style: every text element is Arial Regular 8 pt, including figure titles,
  figure-level labels, and legend titles. It was bold, with a 14 pt base, 12 pt axis labels,
  16 pt titles, 10 pt tick labels, and an 8 pt legend. (#7)
- GraphPadPrism style: saved files are 600 dpi (`savefig.dpi`); the screen stays at 300 dpi. (#7)
- GraphPadPrism style: no figure size is set (it was 4.5 by 3 in). (#7)
- GraphPadPrism style: saved figures are not cropped (`savefig.bbox: tight` removed), so a file
  has exactly the figure's size. Pass `bbox_inches="tight"` to `savefig` to crop. (#9)
- GraphPadPrism style: PDF and PostScript embed fonts as TrueType (Type 42) instead of Type 3,
  so text stays editable; SVG stores glyphs as paths. (#7)
- GraphPadPrism style: axis lines, ticks, and data lines (including error bars) are 1 pt wide.
  Axis lines and ticks were 1.5 pt and data lines 2 pt. (#11)
- README example images use the GraphPadPrism style and Arial throughout, are laid out in round
  inches, and are saved as PNG, SVG, and PDF. Variables in their labels are math text. (#5, #8, #12)

### Added

- `mplplots.utils.add_axes_inches`, `legend_inches`, and `suptitle_inches` place axes (their
  position and axis lengths), legends, and figure titles in inches, as GraphPad Prism sets axis
  lengths. They keep their place when the figure is resized and at any dpi. `LegendCorner` is
  the type of the legend anchor `loc`. (#10)

### Fixed

- `auto_ticks` prefers the smaller tick spacing when two spacings give the same number of
  intervals, so an unset limit moves out only to the nearest major tick. Data from 0 to 2 pi with
  `left=0` now ends at 8 instead of 10. (#6)

## [0.1.0]

Untagged initial version: the GraphPadPrism style (`STYLE_PATH`, `prism_style`), the palettes
in `mplplots.palettes` (`PALETTES`, `set_palette`, `get_colors`), `auto_ticks`, and
`add_custom_fonts`.

[Unreleased]: https://github.com/FridrichMethod/mplplots/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/FridrichMethod/mplplots/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/FridrichMethod/mplplots/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/FridrichMethod/mplplots/releases/tag/v0.2.0
