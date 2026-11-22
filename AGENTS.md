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

1. `pre-commit run --all-files`: must pass with no errors
2. `pytest`: all tests must pass

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

## Documentation

- `README.md` is a short introduction; the reference documentation lives in `docs/`, one page per
  topic, indexed in both `docs/README.md` and the Documentation table of `README.md`, so a new or
  renamed page goes into both. A change to the API or a style updates the matching page.

## Code Style

- Ruff for linting and formatting (line length 100, Google-style docstrings)
- Mypy for type checking (strict-ish, see pyproject.toml)
- `src/` layout with `mplplots` package
- Tests in `tests/` using pytest (no docstrings required in tests)
- Type annotations on all public functions
- American English (color, center, gray, labeled) and ASCII characters in code, comments,
  docstrings, messages and documentation. A non-ASCII character that a figure needs is written
  as an escape (`"\u00c5"`, `"\u2014"`). The palette `GREYS` keeps the spelling of the Matplotlib
  colormap `Greys` that it samples. Pre-commit checks both (`ascii-only` and `codespell`).

## Styles

- Each style is one self-contained `.mplstyle` file in `src/mplplots/styles/`, and its stem is
  its name. `mplplots.STYLES` lists the stems, sorted; `DEFAULT_STYLE` is `"Personal"`. A style
  loads with `plt.style.use("mplplots.styles.<Name>")` without importing mplplots, so it never
  depends on mplplots code.
- Every style sets `pdf.fonttype: 42`, `ps.fonttype: 42`, `savefig.dpi: 600` and
  `svg.fonttype: path`, and sets neither `figure.figsize` nor `savefig.bbox`, so a saved file
  has exactly the figure's size. Every style resolves its fonts without warnings on a machine
  that lacks its first-choice font; the only notices tolerated are Matplotlib's weight notices
  for its bundled one-weight fonts and the style's cursive fonts, which bold math logs (all math
  in GraphPadPrism). `tests/test_styles.py` checks both for every packaged style.
- `mplplots.use` and `mplplots.context` first return every key that any packaged style sets to
  Matplotlib's default, then apply the style, so switching styles in a session gives the style
  alone. `tests/test_styles.py` checks every pair of packaged styles.
- The style table and each style's "What the style changes" table live in `docs/styles.md`;
  `README.md` keeps only a short summary of the styles.
- Adding a style takes: the file; a row in the style table of `docs/styles.md` with its own "What
  the style changes" table; a paragraph under "Minor ticks of the styles" in `docs/ticks.md`; its
  name in `README.md` (the style count in the first paragraph, the "Two styles" bullet, and the
  Styles row of the Documentation table); one image in `docs/gallery.md`; and assertions in
  `tests/test_styles.py`.
- A change to a style goes together with its "What the style changes" table in `docs/styles.md`
  and its assertions in `tests/test_styles.py`. `check_figure` reads its expected values from the
  style file, so the checker follows the change.

### Personal

- `src/mplplots/styles/Personal.mplstyle` is the default style. Its values come from the
  `PUBLICATION_RCPARAMS` of the owner's two research repositories; `tests/test_styles.py` pins
  every key it sets.
- Every text element is Arial Regular 8 pt: tick labels, axis labels, axes and figure titles,
  figure-level axis labels, and the legend and its title. Do not give any of them another size
  or weight.
- Axis lines and major ticks are 0.8 pt wide (major ticks 3.5 pt long); minor ticks are on, 0.6
  pt wide and 2 pt long, and split each major interval in two (`xtick.minor.ndivs` and
  `ytick.minor.ndivs` 2). The top and right spines are hidden. A bare data line is 2 pt.
- It saves uncropped at 600 dpi, with TrueType fonts in PDF and PostScript and SVG text as paths.

### GraphPadPrism

- `src/mplplots/styles/GraphPadPrism.mplstyle` reproduces the default graphs of GraphPad Prism
  11. Every value that comes from Prism is measured from the SVG and PDF files that Prism 11
  exports for its default XY, column and grouped graphs (exported at "Actual" size, with Prism's
  small export scale divided out); `tests/test_styles.py` pins every key it sets. A change to
  them alters how existing figures look, so it raises the minor version.
- Text is Arial Bold: tick labels 11 pt; axis labels and figure-level axis labels 12 pt; axes
  and figure titles 14 pt; the legend and its title 12 pt (`font.size` 12). Matplotlib has no
  weight setting for tick labels or the legend, so `font.weight` is bold and the legend is bold,
  where Prism draws it regular. Math text is bold too. Do not give any text another size or
  weight.
- Lengths and widths are the rendered PostScript points measured in Prism's files, not Prism's
  dialog values: Prism's "1 pt" renders 1.44 pt (1/50 in) and its "1/2 pt" 0.72 pt. Axis lines
  and ticks are 1.44 pt wide; ticks point out and reach 5.4 pt beyond the axis line (minor
  ticks 2.7 pt, off by default, as in Prism); data lines, error bars and caps are 0.72 pt; caps
  are 6.48 pt long; filled symbols are 5.76 pt across; bars given an edge color get Prism's
  2.16 pt border (`patch.linewidth`). The pads put tick labels, axis labels and the title where
  Prism puts them.
- Where the style departs from Prism is listed in `docs/styles.md` under "Where the style
  departs from Prism": among others, Prism's regular legend text, its legend outside the plot
  on the right, its 1.44 pt border on hollow symbols (only `errorbar.capthick`, new in
  Matplotlib 3.11, sets the caps apart from it, so the style leaves the border at 0.72 pt), its
  bar borders drawn inside the bar, and the font weight notices that its bold math logs.
- It saves at 600 dpi (`savefig.dpi`), embeds TrueType fonts in PDF and PostScript
  (`pdf.fonttype` and `ps.fonttype` 42), stores SVG text as paths, sets no figure size, and does
  not crop saved figures (no `savefig.bbox`), so a saved file has exactly the figure's size.

## Rendering Figures

- The images of `README.md` and `docs/` come from three scripts in `examples/`:
  - `styles_demo.py` writes `default_style`, which shows Matplotlib's defaults, and the five
    `graphpadprism_*` figures in the GraphPadPrism style.
  - `personal_demo.py` writes the five `personal_*` figures in the Personal style.
  - `palettes_demo.py` writes the eight palette figures (`all_palettes`, `color_families`,
    `get_colors_demo`, `custom_multiline`, `dusk_hbar`, `spring_area`, `candy_pie`,
    `scatter_comparison`) in the Personal style.
- Lay figures out in round inches: the figure size, each axes' position and size (the axis
  lengths), and the anchors of legends and figure titles lie on a 0.05 in grid, mostly on
  multiples of 0.1, 0.25, 0.5 or 1 in. Place them with `grid_inches`, `add_axes_inches`,
  `legend_inches` and `suptitle_inches`, not with `tight_layout`, `subplots_adjust` or a tight
  bounding box. `check_figure` (`round-inches`) checks the figure size and the axes boxes only,
  so check the anchors of legends and titles by hand.
- Keep the style's text: pass no `fontsize` or `fontweight`.
- Write variables and formulas in labels, titles and legends as math text (`"$x$"`,
  `r"$\sin(x)$"`), never as upright text (`"x"`, `"sin(x)"`). The styles set math variables in
  Arial Italic (Bold Italic in GraphPadPrism) and function names, numbers and operators upright.
- `personal_demo.py` checks each figure with `mpp.assert_figure(fig, warnings_as_errors=True)`
  before saving it, and `styles_demo.py` each `graphpadprism_*` figure with
  `assert_figure(fig, style="GraphPadPrism", warnings_as_errors=True)`.
- Save every figure with `save()` from `examples/_common.py`, which calls
  `mplplots.save_figure`: PNG at 600 dpi, SVG and PDF, side by side in `examples/`, uncropped and
  without timestamps, so rerunning an unchanged script reproduces the files byte for byte.
- Render with Matplotlib 3.11.2: another version writes its version string into every file.
  Rendering needs Arial Regular and Italic installed, and Arial Bold and Bold Italic for
  `styles_demo.py`; the scripts exit without them. After changing a style, the toolkit or a
  script, rerun all three scripts and commit all three formats.
- `docs/gallery.md` shows the gallery images, `docs/colors.md` the palette swatches and the
  `get_colors` figure, and `README.md` a selection, each at 100 pixels per inch of figure width.
  An image shown in both `README.md` and a docs page has the same alt text and width in both, so
  change them together.

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
- `evals/evals.json` holds the eval cases of the skill: a request, its input files and what a
  good result looks like, including one request the skill must not be applied to.
  `python evals/cases.py setup <case> <dir>` builds a throwaway project with the skill installed
  and prints the message for a fresh agent (`--no-skill` gives the baseline), and
  `python evals/cases.py score <dir>` runs what the agent wrote under `check_figure`. After a
  change to the skill, the rules snippet or the workflow of the style guide, run the cases with
  fresh agents and read their figures.
