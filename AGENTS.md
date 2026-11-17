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
- It saves at 600 dpi (`savefig.dpi`), embeds TrueType fonts in PDF and PostScript
  (`pdf.fonttype` and `ps.fonttype` 42), stores SVG text as paths, and sets no figure size.
- A change to the style goes together with the "What the style changes" table in `README.md` and
  the assertions in `tests/test_styles.py`.
