# Changelog

All notable changes to mplplots are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/FridrichMethod/mplplots/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/FridrichMethod/mplplots/releases/tag/v0.2.0
