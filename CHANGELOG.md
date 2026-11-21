# Changelog

All notable changes to mplplots are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- GraphPadPrism style: no figure size is set (it was 4.5 × 3 in). (#7)
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
  intervals, so an unset limit moves out only to the nearest major tick. Data from 0 to 2π with
  `left=0` now ends at 8 instead of 10. (#6)

## [0.1.0]

Untagged initial version: the GraphPadPrism style (`STYLE_PATH`, `prism_style`), the palettes
in `mplplots.palettes` (`PALETTES`, `set_palette`, `get_colors`), `auto_ticks`, and
`add_custom_fonts`.

[Unreleased]: https://github.com/FridrichMethod/mplplots/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/FridrichMethod/mplplots/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/FridrichMethod/mplplots/releases/tag/v0.2.0
