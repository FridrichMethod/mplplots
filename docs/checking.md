# Checking a figure

`mplplots.check` turns the mechanical rules of the
[style guide](../src/mplplots/data/skills/mplplots/references/style-guide.md) into code.
`check_figure(fig)` returns a list of `Issue(rule, severity, message)`, reading the expected values
(text sizes and weights, font list, spine width, hidden spines, legend frame, minus sign) from the
style file, so it follows the style instead of restating it. `assert_figure(fig)` raises
`StyleError` listing every error and emits one `StyleWarning` per warning;
`warnings_as_errors=True` fails on warnings too.

```python
import numpy as np

import mplplots as mpp

mpp.use()
fig, (ax,) = mpp.grid_inches(width=2.0, height=1.5)
mpp.box_axes(ax)
ax.plot(np.arange(10), np.arange(10) ** 0.5, color="#4f9d58", linewidth=1.2)
ax.set_xlim(0, 9)

for issue in mpp.check_figure(fig):
    print(issue.rule, issue.severity, issue.message)
# A boxed panel is a requested exception, so its top and right spines are not an issue.
mpp.assert_figure(fig, ignore={"open-spines"})
```

Both take `style=` to check against another packaged style (`"Personal"` by default), `ignore=`
to skip rule ids, `allow_font_sizes=` for sizes accepted besides the style's text sizes, and
`allow_font_weights=` for weights accepted besides the style's weights, such as a bold callout in
the Personal style. Pass any of the three only with the reason in a comment. They inspect only
drawn artists and handle polar and 3D axes, colorbars, twin axes, and log scales.
`mplplots.RULES` maps each rule id to a one-line description.

## Text sizes and weights

The style's text sizes are the sizes it sets for each kind of text: `font.size`,
`axes.labelsize`, `axes.titlesize`, `xtick.labelsize`, `ytick.labelsize`, `legend.fontsize`,
`legend.title_fontsize`, `figure.titlesize`, and `figure.labelsize`, with a relative size such as
`"large"` taken against `font.size`. Its weights are those of `font.weight`, `axes.labelweight`,
`axes.titleweight`, `figure.titleweight`, and `figure.labelweight`. A key that the style leaves
out counts with Matplotlib's default, which is what text gets when the style is applied over
Matplotlib's defaults. So the Personal style accepts 8 pt regular text only, and the
GraphPadPrism style bold text at 11, 12, or 14 pt.

## Rules

| Rule id | Severity | Reports |
| --- | --- | --- |
| `font-size` | error | Text whose size is neither one of the style's text sizes nor in `allow_font_sizes` |
| `font-weight` | error | Text whose weight is neither one of the style's weights nor in `allow_font_weights` |
| `font-family` | error | Text that resolves to a font outside the style's `font.sans-serif` list |
| `font-fallback` | warning | The style's first-choice font is not installed, so text renders in a fallback (once per figure) |
| `script-glyph` | error | Text with a precomposed superscript or subscript character, such as U+00B2; write `$^2$` |
| `unicode-minus` | warning | Text with the Unicode minus sign (U+2212) when the style uses the ASCII hyphen-minus |
| `spine-width` | error | A visible spine whose width differs from the style's `axes.linewidth`, or a colorbar outline whose width differs from the minor tick width |
| `open-spines` | warning | A visible top or right spine where the style hides it |
| `legend-frame` | error | A legend with a frame when the style has none |
| `layout-engine` | error | A figure with a layout engine (tight or constrained) |
| `round-inches` | warning | A figure size, or an axes position or size, off the 0.05 in grid |
| `off-canvas` | error | Text or a legend that extends beyond the canvas, which an uncropped file cuts off |
| `text-overlap` | warning | Texts whose drawn boxes overlap each other; a text at an angle other than a multiple of 90 degrees is not compared |
| `panel-letter` | warning | Text other than a tick label that is a single letter, such as `a`, `B`, or `(c)` |
| `default-color` | warning | A line, patch, or collection in one of Matplotlib's ten default-cycle colors |

The other rules of the style guide are judgment, such as what a color means or whether a legend
covers data. Check those by looking at the saved PNG at print size.
