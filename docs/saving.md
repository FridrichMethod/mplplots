# Saving figures

`mplplots.export.save_figure` saves a figure the way the
[style guide](../src/mplplots/data/skills/mplplots/references/style-guide.md) asks:

```python
import mplplots as mpp

mpp.use()
fig, (ax,) = mpp.grid_inches(width=2.0, height=1.5)
ax.plot([0, 1, 2], [0, 1, 4], color="#4f9d58", linewidth=1.2)
paths = mpp.save_figure(fig, "figures/fig01", caption="Signal after the pulse.")
# figures/fig01.png, figures/fig01.pdf, figures/fig01.svg, figures/fig01_caption.txt
```

- `path` is the output path without an extension; each format's extension is appended, and
  missing directories are created. `formats` defaults to `("png", "pdf", "svg")` (`mpp.FORMATS`).
- The files have the figure's exact size, whatever `savefig.bbox` your `matplotlibrc` sets.
  `crop=True` trims them to the drawn content with a 0.02 in margin instead.
- Raster files use `rcParams["savefig.dpi"]` (600 under both styles) unless you pass `dpi`.
- Output is reproducible: the PDF and SVG carry no date, so saving the same figure again writes the
  same bytes, and a file that changes under version control is a figure that changed. The raster
  formats (PNG, TIFF, JPEG, WebP, ...) and PGF are reproducible too; SVGZ, PS and EPS, which
  `formats` also accepts, record the time of the save.
- SVG stores text as paths, so it looks the same on a machine without Arial;
  `editable_svg_text=True` keeps it as text. Under both styles (`pdf.fonttype: 42`), the PDF keeps
  text editable as TrueType; `save_figure` does not set the PDF font type itself.
- A `caption` that is not blank is written, stripped and newline-terminated, to
  `<path>_caption.txt`. The figure is closed afterward unless
  `close=False`. It returns the written paths, in the order of `formats`, then the caption file.
