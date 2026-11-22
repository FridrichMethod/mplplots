import math
import re

import pytest

from mplplots.colors import (
    BAND_ALPHA,
    LINE_ALPHA,
    REFERENCE_LINE,
    SCATTER_ALPHA,
    SECONDARY_LINESTYLE,
    ColorPair,
    check_palette,
    contrast_ratio,
    darken,
    lighten,
    relative_luminance,
)

GREEN = ColorPair(fill="#c7e9c0", edge="#4f9d58")
GRAY = ColorPair(fill="#cccccc", edge="#7a7a7a")
YELLOW = ColorPair(fill="#fff0a6", edge="#e6b800")

CONTRAST_MESSAGE = re.compile(r"contrast (\S+) on white, below the floor (\S+)$")


def contrast_and_floor(message: str) -> tuple[str, str]:
    match = CONTRAST_MESSAGE.search(message)
    assert match is not None, message
    ratio, floor = match.groups()
    return ratio, floor


def test_constants() -> None:
    assert (SCATTER_ALPHA, BAND_ALPHA, LINE_ALPHA) == (0.6, 0.5, 0.95)
    assert dict(REFERENCE_LINE) == {"color": "0.55", "linestyle": "--", "linewidth": 0.8}
    assert SECONDARY_LINESTYLE == (0, (4, 2))
    with pytest.raises(TypeError):
        REFERENCE_LINE["color"] = "red"  # type: ignore[index]


@pytest.mark.parametrize(
    ("color", "amount", "expected"),
    [("#dd6692", 0.3, "#efb5ca"), ("#4f9d58", 0.4, "#88c38e"), ("#ffffff", 0.4, "#ffffff")],
)
def test_lighten(color: str, amount: float, expected: str) -> None:
    assert lighten(color, amount) == expected


@pytest.mark.parametrize(
    ("color", "amount", "expected"),
    [("#006d2c", 0.25, "#005221"), ("#4f9d58", 0.3, "#376e3e"), ("#000000", 0.3, "#000000")],
)
def test_darken(color: str, amount: float, expected: str) -> None:
    assert darken(color, amount) == expected


def test_any_matplotlib_color_is_accepted() -> None:
    assert lighten("tab:green", 0.0) == "#2ca02c"
    assert darken((1.0, 0.0, 0.0), 0.0) == "#ff0000"


def test_relative_luminance() -> None:
    assert relative_luminance("white") == pytest.approx(1.0)
    assert relative_luminance("black") == pytest.approx(0.0)
    assert relative_luminance("#7a7a7a") == pytest.approx(0.1946, abs=1e-4)


@pytest.mark.parametrize(
    ("color", "alpha", "expected"),
    [
        ("black", 1.0, 21.0),
        ("#e6b800", 0.95, 1.816),
        ("#ee7733", 0.95, 2.725),
        ("#4f9d58", 0.95, 3.114),
        ("#00a0aa", 0.95, 3.003),
    ],
)
def test_contrast_ratio(color: str, alpha: float, expected: float) -> None:
    assert contrast_ratio(color, alpha=alpha) == pytest.approx(expected, abs=1e-3)


def test_color_pair_unpacks() -> None:
    fill, edge = GREEN
    assert (fill, edge) == ("#c7e9c0", "#4f9d58")
    assert GREEN.edge == "#4f9d58"


def test_check_palette_accepts_a_sound_palette() -> None:
    assert check_palette({"green": GREEN, "gray": GRAY}) == []


def test_check_palette_reports_an_edge_lighter_than_its_fill() -> None:
    swapped = ColorPair(fill="#4f9d58", edge="#c7e9c0")
    (message,) = check_palette({"swapped": swapped}, min_edge_contrast=1.0)
    assert "swapped" in message
    assert "darker" in message


def test_check_palette_reports_a_shared_edge() -> None:
    twin = ColorPair(fill="#e5f5e0", edge="#4f9d58")
    (message,) = check_palette({"green": GREEN, "twin": twin})
    assert "green" in message
    assert "twin" in message


def test_check_palette_reports_low_contrast_and_honours_floors() -> None:
    (message,) = check_palette({"yellow": YELLOW})
    assert "yellow" in message
    assert "1.82" in message
    assert check_palette({"yellow": YELLOW}, floors={"yellow": 1.8}) == []


def test_lighten_and_darken_return_lowercase_hex() -> None:
    assert lighten("#4F9D58", 0.4) == "#88c38e"
    assert darken("#4F9D58", 0.3) == "#376e3e"


def test_lightness_is_clipped() -> None:
    assert lighten("#4f9d58", 5.0) == "#ffffff"
    assert darken("#4f9d58", 1.5) == "#000000"


def test_default_amounts() -> None:
    assert lighten("#4f9d58") == lighten("#4f9d58", 0.4)
    assert darken("#4f9d58") == darken("#4f9d58", 0.3)


def test_contrast_ratio_uses_the_background() -> None:
    assert contrast_ratio("white", "black") == pytest.approx(21.0)
    assert contrast_ratio("#7a7a7a", "#7a7a7a") == pytest.approx(1.0)


def test_contrast_ratio_composites_over_the_background() -> None:
    assert contrast_ratio("black", alpha=0.0) == pytest.approx(1.0)
    assert contrast_ratio("white", "black", alpha=0.0) == pytest.approx(1.0)
    assert contrast_ratio("black", alpha=0.5) < contrast_ratio("black")


def test_contrast_ratio_replaces_the_colors_own_alpha() -> None:
    assert contrast_ratio((0.0, 0.0, 0.0, 0.1)) == pytest.approx(21.0)


def test_contrast_ratio_keeps_none_transparent() -> None:
    assert contrast_ratio("none", alpha=LINE_ALPHA) == pytest.approx(1.0)
    assert contrast_ratio("none", "black") == pytest.approx(1.0)


@pytest.mark.parametrize("alpha", [-0.1, 1.1, float("nan")])
def test_contrast_ratio_rejects_an_alpha_outside_the_unit_interval(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha"):
        contrast_ratio("black", alpha=alpha)


@pytest.mark.parametrize("alpha", [-0.1, 1.1, float("nan")])
def test_check_palette_rejects_an_alpha_outside_the_unit_interval(alpha: float) -> None:
    with pytest.raises(ValueError, match="alpha"):
        check_palette({}, alpha=alpha)
    with pytest.raises(ValueError, match="alpha"):
        check_palette({"green": GREEN}, alpha=alpha)


def test_check_palette_compares_edges_as_colors() -> None:
    upper = ColorPair(fill="#e5f5e0", edge="#4F9D58")
    (message,) = check_palette({"green": GREEN, "upper": upper})
    assert "green" in message
    assert "upper" in message


def test_check_palette_reports_every_violation() -> None:
    swapped = ColorPair(fill="#4f9d58", edge="#c7e9c0")
    messages = check_palette({"green": GREEN, "swapped": swapped, "yellow": YELLOW})
    assert len(messages) == 3
    assert any("swapped" in m and "darker" in m for m in messages)
    assert any("swapped" in m and "1.31" in m for m in messages)
    assert any("yellow" in m and "1.82" in m for m in messages)


def test_check_palette_uses_line_alpha_by_default() -> None:
    cyan = {"cyan": ColorPair(fill="#abeaed", edge="#00a0aa")}
    assert check_palette(cyan) == []
    assert check_palette(cyan, alpha=1.0) == []
    (message,) = check_palette(cyan, alpha=0.9)
    assert "cyan" in message


def test_check_palette_floor_overrides_the_default_for_its_role_only() -> None:
    palette = {"green": GREEN, "yellow": YELLOW}
    assert check_palette(palette, min_edge_contrast=3.2, floors={"yellow": 1.8}) == [
        check_palette({"green": GREEN}, min_edge_contrast=3.2)[0]
    ]
    assert check_palette(palette, floors={"green": 3.2, "yellow": 1.8}) != []


def test_check_palette_accepts_an_empty_palette() -> None:
    assert check_palette({}) == []


def test_check_palette_reports_a_transparent_edge() -> None:
    (message,) = check_palette({"hidden": ColorPair(fill="#c7e9c0", edge="none")})
    assert "hidden" in message
    assert contrast_and_floor(message) == ("1.00", "3")


def test_check_palette_prints_a_ratio_just_below_the_floor_with_more_digits() -> None:
    # The ratio is 2.995006, which two decimals round up to the floor, 3.00.
    (message,) = check_palette({"gray": ColorPair(fill="#ffffff", edge="#949494")}, alpha=0.99057)
    assert contrast_and_floor(message) == ("2.995", "3")


@pytest.mark.parametrize(
    ("edge", "alpha"),
    [
        ("#949494", 0.99057),
        ("#949494", 0.97849),  # The ratio needs all 16 decimals to read below the floor.
        ("#4f9d58", LINE_ALPHA),  # The floor's 6-digit "g" format reads below the ratio.
        ("#00a0aa", LINE_ALPHA),
        ("#949494", 1.0),
    ],
)
def test_check_palette_prints_a_ratio_below_a_floor_one_step_above_it(
    edge: str, alpha: float
) -> None:
    floor = math.nextafter(contrast_ratio(edge, alpha=alpha), math.inf)
    pair = ColorPair(fill="#ffffff", edge=edge)
    (message,) = check_palette({"role": pair}, alpha=alpha, floors={"role": floor})
    ratio_text, floor_text = contrast_and_floor(message)
    assert float(floor_text) == floor
    assert float(ratio_text) < floor
