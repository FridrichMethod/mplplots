"""Color pairs, lightness helpers, contrast and the alpha and line constants of the style.

A project's palette maps each role to a ``ColorPair``: the edge carries the role's identity
(lines, marker edges, bar borders) and the fill is its pale partner, drawn under alpha (bands,
bar faces, scatter faces). ``check_palette`` tests a palette for the mechanical invariants of
that contract.

Contrast follows WCAG 2: ``relative_luminance`` is the sRGB relative luminance and
``contrast_ratio`` the ratio ``(L1 + 0.05) / (L2 + 0.05)`` of the lighter to the darker
luminance.
"""

from collections.abc import Mapping
from colorsys import hls_to_rgb, rgb_to_hls
from types import MappingProxyType
from typing import Any, NamedTuple

import matplotlib.colors as mcolors
from matplotlib.typing import ColorType

__all__ = [
    "BAND_ALPHA",
    "LINE_ALPHA",
    "REFERENCE_LINE",
    "SCATTER_ALPHA",
    "SECONDARY_LINESTYLE",
    "ColorPair",
    "check_palette",
    "contrast_ratio",
    "darken",
    "lighten",
    "relative_luminance",
]

SCATTER_ALPHA: float = 0.6
"""Alpha for scatter dots, histogram fills and density fills."""

BAND_ALPHA: float = 0.5
"""Alpha for mean +/- SEM bands and confidence bands."""

LINE_ALPHA: float = 0.95
"""Alpha for curves: mean curves, smooth density overlays and regression lines."""

REFERENCE_LINE: Mapping[str, Any] = MappingProxyType({
    "color": "0.55",
    "linestyle": "--",
    "linewidth": 0.8,
})
"""Keyword arguments for a reference or threshold line (y = x, a cutoff): dashed gray 0.8 pt.

Read-only; use it as ``ax.axhline(0.5, **REFERENCE_LINE)``.
"""

SECONDARY_LINESTYLE: tuple[int, tuple[int, int]] = (0, (4, 2))
"""Dash pattern that marks a second variable within one hue.

The dashes are 4 on and 2 off in multiples of the line width, because Matplotlib scales dash
lengths by the line width (``lines.scale_dashes``, which no packaged style changes).
"""


class ColorPair(NamedTuple):
    """The two colors of a palette role.

    It unpacks as ``fill, edge = pair``.

    Attributes:
        fill: The pale color drawn under alpha: bands, bar faces, scatter faces.
        edge: The darker color that carries identity: lines, marker edges, bar borders.
    """

    fill: str
    edge: str


def _shift_lightness(color: ColorType, factor: float) -> str:
    """Multiply the HLS lightness of a color by a factor.

    The new lightness is clipped to [0, 1]; hue and saturation are kept.

    Args:
        color: Any Matplotlib color. Its alpha channel is ignored.
        factor: The factor; above 1 lightens, below 1 darkens.

    Returns:
        The shifted color as a lowercase ``#rrggbb`` string.
    """
    hue, lightness, saturation = rgb_to_hls(*mcolors.to_rgb(color))
    shifted = max(0.0, min(1.0, lightness * float(factor)))
    return mcolors.to_hex(hls_to_rgb(hue, shifted, saturation))


def lighten(color: ColorType, amount: float = 0.4) -> str:
    """Return a lighter variant of a color.

    The HLS lightness is multiplied by ``1 + amount`` and clipped to [0, 1]. Use it to derive a
    further member of a hue family instead of adding a new color constant.

    Args:
        color: Any Matplotlib color. Its alpha channel is ignored.
        amount: The relative increase in lightness.

    Returns:
        The lighter color as a lowercase ``#rrggbb`` string.

    Examples:
        >>> lighten("#dd6692", 0.3)
        '#efb5ca'
    """
    return _shift_lightness(color, 1.0 + amount)


def darken(color: ColorType, amount: float = 0.3) -> str:
    """Return a darker variant of a color.

    The HLS lightness is multiplied by ``1 - amount`` and clipped to [0, 1].

    Args:
        color: Any Matplotlib color. Its alpha channel is ignored.
        amount: The relative decrease in lightness.

    Returns:
        The darker color as a lowercase ``#rrggbb`` string.

    Examples:
        >>> darken("#006d2c", 0.25)
        '#005221'
    """
    return _shift_lightness(color, 1.0 - amount)


def _linearize(channel: float) -> float:
    """Convert one encoded sRGB channel in [0, 1] to linear light.

    The threshold 0.04045 is that of the sRGB standard (IEC 61966-2-1) and of WCAG 2.2.

    Args:
        channel: The encoded channel value.

    Returns:
        The linear-light channel value.
    """
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def _luminance(rgb: tuple[float, float, float]) -> float:
    """Return the WCAG relative luminance of encoded sRGB channels.

    Args:
        rgb: The encoded red, green and blue channels, each in [0, 1].

    Returns:
        The relative luminance, from 0 for black to 1 for white.
    """
    red, green, blue = (_linearize(channel) for channel in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def relative_luminance(color: ColorType) -> float:
    """Return the WCAG 2 relative luminance of a color.

    Args:
        color: Any Matplotlib color. Its alpha channel is ignored.

    Returns:
        The relative luminance, from 0 for black to 1 for white.

    Examples:
        >>> round(relative_luminance("#7a7a7a"), 4)
        0.1946
    """
    return _luminance(mcolors.to_rgb(color))


def _check_alpha(alpha: float) -> None:
    """Raise unless an alpha is in [0, 1].

    Args:
        alpha: The opacity to check.

    Raises:
        ValueError: If ``alpha`` is not in [0, 1], which includes NaN.
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha must be in [0, 1], got {alpha}")


def _format_exact(value: float) -> str:
    """Format a number briefly, with as many digits as it needs to read back unchanged.

    Args:
        value: The number.

    Returns:
        The ``g`` format of ``value`` if it reads back as ``value``, otherwise its ``repr``.
    """
    text = f"{value:g}"
    return text if float(text) == value else repr(float(value))


def _format_below(value: float, limit: float) -> str:
    """Format a number that is below a limit so that the text reads below the limit too.

    Args:
        value: The number, below ``limit``.
        limit: The limit.

    Returns:
        ``value`` to two decimals, or to as many more as keep the rounded text below ``limit``.
    """
    digits = 2
    while digits < 17 and float(f"{value:.{digits}f}") >= limit:
        digits += 1
    return f"{value:.{digits}f}"


def contrast_ratio(
    color: ColorType, background: ColorType = "white", *, alpha: float = 1.0
) -> float:
    """Return the WCAG 2 contrast ratio of a color drawn at an alpha over a background.

    ``color`` is composited over ``background`` at ``alpha`` in encoded sRGB, as Matplotlib
    renders it, and the result is compared with ``background``. As for a Matplotlib artist whose
    alpha is set, ``alpha`` replaces any alpha channel of ``color``, except that ``"none"``
    stays fully transparent and so has a contrast ratio of 1.

    Args:
        color: Any Matplotlib color.
        background: The opaque background color. Its alpha channel is ignored.
        alpha: The opacity at which ``color`` is drawn, in [0, 1].

    Returns:
        The contrast ratio, from 1 (no contrast) to 21 (black on white).

    Raises:
        ValueError: If ``alpha`` is not in [0, 1].

    Examples:
        >>> contrast_ratio("black")
        21.0
        >>> round(contrast_ratio("#e6b800", alpha=0.95), 3)
        1.816
    """
    _check_alpha(alpha)
    back = mcolors.to_rgb(background)
    *fore, opacity = mcolors.to_rgba(color, alpha)
    red, green, blue = (opacity * f + (1.0 - opacity) * b for f, b in zip(fore, back))
    lighter, darker = sorted((_luminance((red, green, blue)), _luminance(back)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def check_palette(
    palette: Mapping[str, ColorPair],
    *,
    min_edge_contrast: float = 3.0,
    alpha: float = LINE_ALPHA,
    floors: Mapping[str, float] | None = None,
) -> list[str]:
    """Check a palette of color pairs for the mechanical invariants of the style.

    It reports, with one message per violation that names the role or roles:

    - an edge that is not darker (lower relative luminance) than its own fill;
    - an edge whose ``contrast_ratio(edge, alpha=alpha)`` on white is below the role's floor,
      which is ``floors[role]`` if given and ``min_edge_contrast`` otherwise;
    - an edge color that several roles share, one message per shared color.

    Args:
        palette: The palette, mapping each role name to its color pair.
        min_edge_contrast: The contrast floor for a role without its own floor.
        alpha: The opacity at which edges are drawn, ``LINE_ALPHA`` by default.
        floors: Per-role contrast floors, for a lighter warm hue that is a documented exception
            and carries a non-color cue. Roles not in ``palette`` are ignored.

    Returns:
        The messages: those about single roles in palette order, then those about shared
        edges. An empty list for a sound palette. A contrast message gives the ratio to two
        decimals, or to as many more as show it below the floor.

    Raises:
        ValueError: If ``alpha`` is not in [0, 1] or a color is not a valid Matplotlib color.

    Examples:
        >>> check_palette({"green": ColorPair(fill="#c7e9c0", edge="#4f9d58")})
        []
    """
    _check_alpha(alpha)
    floors = {} if floors is None else floors
    messages: list[str] = []
    roles_by_edge: dict[str, list[str]] = {}
    for role, (fill, edge) in palette.items():
        if relative_luminance(edge) >= relative_luminance(fill):
            messages.append(f"{role!r}: edge {edge} is not darker than its fill {fill}")
        floor = floors.get(role, min_edge_contrast)
        ratio = contrast_ratio(edge, alpha=alpha)
        if ratio < floor:
            messages.append(
                f"{role!r}: edge {edge} at alpha {alpha:g} has contrast"
                f" {_format_below(ratio, floor)} on white, below the floor {_format_exact(floor)}"
            )
        roles_by_edge.setdefault(mcolors.to_hex(edge), []).append(role)
    for edge, roles in roles_by_edge.items():
        if len(roles) > 1:
            names = ", ".join(repr(role) for role in roles[:-1]) + f" and {roles[-1]!r}"
            messages.append(f"{names} share the edge color {edge}")
    return messages
