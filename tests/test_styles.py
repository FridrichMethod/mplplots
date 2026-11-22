"""Tests for mplplots styles."""

from __future__ import annotations

import importlib.metadata
import io
import itertools
import json
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import matplotlib
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pytest
from matplotlib import rc_params_from_file
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

import mplplots

if TYPE_CHECKING:
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

STYLE_PATH = mplplots.STYLE_PATH
GRAPHPAD_STYLE = str(STYLE_PATH)
PERSONAL_STYLE = str(mplplots.style_path("Personal"))

# The spec's "Personal style values": every key except font.cursive and font.sans-serif,
# numbers as floats, True/False as bools. rcParams returns font.family as a list.
PERSONAL_RC: dict[RcKeyType, Any] = {
    "axes.autolimit_mode": "round_numbers",
    "axes.labelpad": 3.0,
    "axes.labelsize": 8.0,
    "axes.labelweight": "normal",
    "axes.linewidth": 0.8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.titlesize": 8.0,
    "axes.titleweight": "normal",
    "axes.unicode_minus": False,
    "errorbar.capsize": 3.0,
    "figure.dpi": 150.0,
    "figure.frameon": False,
    "figure.labelsize": 8.0,
    "figure.labelweight": "normal",
    "figure.titlesize": 8.0,
    "figure.titleweight": "normal",
    "font.family": ["sans-serif"],
    "font.size": 8.0,
    "font.weight": "normal",
    "image.cmap": "viridis",
    "legend.borderaxespad": 0.3,
    "legend.columnspacing": 1.0,
    "legend.fontsize": 8.0,
    "legend.frameon": False,
    "legend.handlelength": 1.2,
    "legend.handletextpad": 0.4,
    "legend.labelspacing": 0.25,
    "legend.loc": "upper right",
    "legend.title_fontsize": 8.0,
    "lines.linewidth": 2.0,
    "lines.markeredgecolor": "black",
    "lines.markerfacecolor": "black",
    "lines.markersize": 3.0,
    "mathtext.bf": "sans:bold",
    "mathtext.bfit": "sans:italic:bold",
    "mathtext.fontset": "custom",
    "mathtext.it": "sans:italic",
    "mathtext.rm": "sans",
    "mathtext.sf": "sans",
    "patch.linewidth": 0.5,
    "pdf.fonttype": 42.0,
    "ps.fonttype": 42.0,
    "savefig.dpi": 600.0,
    "savefig.transparent": False,
    "svg.fonttype": "path",
    "xtick.labelsize": 8.0,
    "xtick.major.size": 3.5,
    "xtick.major.width": 0.8,
    "xtick.minor.size": 2.0,
    "xtick.minor.visible": True,
    "xtick.minor.width": 0.6,
    "ytick.labelsize": 8.0,
    "ytick.major.size": 3.5,
    "ytick.major.width": 0.8,
    "ytick.minor.size": 2.0,
    "ytick.minor.visible": True,
    "ytick.minor.width": 0.6,
}
# Every key of the GraphPadPrism style except font.cursive and font.sans-serif, as rcParams
# returns it. The lengths and widths are the PostScript points measured in GraphPad Prism 11's
# exported default graphs, where Prism's "1 pt" renders 1.44 pt and its "1/2 pt" 0.72 pt.
GRAPHPAD_RC: dict[RcKeyType, Any] = {
    "axes.autolimit_mode": "round_numbers",
    "axes.labelpad": 6.15,
    "axes.labelsize": 12.0,
    "axes.labelweight": "bold",
    "axes.linewidth": 1.44,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.titlepad": 12.15,
    "axes.titlesize": 14.0,
    "axes.titleweight": "bold",
    "errorbar.capsize": 3.24,
    "figure.dpi": 300.0,
    "figure.frameon": False,
    "figure.labelsize": 12.0,
    "figure.labelweight": "bold",
    "figure.titlesize": 14.0,
    "figure.titleweight": "bold",
    "font.family": ["sans-serif"],
    "font.size": 12.0,
    "font.weight": "bold",
    "legend.fontsize": 12.0,
    "legend.frameon": False,
    "legend.handleheight": 0.68,
    "legend.handlelength": 1.28,
    "legend.handletextpad": 0.72,
    "legend.labelspacing": 0.742,
    "legend.loc": "upper right",
    "legend.title_fontsize": 12.0,
    "lines.linewidth": 0.72,
    "lines.markeredgewidth": 0.72,
    "lines.markersize": 5.04,
    "lines.solid_capstyle": "round",
    "mathtext.bf": "sans:bold",
    "mathtext.bfit": "sans:italic:bold",
    "mathtext.cal": "cursive:bold",
    "mathtext.fontset": "custom",
    "mathtext.it": "sans:italic:bold",
    "mathtext.rm": "sans:bold",
    "mathtext.sf": "sans:bold",
    "mathtext.tt": "monospace:bold",
    "patch.linewidth": 2.16,
    "pdf.fonttype": 42.0,
    "ps.fonttype": 42.0,
    "savefig.dpi": 600.0,
    "svg.fonttype": "path",
    "xtick.direction": "out",
    "xtick.labelsize": 11.0,
    "xtick.major.pad": 4.15,
    "xtick.major.size": 6.12,
    "xtick.major.width": 1.44,
    "xtick.minor.pad": 6.85,
    "xtick.minor.size": 3.42,
    "xtick.minor.visible": False,
    "xtick.minor.width": 1.44,
    "ytick.direction": "out",
    "ytick.labelsize": 11.0,
    "ytick.major.pad": 2.15,
    "ytick.major.size": 6.12,
    "ytick.major.width": 1.44,
    "ytick.minor.pad": 4.85,
    "ytick.minor.size": 3.42,
    "ytick.minor.visible": False,
    "ytick.minor.width": 1.44,
}
# GraphPad Prism 11's text: (size in points, weight) of each kind of text. Prism draws its
# legend in regular type; Matplotlib has no legend weight setting, so the style makes it bold.
PRISM_TICK_LABEL = (11.0, "bold")
PRISM_LABEL = (12.0, "bold")
PRISM_TITLE = (14.0, "bold")
PRISM_LEGEND = (12.0, "bold")
# The axis line's half width, which a tick drawn from the axis centerline spends inside it.
PRISM_AXIS_HALF_WIDTH = 0.72
PERSONAL_SANS_SERIF = [
    "Arial",
    "Helvetica",
    "Liberation Sans",
    "Arimo",
    "Nimbus Sans",
    "DejaVu Sans",
    "sans-serif",
]
MATH_FONT_KEYS: tuple[RcKeyType, ...] = (
    "mathtext.rm",
    "mathtext.it",
    "mathtext.bf",
    "mathtext.bfit",
    "mathtext.sf",
)
# Every font that math text looks up by an rcParams pattern.
MATH_PATTERN_KEYS: tuple[RcKeyType, ...] = (*MATH_FONT_KEYS, "mathtext.cal", "mathtext.tt")

# Runs in a fresh interpreter, because Matplotlib logs each font lookup only once
# per process (results are cached), so earlier tests could hide the warnings.
# rcdefaults() ignores any matplotlibrc on the machine running the tests. Font families
# named after the style argument are removed from the font list before any lookup, which
# stands in for a machine where they are not installed.
RENDER_SCRIPT = r"""
import io, json, logging, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

data_path = matplotlib.get_data_path()
bundled = sorted({f.name for f in fm.fontManager.ttflist if f.fname.startswith(data_path)})
hidden = set(sys.argv[2:])
fm.fontManager.ttflist[:] = [f for f in fm.fontManager.ttflist if f.name not in hidden]

messages = []

class Collect(logging.Handler):
    def emit(self, record):
        messages.append(record.getMessage())

logger = logging.getLogger("matplotlib.font_manager")
logger.setLevel(logging.WARNING)
logger.addHandler(Collect())
logger.propagate = False

matplotlib.rcdefaults()
plt.style.use(sys.argv[1])
fig, ax = plt.subplots()
ax.plot([1, 2], [1, 2], label="data")
ax.set_title("Title")
ax.set_xlabel(r"$\alpha$ x (mV)")
ax.set_ylabel(r"$\mathbf{F}$ / $\mathrm{d}t$ $\mathit{v}$")
ax.legend()
for fmt in ("png", "pdf", "svg"):
    fig.savefig(io.BytesIO(), format=fmt)
text_font = fm.get_font(fm.findfont(fm.FontProperties())).family_name
style_messages = list(messages)

# Positive control: a missing family must show up in the collected messages.
fm.findfont("Mplplots Missing Family")
print(json.dumps({
    "messages": style_messages,
    "control": messages[len(style_messages):],
    "sans_serif": matplotlib.rcParams["font.sans-serif"],
    "cursive": matplotlib.rcParams["font.cursive"],
    "bundled": bundled,
    "text_font": text_font,
}))
"""

# Matplotlib's mathtext always loads its bundled Computer Modern/STIX fallback
# fonts by name, and for bold math (``\mathbf``), or for all math under a bold
# style, it looks them up in bold, as it does the cursive font of ``\mathcal``.
# Those fonts only come in one weight, so Matplotlib may note that it used the
# regular weight. This does not change the output, so such notices are tolerated
# for Matplotlib's bundled fonts and the style's cursive fonts, never for the
# fonts the style uses for text and math.
WEIGHT_NOTICE = re.compile(r"findfont: Failed to find font weight \S+ for (?P<font>.+), now using")


def render_font_report(style: str, hidden: list[str] | None = None) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-c", RENDER_SCRIPT, style, *(hidden or [])],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    report: dict[str, Any] = json.loads(result.stdout.splitlines()[-1])
    assert report["control"], "font warnings were not captured"
    return report


def unexpected_font_messages(report: dict[str, Any]) -> list[str]:
    tolerated = {*report["bundled"], *report["cursive"]} - set(report["sans_serif"])
    return [
        message
        for message in report["messages"]
        if not ((notice := WEIGHT_NOTICE.match(message)) and notice["font"] in tolerated)
    ]


@pytest.fixture(params=mplplots.STYLES)
def style(request: pytest.FixtureRequest) -> str:
    return str(mplplots.style_path(request.param))


class TestStyleRegistry:
    def test_styles_lists_the_packaged_files(self) -> None:
        assert mplplots.STYLES == ("GraphPadPrism", "Personal")

    def test_personal_is_the_default(self) -> None:
        assert mplplots.DEFAULT_STYLE == "Personal"
        assert mplplots.style_path().name == "Personal.mplstyle"
        assert mplplots.style_path().is_file()

    def test_style_path_rejects_an_unknown_name(self) -> None:
        with pytest.raises(ValueError, match="GraphPadPrism, Personal"):
            mplplots.style_path("Nope")

    def test_use_applies_the_default_and_a_named_style(self) -> None:
        mplplots.use()
        assert plt.rcParams["axes.linewidth"] == 0.8
        mplplots.use("GraphPadPrism")
        assert plt.rcParams["axes.linewidth"] == 1.44

    def test_context_restores_rcparams(self) -> None:
        before = plt.rcParams["axes.linewidth"]
        with mplplots.context():
            assert plt.rcParams["axes.linewidth"] == 0.8
        assert plt.rcParams["axes.linewidth"] == before

    def test_context_applies_a_named_style(self) -> None:
        with mplplots.context("GraphPadPrism"):
            assert plt.rcParams["lines.linewidth"] == 0.72

    @pytest.mark.parametrize(("before", "after"), list(itertools.permutations(mplplots.STYLES, 2)))
    def test_switching_styles_gives_the_style_alone(self, before: str, after: str) -> None:
        # A setting that only the earlier style sets returns to Matplotlib's default instead
        # of carrying over into the later style.
        plt.style.use("default")
        mplplots.use(after)
        alone = dict(plt.rcParams)
        mplplots.use(before)
        mplplots.use(after)
        assert dict(plt.rcParams) == alone
        mplplots.use(before)
        with mplplots.context(after):
            assert dict(plt.rcParams) == alone
        mplplots.use(before)
        mplplots.prism_style()
        mplplots.use(after)
        assert dict(plt.rcParams) == alone

    def test_use_resets_the_settings_of_every_packaged_style(self) -> None:
        mplplots.use("GraphPadPrism")
        mplplots.use("Personal")
        assert plt.rcParams["axes.titlepad"] == matplotlib.rcParamsDefault["axes.titlepad"]
        assert plt.rcParams["lines.solid_capstyle"] == "projecting"
        mplplots.use("Personal")
        mplplots.use("GraphPadPrism")
        assert plt.rcParams["axes.unicode_minus"] is True
        assert plt.rcParams["lines.markerfacecolor"] == "auto"

    @pytest.mark.parametrize(("before", "after"), list(itertools.permutations(mplplots.STYLES, 2)))
    def test_math_fonts_do_not_depend_on_the_style_before(self, before: str, after: str) -> None:
        # Matplotlib before 3.11 caches a font lookup by its pattern alone, without
        # font.weight, so a math font resolves the same after a style of another weight only
        # if its pattern names its weight.
        with mplplots.context(before):
            for key in MATH_PATTERN_KEYS:
                fm.findfont(matplotlib.rcParams[key])
        with mplplots.context(after):
            for key in MATH_PATTERN_KEYS:
                pattern = matplotlib.rcParams[key]
                assert fm.findfont(pattern) == fm.findfont(FontProperties(pattern)), key

    def test_dotted_name_loads(self) -> None:
        plt.style.use("mplplots.styles.Personal")
        assert plt.rcParams["font.size"] == 8.0

    def test_prism_api_is_unchanged(self) -> None:
        assert mplplots.STYLE_PATH.name == "GraphPadPrism.mplstyle"
        assert mplplots.style_path("GraphPadPrism") == mplplots.STYLE_PATH
        mplplots.prism_style()
        assert plt.rcParams["lines.linewidth"] == 0.72

    def test_version_matches_the_distribution(self) -> None:
        assert mplplots.__version__ == importlib.metadata.version("mplplots")


@pytest.mark.parametrize("name", mplplots.STYLES)
class TestStyleCollection:
    def test_export_settings(self, name: str) -> None:
        rc = rc_params_from_file(mplplots.style_path(name), use_default_template=False)
        assert rc["pdf.fonttype"] == 42
        assert rc["ps.fonttype"] == 42
        assert rc["savefig.dpi"] == 600
        assert rc["svg.fonttype"] == "path"

    def test_sets_no_figure_size_and_no_crop(self, name: str) -> None:
        rc = rc_params_from_file(mplplots.style_path(name), use_default_template=False)
        assert "figure.figsize" not in rc
        assert "savefig.bbox" not in rc


class TestPersonalStyle:
    @pytest.mark.parametrize(("key", "value"), PERSONAL_RC.items(), ids=list(PERSONAL_RC))
    def test_value(self, key: RcKeyType, value: Any) -> None:
        with mplplots.context("Personal"):
            assert plt.rcParams[key] == value

    def test_sets_exactly_the_specified_keys(self) -> None:
        rc = rc_params_from_file(PERSONAL_STYLE, use_default_template=False)
        assert set(rc) == {*PERSONAL_RC, "font.cursive", "font.sans-serif"}

    def test_font_lists(self) -> None:
        personal = rc_params_from_file(PERSONAL_STYLE, use_default_template=False)
        prism = rc_params_from_file(GRAPHPAD_STYLE, use_default_template=False)
        assert personal["font.sans-serif"] == PERSONAL_SANS_SERIF
        assert personal["font.cursive"] == prism["font.cursive"]

    def test_every_text_element_is_regular_8pt(self) -> None:
        # Bold, large settings from a matplotlibrc (or an earlier style) are overridden.
        earlier: dict[RcKeyType, Any] = {
            "font.size": 20,
            "font.weight": "bold",
            "axes.labelweight": "bold",
            "axes.titleweight": "bold",
            "figure.titleweight": "bold",
            "figure.labelweight": "bold",
        }
        with plt.rc_context(earlier), plt.style.context(PERSONAL_STYLE):
            fig, ax = plt.subplots()
            ax.plot([1, 2], [1, 2], label="data")
            ax.set_title("Title")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.legend(title="Legend")
            fig.suptitle("Figure title")
            fig.supxlabel("Figure x")
            fig.supylabel("Figure y")
            fig.canvas.draw()
            texts = [text for text in fig.findobj(Text) if text.get_text()]
            plt.close(fig)
        fonts = {(text.get_fontsize(), text.get_fontweight()) for text in texts}
        assert len(texts) > 10  # the labeled elements above plus the tick labels
        assert fonts == {(8, "normal")}

    def test_saved_figure_keeps_its_size(self) -> None:
        # No tight bounding box: the file is the whole figure, so it keeps the figure's size.
        with plt.style.context(PERSONAL_STYLE):
            fig, ax = plt.subplots(figsize=(2, 1.5))
            ax.plot([1, 2], [1, 2])
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=100)
            plt.close(fig)
        buffer.seek(0)
        height, width = plt.imread(buffer).shape[:2]
        assert (width, height) == (200, 150)

    def test_negative_tick_labels_use_hyphen_minus(self) -> None:
        with plt.style.context(PERSONAL_STYLE):
            fig, ax = plt.subplots()
            ax.plot([-2, 2], [-2, 2])
            fig.canvas.draw()
            labels = [label.get_text() for label in ax.get_xticklabels()]
            plt.close(fig)
        assert any(label.startswith("-") for label in labels)
        assert not any("\N{MINUS SIGN}" in label for label in labels)


class TestGraphPadPrismStyle:
    @pytest.mark.parametrize(("key", "value"), GRAPHPAD_RC.items(), ids=list(GRAPHPAD_RC))
    def test_value(self, key: RcKeyType, value: Any) -> None:
        with mplplots.context("GraphPadPrism"):
            assert plt.rcParams[key] == value

    def test_sets_exactly_the_specified_keys(self) -> None:
        rc = rc_params_from_file(GRAPHPAD_STYLE, use_default_template=False)
        assert set(rc) == {*GRAPHPAD_RC, "font.cursive", "font.sans-serif"}

    def test_font_lists(self) -> None:
        rc = rc_params_from_file(GRAPHPAD_STYLE, use_default_template=False)
        assert rc["font.sans-serif"] == PERSONAL_SANS_SERIF

    def test_style_file_exists(self) -> None:
        assert (STYLE_PATH).is_file()

    def test_style_is_loadable(self) -> None:
        style_path = str(STYLE_PATH)
        plt.style.use(style_path)

    def test_style_sets_dpi(self) -> None:
        mplplots.prism_style()
        assert matplotlib.rcParams["figure.dpi"] == 300
        assert matplotlib.rcParams["savefig.dpi"] == 600

    def test_saved_figure_keeps_its_size(self) -> None:
        # No tight bounding box: the file is the whole figure, so it keeps the figure's size.
        with plt.style.context(GRAPHPAD_STYLE):
            fig, ax = plt.subplots(figsize=(2, 1.5))
            ax.plot([1, 2], [1, 2])
            buffer = io.BytesIO()
            fig.savefig(buffer, format="png", dpi=100)
            plt.close(fig)
        buffer.seek(0)
        height, width = plt.imread(buffer).shape[:2]
        assert (width, height) == (200, 150)

    def test_style_sets_no_figure_size(self) -> None:
        with plt.rc_context({"figure.figsize": (1.5, 2.5)}), plt.style.context(GRAPHPAD_STYLE):
            assert list(matplotlib.rcParams["figure.figsize"]) == [1.5, 2.5]

    def test_every_text_element_has_prisms_size_and_weight(self) -> None:
        # Settings from a matplotlibrc (or an earlier style) are overridden.
        earlier: dict[RcKeyType, Any] = {
            "font.size": 20,
            "font.weight": "light",
            "axes.labelsize": 6,
            "axes.labelweight": "normal",
            "axes.titlesize": 6,
            "axes.titleweight": "normal",
            "figure.labelsize": 6,
            "figure.labelweight": "normal",
            "figure.titlesize": 6,
            "figure.titleweight": "normal",
            "legend.fontsize": 6,
            "legend.title_fontsize": 6,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
        }
        with plt.rc_context(earlier), plt.style.context(GRAPHPAD_STYLE):
            fig, ax = plt.subplots()
            ax.plot([1, 2], [1, 2], label="data")
            legend = ax.legend(title="Legend")
            kinds: dict[str, list[Text]] = {
                "label": [
                    ax.set_xlabel("x"),
                    ax.set_ylabel("y"),
                    fig.supxlabel("Figure x"),
                    fig.supylabel("Figure y"),
                ],
                "title": [ax.set_title("Title"), fig.suptitle("Figure title")],
                "legend": [*legend.get_texts(), legend.get_title()],
                "text": [ax.text(1.5, 1.5, "Note")],
            }
            fig.canvas.draw()
            kinds["tick label"] = [*ax.get_xticklabels(), *ax.get_yticklabels()]
            fonts = {
                kind: {(text.get_fontsize(), text.get_fontweight()) for text in texts}
                for kind, texts in kinds.items()
            }
            plt.close(fig)
        assert all(text.get_text() for text in kinds["tick label"])
        assert fonts == {
            "label": {PRISM_LABEL},
            "title": {PRISM_TITLE},
            "legend": {PRISM_LEGEND},
            "text": {(12.0, "bold")},
            "tick label": {PRISM_TICK_LABEL},
        }

    def test_math_is_set_in_the_bold_text_font(self) -> None:
        # Math matches the bold text: the bold face of the text font for numbers and function
        # names, its bold italic for variables.
        with plt.style.context(GRAPHPAD_STYLE):
            text = fm.findfont(FontProperties())
            italic = fm.findfont(FontProperties(style="italic"))
            assert fm.findfont(matplotlib.rcParams["mathtext.rm"]) == text
            assert fm.findfont(matplotlib.rcParams["mathtext.it"]) == italic
            assert FontProperties().get_weight() == "bold"

    def test_pdf_embeds_truetype_and_svg_uses_paths(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            fig, ax = plt.subplots()
            ax.set_title("Title")
            pdf, svg = io.BytesIO(), io.BytesIO()
            fig.savefig(pdf, format="pdf")
            fig.savefig(svg, format="svg")
            plt.close(fig)
        assert b"/FontFile2" in pdf.getvalue()  # TrueType font program (Type 42)
        assert b"/Type3" not in pdf.getvalue()
        assert b"<text" not in svg.getvalue()

    def test_style_hides_top_right_spines(self) -> None:
        mplplots.prism_style()
        assert matplotlib.rcParams["axes.spines.top"] is False
        assert matplotlib.rcParams["axes.spines.right"] is False

    def test_axis_lines_and_ticks_are_prisms(self) -> None:
        # Prism's "1 pt" axes and ticks render 1.44 pt wide; its ticks point out and reach 5.4 pt
        # beyond the axis line. A Matplotlib tick starts at the axis centerline, half the axis
        # width inside the line.
        with plt.style.context(GRAPHPAD_STYLE):
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 1])
            fig.canvas.draw()
            spines = {ax.spines[name].get_linewidth() for name in ("left", "bottom")}
            ticks = [
                tick.tick1line for axis in (ax.xaxis, ax.yaxis) for tick in axis.get_major_ticks()
            ]
            assert spines == {1.44}
            assert {line.get_markeredgewidth() for line in ticks} == {1.44}
            beyond = {round(line.get_markersize() - PRISM_AXIS_HALF_WIDTH, 6) for line in ticks}
            assert beyond == {5.4}
            assert set(ax.xaxis.get_ticks_direction()) == {"out"}
            assert set(ax.yaxis.get_ticks_direction()) == {"out"}
            plt.close(fig)

    def test_minor_ticks_are_hidden_but_keep_prisms_size(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            fig, ax = plt.subplots()
            ax.plot([0, 1], [0, 1])
            fig.canvas.draw()
            assert len(ax.xaxis.get_minorticklocs()) == 0
            assert len(ax.yaxis.get_minorticklocs()) == 0
            ax.minorticks_on()  # Prism's minor ticks, when a figure turns them on.
            fig.canvas.draw()
            minor = [
                tick.tick1line for axis in (ax.xaxis, ax.yaxis) for tick in axis.get_minor_ticks()
            ]
            plt.close(fig)
        assert minor
        assert {line.get_markeredgewidth() for line in minor} == {1.44}
        beyond = {round(line.get_markersize() - PRISM_AXIS_HALF_WIDTH, 6) for line in minor}
        assert beyond == {2.7}

    def test_data_lines_error_bars_and_symbols_are_prisms(self) -> None:
        # Prism's "1/2 pt" connecting lines, error bars and caps render 0.72 pt wide, its caps
        # are 6.48 pt long, and its size 4 symbols 5.76 pt across. A marker's edge is centered
        # on its outline, so the drawn symbol is markersize + markeredgewidth across.
        with plt.style.context(GRAPHPAD_STYLE):
            _, ax = plt.subplots()
            (line,) = ax.plot([0, 1], [0, 1])
            data, caps, (stems,) = ax.errorbar([0.5], [0.5], yerr=[0.1], fmt="o")
        assert line.get_linewidth() == 0.72
        assert line.get_solid_capstyle() == "round"
        assert list(stems.get_linewidths()) == [0.72]
        assert {cap.get_markeredgewidth() for cap in caps} == {0.72}
        assert {cap.get_markersize() for cap in caps} == {6.48}
        assert data.get_markersize() + data.get_markeredgewidth() == pytest.approx(5.76)

    def test_bars_outlined_on_request_get_prisms_border(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            _, ax = plt.subplots()
            (outlined,) = ax.bar([0], [1], edgecolor="black")
            (plain,) = ax.bar([1], [1])
        assert outlined.get_linewidth() == 2.16
        assert mcolors.to_rgba(plain.get_edgecolor())[3] == 0  # no edge unless asked for

    def test_style_applies_to_plot(self) -> None:
        style_path = str(STYLE_PATH)
        with plt.style.context(style_path):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            assert ax.spines["top"].get_visible() is False
            assert ax.spines["right"].get_visible() is False
            plt.close(fig)

    def test_markers_follow_line_color(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            _, ax = plt.subplots()
            (line,) = ax.plot([1, 2], [1, 2], "o-", color="#5CA8C4")
            errorbar = ax.errorbar([1], [1], yerr=[0.1], fmt="s", color="#E88791")
        for artist, color in ((line, "#5CA8C4"), (errorbar.lines[0], "#E88791")):
            assert mcolors.same_color(artist.get_markerfacecolor(), color)
            assert mcolors.same_color(artist.get_markeredgecolor(), color)


class TestStyleFonts:
    def test_arial_is_first_choice(self, style: str) -> None:
        with plt.style.context(style):
            assert matplotlib.rcParams["font.sans-serif"][0] == "Arial"
            assert matplotlib.rcParams["mathtext.fontset"] == "custom"

    def test_overrides_font_family_from_rc(self, style: str) -> None:
        # A matplotlibrc (or an earlier style) may pick another family; the style still
        # uses its sans-serif list.
        with plt.rc_context({"font.family": ["serif"]}), plt.style.context(style):
            assert matplotlib.rcParams["font.family"] == ["sans-serif"]
            font = fm.get_font(fm.findfont(FontProperties()))
            assert font.family_name in matplotlib.rcParams["font.sans-serif"]

    def test_sans_serif_always_resolves(self, style: str) -> None:
        with plt.style.context(style):
            # Raises if no family in font.sans-serif is installed.
            fm.findfont(FontProperties(family=["sans-serif"]), fallback_to_default=False)

    def test_math_uses_text_font(self, style: str) -> None:
        with plt.style.context(style):
            text_font = fm.get_font(fm.findfont(FontProperties(family=["sans-serif"])))
            for key in MATH_FONT_KEYS:
                math_font = fm.get_font(fm.findfont(matplotlib.rcParams[key]))
                assert math_font.family_name == text_font.family_name, key

    def test_math_variables_are_italic_and_functions_upright(self, style: str) -> None:
        with plt.style.context(style):
            variable = fm.get_font(fm.findfont(matplotlib.rcParams["mathtext.it"]))
            function = fm.get_font(fm.findfont(matplotlib.rcParams["mathtext.rm"]))
        assert any(word in variable.style_name for word in ("Italic", "Oblique"))
        assert not any(word in function.style_name for word in ("Italic", "Oblique"))

    def test_renders_without_font_warnings(self, style: str) -> None:
        report = render_font_report(style)
        assert "cmr10" in report["bundled"]
        assert unexpected_font_messages(report) == []

    @pytest.mark.parametrize("missing", ["first-choice", "all-but-dejavu-sans"])
    def test_falls_back_without_font_warnings(self, style: str, missing: str) -> None:
        # A machine without the first-choice font (or without any listed font except DejaVu
        # Sans, which ships with Matplotlib) renders in the next family, without warnings.
        families = list(rc_params_from_file(style, use_default_template=False)["font.sans-serif"])
        if missing == "first-choice":
            hidden = families[:1]
        else:
            hidden = [family for family in families if family not in {"DejaVu Sans", "sans-serif"}]
        report = render_font_report(style, hidden)
        assert report["text_font"] in families
        assert report["text_font"] not in hidden
        assert unexpected_font_messages(report) == []
