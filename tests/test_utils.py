"""Tests for mplplots.utils."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pytest
from fontTools.ttLib import TTFont
from matplotlib import ticker
from matplotlib.font_manager import FontProperties
from matplotlib.text import Text

import mplplots
from mplplots.utils import _clear_font_caches, add_custom_fonts, auto_ticks

if TYPE_CHECKING:
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

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


def _ends_on_ticks(ticks: npt.ArrayLike, limits: tuple[float, float]) -> bool:
    """Whether both ends of an axis (in either order) sit on its outermost visible ticks."""
    low, high = sorted(limits)
    tol = 1e-9 * (high - low)
    ticks = np.asarray(ticks)
    visible = ticks[(ticks >= low - tol) & (ticks <= high + tol)]
    return bool(abs(visible[0] - low) <= tol and abs(visible[-1] - high) <= tol)


def _is_round_step(step: float) -> bool:
    """Whether a tick spacing is 1, 2, 2.5 or 5 times a power of 10."""
    mantissa = step / 10 ** np.floor(np.log10(step))
    return any(np.isclose(mantissa, m) for m in (1, 2, 2.5, 5, 10))


@pytest.mark.filterwarnings("error::UserWarning")
class TestAutoTicks:
    def test_sets_ticks_on_simple_plot(self) -> None:
        _, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        auto_ticks(ax)
        assert len(ax.get_xticks()) >= 3
        assert len(ax.get_yticks()) >= 3
        assert isinstance(ax.xaxis.get_major_locator(), ticker.MaxNLocator)
        assert isinstance(ax.xaxis.get_minor_locator(), ticker.AutoMinorLocator)

    def test_respects_explicit_limits(self) -> None:
        _, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        auto_ticks(ax, left=0.5, right=3.5, bottom=0, top=10)
        assert ax.get_xlim() == (0.5, 3.5)
        assert ax.get_ylim() == (0, 10)

    def test_one_explicit_limit_other_end_on_tick(self) -> None:
        _, ax = plt.subplots()
        ax.bar([1, 2, 3], [23, 45, 12])
        auto_ticks(ax, bottom=0)
        assert ax.get_ylim()[0] == 0
        assert _ends_on_ticks(ax.get_yticks(), ax.get_ylim())

    @pytest.mark.parametrize(
        ("right", "visible_major", "divisions"),
        [
            (10, [0, 2, 4, 6, 8, 10], 2),  # six or more: halves
            (4, [0, 1, 2, 3, 4], 4),  # five: quarters
            (20, [0, 5, 10, 15, 20], 5),  # five spaced 5: fifths (every 1, not 1.25)
            (12.4, [0, 2.5, 5, 7.5, 10], 5),  # five spaced 2.5: fifths (every 0.5)
            (3.5, [0, 1, 2, 3], 5),  # four or fewer: fifths
            (17, [0, 5, 10, 15], 5),  # four or fewer spaced 5: fifths
            (7, [0, 2, 4, 6], 4),  # four or fewer spaced 2: quarters (every 0.5, not 0.4)
        ],
    )
    def test_minor_divisions(
        self, right: float, visible_major: list[float], divisions: int
    ) -> None:
        _, ax = plt.subplots()
        ax.plot([0, right], [0, 1])
        auto_ticks(ax, left=0, right=right)
        visible = [tick for tick in ax.get_xticks() if 0 <= tick <= right]
        assert visible == pytest.approx(visible_major)
        minor = ax.xaxis.get_minor_locator()
        assert isinstance(minor, ticker.AutoMinorLocator)
        assert minor.ndivs == divisions

    @pytest.mark.parametrize("style", ["default", STYLE_PATH])
    def test_unset_limits_end_on_ticks(self, style: str) -> None:
        # Snapping a limit out to a tick can make the locator choose a larger step, so the
        # snap has to be repeated until the ends sit on ticks.
        rng = np.random.default_rng(0)
        with plt.style.context(style):
            for _ in range(200):
                low = rng.uniform(-100, 100)
                high = low + 10 ** rng.uniform(-2, 3)
                fig, ax = plt.subplots()
                ax.plot([low, high], [low, high])
                auto_ticks(ax)
                for ticks, limits in (
                    (ax.get_xticks(), ax.get_xlim()),
                    (ax.get_yticks(), ax.get_ylim()),
                ):
                    assert _ends_on_ticks(ticks, limits), (low, high, limits, ticks)
                    assert _is_round_step(ticks[1] - ticks[0]), ticks
                plt.close(fig)

    @pytest.mark.parametrize("data", [(-40.367, 10.776), (69.954, 70.886), (-4.063, -4.009)])
    def test_snap_settles_when_step_grows(self, data: tuple[float, float]) -> None:
        # Data ranges where a single snap left the axis ending between ticks.
        with plt.style.context("default"):
            _, ax = plt.subplots()
            ax.plot(data, data)
            auto_ticks(ax)
        assert _ends_on_ticks(ax.get_yticks(), ax.get_ylim())

    def test_repeated_call_changes_nothing(self) -> None:
        _, ax = plt.subplots()
        ax.plot([0.3, 47.1], [-2.2, 9.7])
        auto_ticks(ax, bottom=-3)
        first = (ax.get_xlim(), ax.get_ylim(), list(ax.get_xticks()), list(ax.get_yticks()))
        auto_ticks(ax, bottom=-3)
        second = (ax.get_xlim(), ax.get_ylim(), list(ax.get_xticks()), list(ax.get_yticks()))
        assert first == second

    def test_categorical_axis_keeps_one_tick_per_category(self) -> None:
        fig, ax = plt.subplots()
        ax.bar(["A", "B", "C"], [23, 45, 12])
        xlim = ax.get_xlim()
        auto_ticks(ax, bottom=0)
        fig.canvas.draw()
        assert list(ax.get_xticks()) == [0, 1, 2]
        assert [label.get_text() for label in ax.get_xticklabels()] == ["A", "B", "C"]
        assert ax.get_xlim() == xlim
        assert isinstance(ax.xaxis.get_minor_locator(), ticker.NullLocator)
        # The numeric y-axis is still handled.
        assert ax.get_ylim()[0] == 0
        assert _ends_on_ticks(ax.get_yticks(), ax.get_ylim())

    def test_categorical_y_axis(self) -> None:
        fig, ax = plt.subplots()
        ax.barh(["low", "high"], [3.2, 5.1])
        auto_ticks(ax, left=0)
        fig.canvas.draw()
        assert [label.get_text() for label in ax.get_yticklabels()] == ["low", "high"]
        assert ax.get_xlim()[0] == 0
        assert _ends_on_ticks(ax.get_xticks(), ax.get_xlim())

    def test_categorical_axis_takes_explicit_limits(self) -> None:
        _, ax = plt.subplots()
        ax.bar(["A", "B", "C"], [23, 45, 12])
        auto_ticks(ax, left=-1, right=3)
        assert ax.get_xlim() == (-1, 3)
        assert list(ax.get_xticks()) == [0, 1, 2]

    @pytest.mark.parametrize("which", ["x", "y"])
    def test_inverted_axis_stays_inverted(self, which: str) -> None:
        _, ax = plt.subplots()
        ax.plot([0.3, 9.7], [0.3, 9.7])
        axis = ax.xaxis if which == "x" else ax.yaxis
        axis.set_inverted(True)
        auto_ticks(ax)
        assert axis.get_inverted()
        start, end = axis.get_view_interval()
        assert start > end
        assert _ends_on_ticks(axis.get_majorticklocs(), (start, end))

    def test_inverted_axis_takes_explicit_limit(self) -> None:
        _, ax = plt.subplots()
        ax.plot([0, 1], [0.3, 9.7])
        ax.invert_yaxis()
        # As in ax.set_ylim(top=0): the top edge of the inverted axis shows 0.
        auto_ticks(ax, top=0)
        bottom, top = ax.get_ylim()
        assert top == 0
        assert bottom > top
        assert _ends_on_ticks(ax.get_yticks(), (bottom, top))

    def test_log_axis_unchanged(self) -> None:
        _, ax = plt.subplots()
        ax.plot([1, 10, 100, 1000], [1, 2, 3, 4])
        ax.set_xscale("log")
        xlim = ax.get_xlim()
        major, minor = ax.xaxis.get_major_locator(), ax.xaxis.get_minor_locator()
        auto_ticks(ax)
        assert ax.get_xlim() == xlim
        assert ax.xaxis.get_major_locator() is major
        assert ax.xaxis.get_minor_locator() is minor
        # The linear y-axis is still handled.
        assert isinstance(ax.yaxis.get_major_locator(), ticker.MaxNLocator)

    def test_log_axis_takes_explicit_limits(self) -> None:
        _, ax = plt.subplots()
        ax.plot([1, 10, 100, 1000], [1, 2, 3, 4])
        ax.set_xscale("log")
        auto_ticks(ax, left=1, right=1e4)
        assert ax.get_xlim() == (1, 1e4)
        assert isinstance(ax.xaxis.get_major_locator(), ticker.LogLocator)

    def test_date_axis_unchanged(self) -> None:
        _, ax = plt.subplots()
        dates = np.array(["2024-01-01", "2024-02-15", "2024-03-01"], dtype="datetime64[D]")
        ax.plot(dates, [1, 3, 2])
        xlim = ax.get_xlim()
        major, minor = ax.xaxis.get_major_locator(), ax.xaxis.get_minor_locator()
        auto_ticks(ax)
        assert ax.get_xlim() == xlim
        assert ax.xaxis.get_major_locator() is major
        assert ax.xaxis.get_minor_locator() is minor


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
