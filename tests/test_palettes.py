"""Tests for mplplots.palettes."""

import re
import subprocess
import sys
from collections.abc import Iterator, Sequence

import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pytest

import mplplots.palettes as palettes
from mplplots.palettes import (
    BLUES,
    CUSTOM,
    OCEAN,
    PALETTES,
    ROSE,
    get_colors,
    set_palette,
)

HEX_RE = re.compile(r"^#[0-9a-f]{6}$")

# Every hand-picked 11-color palette
CUSTOM_STYLE_PALETTES = [
    "CUSTOM",
    "PASTEL",
    "WARM",
    "COOL",
    "EARTH",
    "OCEAN",
    "ROSE",
    "FOREST",
    "LAVENDER",
    "SUNSET",
    "COASTAL",
    "SPRING",
    "SUMMER",
    "AUTUMN",
    "WINTER",
    "DAWN",
    "DUSK",
    "CANDY",
    "SMOKE",
    "VINTAGE",
    "NORDIC",
    "MEADOW",
    "CORAL",
    "TROPICAL",
    "POWDER",
]

# Colormap-derived 8-color palettes
FAMILY_PALETTES = ["BLUES", "GREENS", "REDS", "PURPLES", "ORANGES", "GREYS"]


# ---------------------------------------------------------------------------
# get_colors() API
# ---------------------------------------------------------------------------
class TestGetColors:
    def test_returns_correct_count(self) -> None:
        assert len(get_colors("Blues", 5)) == 5

    def test_single_color(self) -> None:
        result = get_colors("Blues", 1)
        assert len(result) == 1
        assert HEX_RE.match(result[0])

    def test_returns_hex_strings(self) -> None:
        for c in get_colors("viridis", 6):
            assert HEX_RE.match(c), f"{c} is not a valid hex color"

    def test_full_range(self) -> None:
        colors = get_colors("Set2", 8, start=0, end=1)
        assert len(colors) == 8
        assert len(set(colors)) == 8

    def test_custom_range_differs(self) -> None:
        narrow = get_colors("Blues", 3, start=0.3, end=0.5)
        wide = get_colors("Blues", 3, start=0.1, end=0.9)
        assert narrow != wide

    def test_returns_tuple(self) -> None:
        assert isinstance(get_colors("Reds", 3), tuple)

    @pytest.mark.parametrize("cmap", ["Blues", "Greens", "Reds", "Purples", "viridis", "coolwarm"])
    def test_various_colormaps(self, cmap: str) -> None:
        colors = get_colors(cmap, 4)
        assert len(colors) == 4
        for c in colors:
            assert HEX_RE.match(c)

    def test_start_equals_end_single(self) -> None:
        colors = get_colors("Blues", 1, start=0.5, end=0.5)
        assert len(colors) == 1
        assert HEX_RE.match(colors[0])

    def test_large_n(self) -> None:
        colors = get_colors("viridis", 50)
        assert len(colors) == 50
        assert len(set(colors)) == 50

    def test_reversed_range(self) -> None:
        assert get_colors("viridis", 5, start=0.8, end=0.2) == get_colors("viridis", 5)[::-1]

    @pytest.mark.parametrize("n", [0, -1])
    def test_n_below_one(self, n: int) -> None:
        with pytest.raises(ValueError, match=f"n must be at least 1, got {n}"):
            get_colors("viridis", n)

    @pytest.mark.parametrize(
        ("start", "end", "label"),
        [(-0.1, 0.8, "start"), (0.2, 1.5, "end"), (float("nan"), 0.8, "start")],
    )
    def test_position_outside_unit_range(self, start: float, end: float, label: str) -> None:
        with pytest.raises(ValueError, match=f"{label} must be between 0 and 1"):
            get_colors("viridis", 3, start=start, end=end)

    def test_unknown_colormap(self) -> None:
        with pytest.raises(ValueError, match="not_a_colormap"):
            get_colors("not_a_colormap", 3)


def test_import_does_not_load_pyplot() -> None:
    # pyplot picks a GUI backend on import, which a library should leave to the caller.
    code = "import sys, mplplots.palettes; print('matplotlib.pyplot' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, timeout=120
    )
    assert result.stdout.strip() == "False"


# ---------------------------------------------------------------------------
# Custom-style 11-color palettes
# ---------------------------------------------------------------------------
class TestCustomStylePalettes:
    @pytest.mark.parametrize("name", CUSTOM_STYLE_PALETTES)
    def test_length_is_11(self, name: str) -> None:
        pal = getattr(palettes, name)
        assert len(pal) == 11, f"{name} has {len(pal)} colors, expected 11"

    @pytest.mark.parametrize("name", CUSTOM_STYLE_PALETTES)
    def test_is_tuple_of_str(self, name: str) -> None:
        pal = getattr(palettes, name)
        assert isinstance(pal, tuple)
        for c in pal:
            assert isinstance(c, str)

    @pytest.mark.parametrize("name", CUSTOM_STYLE_PALETTES)
    def test_valid_hex(self, name: str) -> None:
        pal = getattr(palettes, name)
        for c in pal:
            assert HEX_RE.match(c.lower()), f"{name}: {c} is not a valid hex color"

    @pytest.mark.parametrize("name", CUSTOM_STYLE_PALETTES)
    def test_colors_unique(self, name: str) -> None:
        pal = getattr(palettes, name)
        lower = [c.lower() for c in pal]
        assert len(set(lower)) == len(lower), f"{name} has duplicate colors"

    def test_palettes_are_distinct(self) -> None:
        seen: set[tuple[str, ...]] = set()
        for name in CUSTOM_STYLE_PALETTES:
            pal = tuple(c.lower() for c in getattr(palettes, name))
            assert pal not in seen, f"{name} duplicates another palette"
            seen.add(pal)

    def test_total_count(self) -> None:
        assert len(CUSTOM_STYLE_PALETTES) == 25


# ---------------------------------------------------------------------------
# Colormap-derived family palettes
# ---------------------------------------------------------------------------
class TestFamilyPalettes:
    @pytest.mark.parametrize("name", FAMILY_PALETTES)
    def test_length_is_8(self, name: str) -> None:
        pal = getattr(palettes, name)
        assert len(pal) == 8, f"{name} has {len(pal)} colors, expected 8"

    @pytest.mark.parametrize("name", FAMILY_PALETTES)
    def test_valid_hex(self, name: str) -> None:
        pal = getattr(palettes, name)
        for c in pal:
            assert HEX_RE.match(c), f"{name}: {c} is not a valid hex color"

    @pytest.mark.parametrize("name", FAMILY_PALETTES)
    def test_colors_unique(self, name: str) -> None:
        pal = getattr(palettes, name)
        assert len(set(pal)) == len(pal), f"{name} has duplicate colors"


# ---------------------------------------------------------------------------
# Legacy tests for CUSTOM specifically
# ---------------------------------------------------------------------------
class TestCustomPalette:
    def test_custom_length(self) -> None:
        assert len(CUSTOM) == 11

    def test_custom_hex_format(self) -> None:
        for c in CUSTOM:
            assert HEX_RE.match(c.lower()), f"{c} is not a valid hex color"


# ---------------------------------------------------------------------------
# PALETTES registry
# ---------------------------------------------------------------------------
ALL_PALETTES = CUSTOM_STYLE_PALETTES + FAMILY_PALETTES


class TestPalettesRegistry:
    def test_has_exactly_all_named_palettes(self) -> None:
        assert set(PALETTES) == set(ALL_PALETTES)
        assert len(PALETTES) == 31

    @pytest.mark.parametrize("name", ALL_PALETTES)
    def test_value_equals_module_constant(self, name: str) -> None:
        assert PALETTES[name] == getattr(palettes, name)
        assert isinstance(PALETTES[name], tuple)

    def test_covers_every_module_level_palette(self) -> None:
        # Guards against a palette being added to the module but not to the registry.
        module_palettes = {
            name
            for name, value in vars(palettes).items()
            if name.isupper()
            and isinstance(value, tuple)
            and all(isinstance(c, str) for c in value)
        }
        assert module_palettes == set(PALETTES)

    def test_keys_are_upper_case(self) -> None:
        for name in PALETTES:
            assert name == name.upper()

    def test_is_read_only(self) -> None:
        with pytest.raises(TypeError):
            PALETTES["NEW"] = ("#000000",)  # type: ignore[index]
        with pytest.raises(TypeError):
            del PALETTES["OCEAN"]  # type: ignore[attr-defined]
        assert PALETTES["OCEAN"] == OCEAN


# ---------------------------------------------------------------------------
# set_palette()
# ---------------------------------------------------------------------------
def _cycle_colors() -> list[str]:
    return list(plt.rcParams["axes.prop_cycle"].by_key()["color"])


class TestSetPalette:
    @pytest.fixture(autouse=True)
    def _restore_rcparams(self) -> Iterator[None]:
        with plt.rc_context():
            yield
        plt.close("all")

    @pytest.mark.parametrize("name", ["ocean", "OCEAN", "Ocean", "oCeAn"])
    def test_by_name_any_case(self, name: str) -> None:
        set_palette(name)
        assert _cycle_colors() == list(OCEAN)

    @pytest.mark.parametrize("name", ["blues", "BLUES", "Blues"])
    def test_family_by_name(self, name: str) -> None:
        set_palette(name)
        assert _cycle_colors() == list(BLUES)

    @pytest.mark.parametrize("name", ALL_PALETTES)
    def test_every_registered_name(self, name: str) -> None:
        set_palette(name.lower())
        assert _cycle_colors() == list(PALETTES[name])

    def test_by_explicit_list(self) -> None:
        colors = ["#112233", "red", "tab:orange", "0.5"]
        set_palette(colors)
        assert _cycle_colors() == colors

    def test_by_palette_tuple(self) -> None:
        set_palette(ROSE)
        assert _cycle_colors() == list(ROSE)

    def test_only_touches_prop_cycle(self) -> None:
        before = mpl.rcParams.copy()
        set_palette("ocean")
        after = mpl.rcParams.copy()
        changed = {key for key in after if after[key] != before[key]}
        assert changed == {"axes.prop_cycle"}

    def test_restored_after_rc_context(self) -> None:
        before = _cycle_colors()
        with plt.rc_context():
            set_palette("ocean")
            assert _cycle_colors() == list(OCEAN)
        assert _cycle_colors() == before

    def test_restored_after_style_context(self) -> None:
        set_palette("rose")
        with plt.style.context("default"):
            set_palette("ocean")
            assert _cycle_colors() == list(OCEAN)
        assert _cycle_colors() == list(ROSE)

    def test_new_plot_uses_palette(self) -> None:
        set_palette("ocean")
        _, ax = plt.subplots()
        first, second = ax.plot([0, 1]), ax.plot([1, 0])
        assert mcolors.same_color(first[0].get_color(), OCEAN[0])
        assert mcolors.same_color(second[0].get_color(), OCEAN[1])

    def test_every_new_figure_starts_at_first_color(self) -> None:
        # Colors don't depend on what was drawn before.
        set_palette("ocean")
        for _ in range(2):
            _, ax = plt.subplots()
            (line,) = ax.plot([0, 1])
            assert mcolors.same_color(line.get_color(), OCEAN[0])

    def test_unknown_name_lists_valid_names(self) -> None:
        with pytest.raises(ValueError, match="Unknown palette 'nope'") as exc_info:
            set_palette("nope")
        for name in PALETTES:
            assert name in str(exc_info.value)

    def test_bare_color_string_is_a_name_not_a_sequence(self) -> None:
        with pytest.raises(ValueError, match="Unknown palette 'red'"):
            set_palette("red")

    @pytest.mark.parametrize("empty", [[], ()])
    def test_empty_sequence(self, empty: Sequence[str]) -> None:
        with pytest.raises(ValueError, match="at least one color"):
            set_palette(empty)

    def test_invalid_color(self) -> None:
        with pytest.raises(ValueError, match="'notacolor'"):
            set_palette(["#BCE4F9", "notacolor"])

    def test_cycle_reference_rejected(self) -> None:
        with pytest.raises(ValueError):
            set_palette(["C0", "C1"])

    @pytest.mark.parametrize("bad", ["nope", [], ["notacolor"], ["C0"]])
    def test_error_leaves_rcparams_unchanged(self, bad: str | Sequence[str]) -> None:
        set_palette("rose")
        with pytest.raises(ValueError):
            set_palette(bad)
        assert _cycle_colors() == list(ROSE)
