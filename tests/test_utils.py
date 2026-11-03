"""Tests for mplplots.utils."""

import uuid
from collections.abc import Callable, Iterator
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pytest
from fontTools.ttLib import TTFont
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text
from matplotlib.typing import RcKeyType

import mplplots
from mplplots.utils import _clear_font_caches, add_custom_fonts, auto_ticks

STYLE_PATH = str(mplplots.STYLE_PATH)
MPL_TTF_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
MATH_FONT_KEYS: tuple[RcKeyType, ...] = (
    "mathtext.rm",
    "mathtext.it",
    "mathtext.bf",
    "mathtext.bfit",
    "mathtext.sf",
)

type FontFactory = Callable[[str, str, str], Path]


class TestAutoTicks:
    def test_sets_ticks_on_simple_plot(self) -> None:
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        auto_ticks(ax)
        assert len(ax.get_xticks()) >= 3
        assert len(ax.get_yticks()) >= 3
        plt.close(fig)

    def test_respects_explicit_limits(self) -> None:
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        auto_ticks(ax, left=0.5, right=3.5, bottom=0, top=10)
        assert ax.get_xlim()[0] == 0.5
        assert ax.get_xlim()[1] == 3.5
        assert ax.get_ylim()[0] == 0
        assert ax.get_ylim()[1] == 10
        plt.close(fig)


@pytest.fixture
def make_font(tmp_path: Path) -> Iterator[FontFactory]:
    """Copy a font bundled with Matplotlib under a new family name.

    The family name is read from the font file, so a renamed copy is a font that
    Matplotlib could not find before it is registered. Registered copies are
    removed from the font manager again after the test.
    """
    created: list[Path] = []

    def factory(source: str, family: str, subfamily: str) -> Path:
        font = TTFont(MPL_TTF_DIR / source)
        names = font["name"]
        # Drop typographic/WWS names so that only the new family name is advertised.
        for name_id in (16, 17, 21, 22):
            names.removeNames(nameID=name_id)
        postscript = f"{family}-{subfamily}".replace(" ", "")
        full = f"{family} {subfamily}"
        for name_id, value in ((1, family), (2, subfamily), (4, full), (6, postscript)):
            names.setName(value, name_id, 3, 1, 0x409)  # Windows, Unicode BMP, en-US
            names.setName(value, name_id, 1, 0, 0)  # Macintosh, Roman, English
        path = tmp_path / f"{postscript}.ttf"
        font.save(path)
        created.append(path.resolve())
        return path

    yield factory

    fm.fontManager.ttflist = [
        entry for entry in fm.fontManager.ttflist if Path(entry.fname).resolve() not in created
    ]
    _clear_font_caches()


def _width(text: Text) -> float:
    return float(text.get_window_extent().width)


class TestAddCustomFonts:
    def test_font_is_found_after_failed_lookup(self, make_font: FontFactory) -> None:
        family = f"Mplplots Probe {uuid.uuid4().hex[:8]}"
        path = make_font("DejaVuSans.ttf", family, "Regular")
        prop = FontProperties(family=family)

        # The failed lookup is cached by Matplotlib.
        with pytest.raises(ValueError, match="Failed to find font"):
            fm.findfont(prop, fallback_to_default=False)

        add_custom_fonts(path)

        found = fm.findfont(prop, fallback_to_default=False)
        assert Path(found).resolve() == path.resolve()

    def test_already_drawn_figure_uses_new_font(self, make_font: FontFactory) -> None:
        # A monospace font has clearly different text extents from DejaVu Sans,
        # the fallback used before the new font is registered.
        family = f"Mplplots Probe {uuid.uuid4().hex[:8]}"
        path = make_font("DejaVuSansMono.ttf", family, "Regular")
        rc: dict[RcKeyType, object] = {
            "font.family": ["sans-serif"],
            "font.sans-serif": [family, "DejaVu Sans"],
            "mathtext.fontset": "custom",
            "mathtext.rm": "sans",
        }
        with plt.rc_context(rc):
            fig, ax = plt.subplots()
            text = ax.text(0, 0, "Wide text")
            math = ax.text(0, 0.5, r"$\mathrm{Wide\ math}$")
            fig.canvas.draw()
            before = (_width(text), _width(math))

            add_custom_fonts(path)

            # Drawing the same figure again reuses its renderer and the caches
            # Matplotlib attached to it.
            fig.canvas.draw()
            after = (_width(text), _width(math))

            fresh_fig, fresh_ax = plt.subplots()
            fresh_text = fresh_ax.text(0, 0, "Wide text")
            fresh_math = fresh_ax.text(0, 0.5, r"$\mathrm{Wide\ math}$")
            fresh_fig.canvas.draw()
            expected = (_width(fresh_text), _width(fresh_math))
            plt.close(fig)
            plt.close(fresh_fig)

        assert expected[0] != pytest.approx(before[0])
        assert expected[1] != pytest.approx(before[1])
        assert after == pytest.approx(expected)

    def test_registered_arial_is_used_by_style(self, make_font: FontFactory) -> None:
        # Stand-in for a real Arial: on machines that already have Arial, either
        # copy may win, and both are named "Arial".
        sources = {
            "Regular": "DejaVuSans.ttf",
            "Bold": "DejaVuSans-Bold.ttf",
            "Italic": "DejaVuSans-Oblique.ttf",
            "Bold Italic": "DejaVuSans-BoldOblique.ttf",
        }
        paths = [make_font(source, "Arial", sub) for sub, source in sources.items()]

        with plt.style.context(STYLE_PATH):
            # Look up (and cache) the style's fonts before Arial is registered.
            fm.findfont(FontProperties(family=["sans-serif"]))
            add_custom_fonts(*paths)

            text_font = fm.findfont(FontProperties(family=["sans-serif"]))
            assert fm.get_font(text_font).family_name == "Arial"
            for key in MATH_FONT_KEYS:
                math_font = fm.findfont(matplotlib.rcParams[key])
                assert fm.get_font(math_font).family_name == "Arial", key
