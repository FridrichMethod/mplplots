## Figures

Figures use the Personal style of mplplots. Use the `mplplots` skill to create, restyle or
review a figure, and follow these steps:

1. `import mplplots as mpp` and `mpp.use()` before the first figure is created.
2. Take colours from the project's palette module of `ColorPair` roles; if there is none, create
   it with a `check_palette` test.
3. Lay the figure out in round inches with `mpp.grid_inches` or `mpp.add_axes_inches`.
4. Draw with the style's text and marks: no `fontsize` or `fontweight`, variables as math text.
5. Run `mpp.assert_figure(fig)` and fix what it reports; pass `ignore` only with a stated reason.
6. Save with `mpp.save_figure(fig, path, caption=...)`, then look at the PNG.

The full rules are in the skill's `references/style-guide.md`, also printed by `mplplots guide`.
