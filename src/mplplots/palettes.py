"""Color palettes for mplplots.

Every named palette (``CUSTOM``, ``OCEAN``, ``BLUES``, ...) is a tuple of hex color strings and is
also registered by upper-case name in :data:`PALETTES`. Use :func:`set_palette` to make a palette
matplotlib's default color cycle.
"""

from collections.abc import Mapping, Sequence
from types import MappingProxyType

import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.rcsetup import cycler


def get_colors(
    name: str,
    n: int,
    start: float = 0.2,
    end: float = 0.8,
) -> tuple[str, ...]:
    """Sample n evenly-spaced hex colors from a matplotlib colormap.

    Args:
        name: Colormap name (e.g. "Blues", "Set2", "viridis").
        n: Number of colors to sample, at least 1.
        start: Start position in the colormap, between 0 and 1.
        end: End position in the colormap, between 0 and 1. It may be smaller than ``start``
            to sample the colormap in reverse.

    Returns:
        Tuple of hex color strings.

    Raises:
        ValueError: If ``n`` is less than 1, if ``start`` or ``end`` is outside [0, 1], or if
            no colormap is registered under ``name``.
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}.")
    for label, position in (("start", start), ("end", end)):
        if not 0 <= position <= 1:
            raise ValueError(f"{label} must be between 0 and 1, got {position}.")
    cmap = mpl.colormaps.get_cmap(name)
    if n == 1:
        return (mcolors.to_hex(cmap((start + end) / 2)),)
    step = (end - start) / (n - 1)
    return tuple(mcolors.to_hex(cmap(start + step * i)) for i in range(n))


# Each palette is a plain tuple, so it can be indexed and sliced. Use ``set_palette(...)`` to make
# one the default color cycle, or ``itertools.cycle(...)`` over the tuple to step through it.
CUSTOM: tuple[str, ...] = (
    "#BCE4F9",
    "#7BD3F2",
    "#F0AECB",
    "#E88791",
    "#C4DDB1",
    "#97D9A8",
    "#CCCCE6",
    "#9D9DCF",
    "#8FB0DD",
    "#F0CEA4",
    "#F8A450",
)

PASTEL: tuple[str, ...] = (
    "#A8D8EA",
    "#F6C6D0",
    "#B8E0C8",
    "#E8D4A8",
    "#C4BEE0",
    "#F2D5B8",
    "#A0C8D4",
    "#E0B8C8",
    "#C0D8A8",
    "#D8C0D8",
    "#B0D4E8",
)

WARM: tuple[str, ...] = (
    "#F0C8A4",
    "#E8A48C",
    "#F4B8B0",
    "#E4C8A0",
    "#D8A8A0",
    "#F0B4A0",
    "#D4A8B8",
    "#E8D0B4",
    "#CCAA8C",
    "#E0B4C4",
    "#ECBCA0",
)

COOL: tuple[str, ...] = (
    "#A4CCE0",
    "#B8C4DC",
    "#A0D4CC",
    "#C4B4D4",
    "#94BCC8",
    "#B4DCD4",
    "#AAB8CC",
    "#C8D0E0",
    "#9CC4B8",
    "#B4A8CC",
    "#8CBCD4",
)

EARTH: tuple[str, ...] = (
    "#BCCCAA",
    "#D4C8A4",
    "#C4ACA4",
    "#ACC4A8",
    "#CCC0A4",
    "#B8B4A0",
    "#A8BCAC",
    "#CCACA0",
    "#C0B8A4",
    "#ACB8A8",
    "#C4B4AC",
)

# ---------------------------------------------------------------------------
# Single-family palettes (derived from CUSTOM's color families)
# ---------------------------------------------------------------------------

OCEAN: tuple[str, ...] = (
    "#B4E0F0",
    "#88CCE4",
    "#6BC0D8",
    "#A0D4DC",
    "#78B8CC",
    "#5CA8C4",
    "#B0D8E8",
    "#90C4D8",
    "#68B4D0",
    "#A8CCE0",
    "#80BCCC",
)

ROSE: tuple[str, ...] = (
    "#F4C4D4",
    "#E8A0B8",
    "#DC88A0",
    "#F0B4C4",
    "#E498AC",
    "#D880A0",
    "#ECC0CC",
    "#E0A8BC",
    "#D494A8",
    "#F0C0D0",
    "#E4A4B4",
)

FOREST: tuple[str, ...] = (
    "#C8E0B8",
    "#A8D4A0",
    "#8CC498",
    "#B8D8B0",
    "#98CCA0",
    "#80BC8C",
    "#C0DCC0",
    "#A4D0AC",
    "#90C498",
    "#B4D4B8",
    "#A0CCAC",
)

LAVENDER: tuple[str, ...] = (
    "#D4CCE8",
    "#BEB4D8",
    "#A8A0CC",
    "#CCC4E0",
    "#B8ACD4",
    "#A498C8",
    "#D0C8E4",
    "#C0B4D8",
    "#ACA0CC",
    "#C8C0DC",
    "#B4A8D0",
)

SUNSET: tuple[str, ...] = (
    "#F4D4B0",
    "#F0C098",
    "#E8AC80",
    "#F0C8A4",
    "#ECB890",
    "#E4A478",
    "#F0D0B8",
    "#ECC09C",
    "#E4B088",
    "#F0CCA8",
    "#E8B894",
)

COASTAL: tuple[str, ...] = (
    "#B8D8D4",
    "#D4CCB4",
    "#A4C8CC",
    "#C8C4A8",
    "#98BCC4",
    "#D0C8B0",
    "#A8CCC4",
    "#C4C0AC",
    "#90B4BC",
    "#CCC8B8",
    "#A0C0C0",
)

# ---------------------------------------------------------------------------
# Seasonal palettes (CUSTOM hue mix shifted by season)
# ---------------------------------------------------------------------------

SPRING: tuple[str, ...] = (
    "#C4E4BC",
    "#F0C8D0",
    "#B8DCE0",
    "#E8DCA4",
    "#C8D4E8",
    "#D8E0B4",
    "#F0D0C0",
    "#B0D4C4",
    "#E0C4D8",
    "#D0E4C0",
    "#E8D4BC",
)

SUMMER: tuple[str, ...] = (
    "#E0D0A8",
    "#A8CCE0",
    "#F0C0A8",
    "#B8D4B0",
    "#E8B8C4",
    "#C4D8E4",
    "#E4CCA0",
    "#ACC8B8",
    "#E0B4B0",
    "#C8D4C4",
    "#DCC8AC",
)

AUTUMN: tuple[str, ...] = (
    "#D4B898",
    "#C8A488",
    "#D8C4A0",
    "#C0A090",
    "#CCA888",
    "#D4B8A0",
    "#B8A88C",
    "#D0B498",
    "#C4AC94",
    "#CCB4A0",
    "#BCA08C",
)

WINTER: tuple[str, ...] = (
    "#C8D8E8",
    "#B4C4D4",
    "#D4D8E0",
    "#A8B8C8",
    "#C0CCD8",
    "#B8C0CC",
    "#D0D4DC",
    "#A4B4C4",
    "#BCC8D4",
    "#C4CCD4",
    "#B0BCC8",
)

# ---------------------------------------------------------------------------
# Time-of-day palettes
# ---------------------------------------------------------------------------

DAWN: tuple[str, ...] = (
    "#F0D0C0",
    "#E0C8D8",
    "#C8D4E4",
    "#F0DCC0",
    "#D4C0D4",
    "#B8D0DC",
    "#F0D4B4",
    "#D8CCE0",
    "#C4D8D8",
    "#E8D0C4",
    "#D0CCE0",
)

DUSK: tuple[str, ...] = (
    "#B4A8C8",
    "#C8A8B8",
    "#A4ACC4",
    "#BCA0B4",
    "#98A8BC",
    "#C0ACC4",
    "#A8A4B8",
    "#B8A4B4",
    "#94A0B8",
    "#B4A8C0",
    "#A0A8BC",
)

# ---------------------------------------------------------------------------
# Thematic palettes
# ---------------------------------------------------------------------------

CANDY: tuple[str, ...] = (
    "#D0E8F0",
    "#F4C8D8",
    "#C8E8D0",
    "#F0DCC0",
    "#D8C8E8",
    "#F0D4C8",
    "#B8DCE0",
    "#E8C4D4",
    "#C8E4C0",
    "#E4D0E4",
    "#C0DCE8",
)

SMOKE: tuple[str, ...] = (
    "#B8C0C8",
    "#C8B8BC",
    "#B8C4B8",
    "#C4C0B8",
    "#BCB8C4",
    "#C8C0BC",
    "#B4BCC0",
    "#C0B8C0",
    "#BCC0B8",
    "#C4BCBC",
    "#B8BCBC",
)

VINTAGE: tuple[str, ...] = (
    "#C8D0BC",
    "#D8C4B0",
    "#C0B4B4",
    "#D0CCB4",
    "#B8B4BC",
    "#D4C8B4",
    "#BCC4BC",
    "#CCC0B4",
    "#B4B0B4",
    "#D0C8BC",
    "#C0BCC0",
)

NORDIC: tuple[str, ...] = (
    "#B4C8D0",
    "#C8D0C0",
    "#A8B8C0",
    "#BCC8BC",
    "#B0BCC8",
    "#C4CCC4",
    "#A4B4BC",
    "#BCC4BC",
    "#B8C0C8",
    "#C0C8C0",
    "#ACC0C4",
)

MEADOW: tuple[str, ...] = (
    "#C8DCA8",
    "#E8B8C8",
    "#B0D4D0",
    "#E0CCB0",
    "#C0B8D4",
    "#D4DCB0",
    "#E0B4B4",
    "#A8CCC4",
    "#D8C4D0",
    "#C4D8B4",
    "#D4C0BC",
)

CORAL: tuple[str, ...] = (
    "#F0C0B8",
    "#A8D4D4",
    "#E8B8A8",
    "#B0D0CC",
    "#E4B0B0",
    "#A4C8C8",
    "#E0C0B0",
    "#B8D4CC",
    "#DCC0BC",
    "#A8CCC4",
    "#E8C4B4",
)

TROPICAL: tuple[str, ...] = (
    "#A0D8D0",
    "#F0C8A8",
    "#B8D8BC",
    "#E8B8B8",
    "#C0D4E0",
    "#E0CCA4",
    "#A8C8CC",
    "#E4C0C4",
    "#B4D4B4",
    "#D8C0D0",
    "#A4CCD4",
)

POWDER: tuple[str, ...] = (
    "#D8E8F0",
    "#F0D8E0",
    "#D0E8D4",
    "#F0E4D0",
    "#D8D0E8",
    "#F0E0D0",
    "#CCE0E4",
    "#E8D4E0",
    "#D4E4D0",
    "#E4D4E0",
    "#D0E0E8",
)

# ---------------------------------------------------------------------------
# Pre-generated color families (muted range, avoids extremes)
# ---------------------------------------------------------------------------
BLUES: tuple[str, ...] = get_colors("Blues", 8, 0.3, 0.8)
GREENS: tuple[str, ...] = get_colors("Greens", 8, 0.3, 0.8)
REDS: tuple[str, ...] = get_colors("Reds", 8, 0.3, 0.8)
PURPLES: tuple[str, ...] = get_colors("Purples", 8, 0.3, 0.8)
ORANGES: tuple[str, ...] = get_colors("Oranges", 8, 0.3, 0.8)
GREYS: tuple[str, ...] = get_colors("Greys", 8, 0.25, 0.75)

# ---------------------------------------------------------------------------
# Registry and default-color-cycle helper
# ---------------------------------------------------------------------------
# Spelled out explicitly: identifiers are checked by mypy/ruff, and the tests check that the keys
# match the identifiers and that no module-level palette is missing from the registry.
PALETTES: Mapping[str, tuple[str, ...]] = MappingProxyType({
    # Custom-style 11-color palettes
    "CUSTOM": CUSTOM,
    "PASTEL": PASTEL,
    "WARM": WARM,
    "COOL": COOL,
    "EARTH": EARTH,
    "OCEAN": OCEAN,
    "ROSE": ROSE,
    "FOREST": FOREST,
    "LAVENDER": LAVENDER,
    "SUNSET": SUNSET,
    "COASTAL": COASTAL,
    "SPRING": SPRING,
    "SUMMER": SUMMER,
    "AUTUMN": AUTUMN,
    "WINTER": WINTER,
    "DAWN": DAWN,
    "DUSK": DUSK,
    "CANDY": CANDY,
    "SMOKE": SMOKE,
    "VINTAGE": VINTAGE,
    "NORDIC": NORDIC,
    "MEADOW": MEADOW,
    "CORAL": CORAL,
    "TROPICAL": TROPICAL,
    "POWDER": POWDER,
    # Colormap-derived 8-color families
    "BLUES": BLUES,
    "GREENS": GREENS,
    "REDS": REDS,
    "PURPLES": PURPLES,
    "ORANGES": ORANGES,
    "GREYS": GREYS,
})
"""Read-only mapping of upper-case palette name to its tuple of hex colors."""


def set_palette(palette: str | Sequence[str]) -> None:
    """Set matplotlib's default color cycle (``rcParams["axes.prop_cycle"]``) to a palette.

    Axes created afterwards cycle through the palette's colors for new lines, bars, etc. Only
    ``axes.prop_cycle`` is changed, so this composes with ``plt.rc_context()`` and
    ``plt.style.context()``: called inside such a block, the previous cycle is restored on exit.

    Args:
        palette: A palette name from :data:`PALETTES`, matched case-insensitively (``"ocean"``,
            ``"OCEAN"`` and ``"blues"`` all work), or a non-empty sequence of colors matplotlib
            accepts (hex strings, named colors, ...). A bare string is always treated as a
            palette name, never as a sequence of characters.

    Raises:
        ValueError: If the name is not in :data:`PALETTES` (the message lists the valid names),
            if the sequence is empty, or if it contains an invalid color. Cycle references such
            as ``"C0"`` are invalid here too, because matplotlib rejects them in a color cycle.

    Example:
        >>> import matplotlib.pyplot as plt
        >>> set_palette("ocean")
        >>> with plt.rc_context():
        ...     set_palette(["#1f77b4", "tab:orange"])  # only inside this block
    """
    if isinstance(palette, str):
        try:
            colors = PALETTES[palette.upper()]
        except KeyError:
            valid = ", ".join(sorted(PALETTES))
            raise ValueError(f"Unknown palette {palette!r}. Valid names: {valid}.") from None
    else:
        colors = tuple(palette)
        if not colors:
            raise ValueError("A palette must contain at least one color.")
        invalid = [c for c in colors if not mcolors.is_color_like(c)]
        if invalid:
            raise ValueError(f"Invalid color(s) in palette: {', '.join(map(repr, invalid))}.")
    # matplotlib's validating cycler() also rejects cycle references such as "C0".
    mpl.rcParams["axes.prop_cycle"] = cycler(color=colors)
