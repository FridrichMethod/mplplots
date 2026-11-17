# mplplots

Visual styling helpers for Matplotlib/Seaborn.

## Environment

- Python >=3.12, use the `.venv` virtual environment: `source .venv/bin/activate`
- Install: `pip install -e ".[dev]"`

## Commands

- **Test**: `pytest` (runs from `tests/`, verbose+stdout by default)
- **Single test**: `pytest tests/test_utils.py::TestAutoTicks::test_sets_ticks_on_simple_plot`
- **Lint**: `ruff check src/ tests/`
- **Format**: `ruff format src/ tests/`
- **Type check**: `mypy src/`
- **Pre-commit**: `pre-commit run --all-files`

## Before Committing

Always run these before `git commit` and `git push`:

1. `pre-commit run --all-files` — must pass with no errors
2. `pytest` — all tests must pass

Do not commit or push if either fails. Fix issues first.

## Code Style

- Ruff for linting and formatting (line length 100, Google-style docstrings)
- Mypy for type checking (strict-ish, see pyproject.toml)
- `src/` layout with `mplplots` package
- Tests in `tests/` using pytest (no docstrings required in tests)
- Type annotations on all public functions

## GraphPadPrism Style

- `src/mplplots/styles/GraphPadPrism.mplstyle` sets every text element to Arial Regular 8 pt:
  tick labels, axis labels, axes and figure titles, figure-level axis labels, and the legend and
  its title. Do not give any of them another size or weight.
- Axis lines and major and minor ticks are 1 pt wide.
- It saves at 600 dpi (`savefig.dpi`), embeds TrueType fonts in PDF and PostScript
  (`pdf.fonttype` and `ps.fonttype` 42), stores SVG text as paths, sets no figure size, and does
  not crop saved figures (no `savefig.bbox`), so a saved file has exactly the figure's size.
- A change to the style goes together with the "What the style changes" table in `README.md` and
  the assertions in `tests/test_styles.py`.

## Rendering Figures

- The README images come from `examples/styles_demo.py` and `examples/palettes_demo.py`. All of
  them use the GraphPadPrism style except `default_style`, which shows Matplotlib's defaults.
- Lay figures out in round inches: the figure size, each axes' position and size (the axis
  lengths), and the anchors of legends and figure titles are multiples of 0.1, 0.25, 0.5 or 1 in.
  Place them with `add_axes_inches`, `legend_inches` and `suptitle_inches` from
  `mplplots.utils`, not with `tight_layout`, `subplots_adjust` or a tight bounding box.
- Keep the style's text: pass no `fontsize` or `fontweight`.
- Render every figure in three formats with `save()` from `examples/_common.py`: PNG at 600 dpi,
  SVG and PDF, side by side in `examples/`, uncropped and without timestamps, so rerunning an
  unchanged script reproduces the files byte for byte.
- Rendering needs Arial installed; the scripts exit without it. After changing the style or a
  script, rerun both scripts and commit all three formats. In `README.md`, show each image at
  100 pixels per inch of figure width.
