# mplplots

Matplotlib styles (Personal by default) and a toolkit for publication figures.

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
- **Styles**: `mplplots styles` (the packaged styles, the default and their files)
- **Skill copies**: `mplplots install-skill --project DIR --check` (exit 1 if a copy in `DIR`
  is missing or stale)

## Before Committing

Always run these before `git commit` and `git push`:

1. `pre-commit run --all-files` — must pass with no errors
2. `pytest` — all tests must pass

Do not commit or push if either fails. Fix issues first.

## Changelog and Releases

- Record every user-visible change in `CHANGELOG.md` under `## [Unreleased]`, in the Keep a
  Changelog sections (Added, Changed, Fixed, ...) with its PR number.
- The version lives only in `pyproject.toml` and follows Semantic Versioning; while it is 0.x, a
  change that alters how existing figures look or breaks the API raises the minor version.
- To release: set the version in `pyproject.toml`, rename `## [Unreleased]` to
  `## [X.Y.Z] - YYYY-MM-DD` above a fresh empty `## [Unreleased]`, update the compare links at
  the bottom, merge that PR, then tag the merged commit on `main` as `vX.Y.Z` (annotated) and
  publish a GitHub release from the tag with that version's changelog section as its notes.

## Code Style

- Ruff for linting and formatting (line length 100, Google-style docstrings)
- Mypy for type checking (strict-ish, see pyproject.toml)
- `src/` layout with `mplplots` package
- Tests in `tests/` using pytest (no docstrings required in tests)
- Type annotations on all public functions

## Styles

- Each style is one self-contained `.mplstyle` file in `src/mplplots/styles/`, and its stem is
  its name. `mplplots.STYLES` lists the stems, sorted; `DEFAULT_STYLE` is `"Personal"`. A style
  loads with `plt.style.use("mplplots.styles.<Name>")` without importing mplplots, so it never
  depends on mplplots code.
- Every style sets `pdf.fonttype: 42`, `ps.fonttype: 42`, `savefig.dpi: 600` and
  `svg.fonttype: path`, and sets neither `figure.figsize` nor `savefig.bbox`, so a saved file
  has exactly the figure's size. Every style resolves its fonts without warnings on a machine
  that lacks its first-choice font. `tests/test_styles.py` checks both for every packaged style.
- Adding a style takes: the file; a row in the style table of `README.md` with its own "What the
  style changes" table; one gallery image; and assertions in `tests/test_styles.py`.
- A change to a style goes together with its "What the style changes" table in `README.md` and
  its assertions in `tests/test_styles.py`. `check_figure` reads its expected values from the
  style file, so the checker follows the change.

### Personal

- `src/mplplots/styles/Personal.mplstyle` is the default style. Its values come from the
  `PUBLICATION_RCPARAMS` of the owner's two research repositories; `tests/test_styles.py` pins
  every key it sets.
- Every text element is Arial Regular 8 pt: tick labels, axis labels, axes and figure titles,
  figure-level axis labels, and the legend and its title. Do not give any of them another size
  or weight.
- Axis lines and major ticks are 0.8 pt wide (major ticks 3.5 pt long); minor ticks are on, 0.6
  pt wide and 2 pt long. The top and right spines are hidden. A bare data line is 2 pt.
- It saves uncropped at 600 dpi, with TrueType fonts in PDF and PostScript and SVG text as paths.

### GraphPadPrism

- `src/mplplots/styles/GraphPadPrism.mplstyle` sets every text element to Arial Regular 8 pt:
  tick labels, axis labels, axes and figure titles, figure-level axis labels, and the legend and
  its title. Do not give any of them another size or weight.
- Axis lines, major and minor ticks, and data lines (including error bars) are 1 pt wide.
- It saves at 600 dpi (`savefig.dpi`), embeds TrueType fonts in PDF and PostScript
  (`pdf.fonttype` and `ps.fonttype` 42), stores SVG text as paths, sets no figure size, and does
  not crop saved figures (no `savefig.bbox`), so a saved file has exactly the figure's size.
- Its values are chosen by eye and are not measured from GraphPad Prism's defaults. A change to
  them alters how existing figures look, so it raises the minor version.

## Rendering Figures

- The README images come from three scripts in `examples/`:
  - `styles_demo.py` writes `default_style`, which shows Matplotlib's defaults, and the five
    `graphpadprism_*` figures in the GraphPadPrism style.
  - `personal_demo.py` writes the five `personal_*` figures in the Personal style.
  - `palettes_demo.py` writes the eight palette figures (`all_palettes`, `color_families`,
    `get_colors_demo`, `custom_multiline`, `dusk_hbar`, `spring_area`, `candy_pie`,
    `scatter_comparison`) in the Personal style.
- Lay figures out in round inches: the figure size, each axes' position and size (the axis
  lengths), and the anchors of legends and figure titles lie on the 0.05 in grid that
  `check_figure` checks, mostly on multiples of 0.1, 0.25, 0.5 or 1 in. Place them with
  `grid_inches`, `add_axes_inches`, `legend_inches` and `suptitle_inches`, not with
  `tight_layout`, `subplots_adjust` or a tight bounding box.
- Keep the style's text: pass no `fontsize` or `fontweight`.
- Write variables and formulas in labels, titles and legends as math text (`"$x$"`,
  `r"$\sin(x)$"`), never as upright text (`"x"`, `"sin(x)"`). The styles set math variables in
  Arial Italic and function names, numbers and operators upright.
- `personal_demo.py` checks each figure with `mpp.assert_figure(fig, warnings_as_errors=True)`
  before saving it.
- Save every figure with `save()` from `examples/_common.py`, which calls
  `mplplots.save_figure`: PNG at 600 dpi, SVG and PDF, side by side in `examples/`, uncropped and
  without timestamps, so rerunning an unchanged script reproduces the files byte for byte.
- Render with Matplotlib 3.11.2: another version writes its version string into every file.
  Rendering needs Arial Regular and Italic installed; the scripts exit without them. After
  changing a style, the toolkit or a script, rerun all three scripts and commit all three
  formats. In `README.md`, show each image at 100 pixels per inch of figure width.

## Agent Skill, Rules and Style Guide

- The files under `src/mplplots/data/` are the only copies: the skill
  (`skills/mplplots/SKILL.md`), the style guide (`skills/mplplots/references/style-guide.md`)
  and the rules snippet for a project's `AGENTS.md` (`rules/figures.md`).
  `mplplots install-skill` copies them into other projects; do not copy them anywhere in this
  repository. `pyproject.toml` lists them as package data, so they ship in the wheel.
- The style guide holds the Personal style's rules, each with an id (T1, L4, C7, ...). It names a
  value only where a rule needs it and otherwise points to the style file. The guide, the skill
  and the rules snippet are generic: they name no protein, dataset or figure of the research
  repositories.
- A rule change goes into the style guide, the checker (`RULES` and its check in
  `src/mplplots/check.py`) and its tests in `tests/test_check.py` together, and into the skill
  and the rules snippet when it changes the workflow.
- `tests/test_api.py` runs every `python` block in the style guide and the skill, so each block
  must run as written.
