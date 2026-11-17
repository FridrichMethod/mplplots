"""Tests for mplplots styles."""

from __future__ import annotations

import io
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
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

import mplplots

if TYPE_CHECKING:
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

STYLE_PATH = mplplots.STYLE_PATH
GRAPHPAD_STYLE = str(STYLE_PATH)
MATH_FONT_KEYS: tuple[RcKeyType, ...] = (
    "mathtext.rm",
    "mathtext.it",
    "mathtext.bf",
    "mathtext.bfit",
    "mathtext.sf",
)

# Runs in a fresh interpreter, because Matplotlib logs each font lookup only once
# per process (results are cached), so earlier tests could hide the warnings.
# rcdefaults() ignores any matplotlibrc on the machine running the tests.
RENDER_SCRIPT = r"""
import io, json, logging, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

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
style_messages = list(messages)

# Positive control: a missing family must show up in the collected messages.
fm.findfont("Mplplots Missing Family")
print(json.dumps({
    "messages": style_messages,
    "control": messages[len(style_messages):],
    "sans_serif": matplotlib.rcParams["font.sans-serif"],
}))
"""

# Matplotlib's mathtext always loads its bundled Computer Modern/STIX fallback
# fonts by name, and for bold math (``\mathbf``) it looks them up in bold. Those
# fonts only come in one weight, so Matplotlib may note that it used the regular
# weight. This does not change the output, so such notices are tolerated, except
# for the fonts the style uses for text and math.
WEIGHT_NOTICE = re.compile(r"findfont: Failed to find font weight \S+ for (?P<font>.+), now using")


class TestGraphPadPrismStyle:
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
        with plt.rc_context(earlier), plt.style.context(GRAPHPAD_STYLE):
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
        assert len(texts) > 10  # the labelled elements above plus the tick labels
        assert fonts == {(8, "normal")}

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

    def test_axis_lines_ticks_and_data_lines_are_1pt(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            _, ax = plt.subplots()
            (data,) = ax.plot([1, 2], [1, 2])
            spines = [ax.spines["left"], ax.spines["bottom"]]
            ticks = [
                tick.tick1line
                for axis in (ax.xaxis, ax.yaxis)
                for tick in axis.get_major_ticks() + axis.get_minor_ticks()
            ]
            widths = {spine.get_linewidth() for spine in spines}
            widths |= {line.get_markeredgewidth() for line in ticks}
            widths.add(data.get_linewidth())
        assert widths == {1}

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


class TestGraphPadPrismFonts:
    def test_arial_is_first_choice(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            assert matplotlib.rcParams["font.sans-serif"][0] == "Arial"
            assert matplotlib.rcParams["mathtext.fontset"] == "custom"

    def test_overrides_font_family_from_rc(self) -> None:
        # A matplotlibrc (or an earlier style) may pick another family; the style still
        # uses its sans-serif list.
        with plt.rc_context({"font.family": ["serif"]}), plt.style.context(GRAPHPAD_STYLE):
            assert matplotlib.rcParams["font.family"] == ["sans-serif"]
            font = fm.get_font(fm.findfont(FontProperties()))
            assert font.family_name in matplotlib.rcParams["font.sans-serif"]

    def test_sans_serif_always_resolves(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            # Raises if no family in font.sans-serif is installed.
            fm.findfont(FontProperties(family=["sans-serif"]), fallback_to_default=False)

    def test_math_uses_text_font(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            text_font = fm.get_font(fm.findfont(FontProperties(family=["sans-serif"])))
            for key in MATH_FONT_KEYS:
                math_font = fm.get_font(fm.findfont(matplotlib.rcParams[key]))
                assert math_font.family_name == text_font.family_name, key

    def test_math_variables_are_italic_and_functions_upright(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            variable = fm.get_font(fm.findfont(matplotlib.rcParams["mathtext.it"]))
            function = fm.get_font(fm.findfont(matplotlib.rcParams["mathtext.rm"]))
        assert any(word in variable.style_name for word in ("Italic", "Oblique"))
        assert not any(word in function.style_name for word in ("Italic", "Oblique"))

    def test_renders_without_font_warnings(self) -> None:
        result = subprocess.run(
            [sys.executable, "-c", RENDER_SCRIPT, GRAPHPAD_STYLE],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
            env={**os.environ, "MPLBACKEND": "Agg"},
        )
        assert result.returncode == 0, result.stderr
        report = json.loads(result.stdout.splitlines()[-1])
        assert report["control"], "font warnings were not captured"

        style_fonts = set(report["sans_serif"])
        unexpected = [
            message
            for message in report["messages"]
            if not (notice := WEIGHT_NOTICE.match(message)) or notice["font"] in style_fonts
        ]
        assert unexpected == []
