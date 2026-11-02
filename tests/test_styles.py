"""Tests for mplplots styles."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.typing import RcKeyType

STYLES_DIR = Path(__file__).resolve().parent.parent / "src" / "mplplots" / "styles"
GRAPHPAD_STYLE = str(STYLES_DIR / "GraphPadPrism.mplstyle")
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
# fonts by name, and those lookups inherit ``font.weight: bold``. Those fonts only
# come in one weight, so Matplotlib notes that it used the regular weight. This
# happens with any bold mathtext, does not change the output and cannot be avoided
# without dropping ``font.weight: bold``, so such notices are tolerated, except
# for the fonts the style uses for text and math.
WEIGHT_NOTICE = re.compile(r"findfont: Failed to find font weight \S+ for (?P<font>.+), now using")


class TestGraphPadPrismStyle:
    def test_style_file_exists(self) -> None:
        assert (STYLES_DIR / "GraphPadPrism.mplstyle").is_file()

    def test_style_is_loadable(self) -> None:
        style_path = str(STYLES_DIR / "GraphPadPrism.mplstyle")
        plt.style.use(style_path)

    def test_style_sets_dpi(self) -> None:
        style_path = str(STYLES_DIR / "GraphPadPrism.mplstyle")
        plt.style.use(style_path)
        assert matplotlib.rcParams["figure.dpi"] == 300

    def test_style_hides_top_right_spines(self) -> None:
        style_path = str(STYLES_DIR / "GraphPadPrism.mplstyle")
        plt.style.use(style_path)
        assert matplotlib.rcParams["axes.spines.top"] is False
        assert matplotlib.rcParams["axes.spines.right"] is False

    def test_style_applies_to_plot(self) -> None:
        style_path = str(STYLES_DIR / "GraphPadPrism.mplstyle")
        with plt.style.context(style_path):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            assert ax.spines["top"].get_visible() is False
            assert ax.spines["right"].get_visible() is False
            plt.close(fig)


class TestGraphPadPrismFonts:
    def test_arial_is_first_choice(self) -> None:
        with plt.style.context(GRAPHPAD_STYLE):
            assert matplotlib.rcParams["font.sans-serif"][0] == "Arial"
            assert matplotlib.rcParams["mathtext.fontset"] == "custom"

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
