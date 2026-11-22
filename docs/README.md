# mplplots documentation

The reference documentation of mplplots: its Matplotlib styles, the toolkit for publication
figures, and the agent skill. The [README](../README.md) introduces the package; each page here
stands on its own.

- [Styles](styles.md): the packaged styles, how to apply and combine them, every setting each
  style changes, where the GraphPadPrism style departs from Prism, and fonts.
- [Ticks](ticks.md): the default minor ticks of each style, and `auto_ticks`, which gives both
  axes of a plot Prism-like ticks and ends each axis on a major tick.
- [Layout in inches](layout.md): axes, legends, and figure titles placed in inches, grids of
  panels built from axis lengths, journal figure sizes, shared labels, margins, and colorbars.
- [Colors](colors.md): the 25 palettes, the colormap families, color cycles and `get_colors`, and
  the color pairs, contrast checks, and alpha and line constants of the Personal style.
- [Plot helpers](plots.md): mean +/- SEM bands, binned distributions, significance stars, and
  boxed axes.
- [Saving figures](saving.md): `save_figure`, which writes PNG, PDF, and SVG at the figure's exact
  size, byte for byte reproducibly, with a caption draft.
- [Checking a figure](checking.md): `check_figure` and `assert_figure`, which test a figure
  against its style, the text sizes and weights a style accepts, and the rules they check.
- [For coding agents](coding-agents.md): the agent skill, the rules snippet for a project's
  `AGENTS.md`, the style guide, `mplplots install-skill`, and the `mplplots` command.
- [Gallery](gallery.md): every example figure with its caption, how to regenerate the images, and
  the conventions they follow.
- [Development](development.md): setting up a clone, the checks to run before committing, and CI.

Installation and a quick start are in the [README](../README.md#installation).
