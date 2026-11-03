"""Utility functions for mplplots."""

import math
import os
from collections.abc import Callable, MutableMapping

import matplotlib.font_manager as fm
import matplotlib.text as mtext
import numpy as np
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.category import StrCategoryConverter
from matplotlib.mathtext import MathTextParser

type StrPath = str | os.PathLike[str]


def add_custom_fonts(*paths: StrPath) -> None:
    """Add custom fonts to the font manager.

    The fonts take effect immediately, even if Matplotlib has already looked up
    (and cached) a font for the same family, e.g. when Arial is registered after a
    figure was drawn with a fallback font. Every figure drawn after the call,
    including one that was already drawn before it, uses the new fonts for both
    text and mathtext.

    Args:
        paths (StrPath): Paths to font files to register.

    Examples:
        >>> add_custom_fonts("/path/to/Arial.ttf", "/path/to/Arial Bold.ttf")  # doctest: +SKIP
    """
    for path in paths:
        fm.fontManager.addfont(path)
    _clear_font_caches()


def _clear_font_caches() -> None:
    """Forget Matplotlib's cached font choices so newly added fonts are used.

    Several Matplotlib caches are keyed by font *properties* (family, weight, ...)
    rather than by the font file they resolved to, so they keep returning the old
    font after a new one is registered. These are private APIs, so each one is
    looked up defensively and skipped if a Matplotlib version does not have it.
    """
    caches = (
        # findfont() results; FontManager.addfont() clears this in recent versions.
        getattr(fm.fontManager, "_findfont_cached", None),
        # Parsed mathtext, with the fonts it resolved baked in. A renderer (and its
        # parser) is reused when the same figure is drawn again.
        getattr(MathTextParser, "_parse_cached", None),
        # Text extents used for layout (older Matplotlib versions).
        getattr(mtext, "_get_text_metrics_with_cache_impl", None),
    )
    for cache in caches:
        cache_clear = getattr(cache, "cache_clear", None)
        if callable(cache_clear):
            cache_clear()

    # Text extents used for layout (newer Matplotlib versions keep one cache per
    # renderer in a mutable default argument).
    metrics_function = getattr(mtext, "_get_text_metrics_function", None)
    for default in getattr(metrics_function, "__defaults__", None) or ():
        if isinstance(default, MutableMapping):
            default.clear()


def auto_ticks(
    ax: Axes,
    *,
    left: float | None = None,
    right: float | None = None,
    top: float | None = None,
    bottom: float | None = None,
) -> None:
    """Give both axes of a plot Prism-like ticks.

    How each axis is handled depends on its data and scale:

    - **Linear numeric axes** get about six major ticks, spaced 1, 2, 2.5 or 5 times a
      power of 10. Minor ticks split each major interval into halves with six or more
      visible major ticks, quarters with five (fifths if the spacing is 2.5 or 5, so minor
      ticks stay on round values), and fifths with four or fewer. Each limit left unset
      moves out to a major tick, so the axis starts and ends on a labelled tick. Inverted
      axes stay inverted.
    - **Categorical axes** (string data, as in ``ax.bar(["A", "B"], ...)``) keep one tick
      per category and lose their minor ticks.
    - **Other axes** (log and other non-linear scales, dates, other units) keep
      Matplotlib's own ticks and limits.

    A limit you pass is applied on every kind of axis.

    Args:
        ax: The axes to set ticks for.
        left: Value at the left edge of the x-axis. If None, it moves to a major tick.
        right: Value at the right edge of the x-axis. If None, it moves to a major tick.
        top: Value at the top edge of the y-axis. If None, it moves to a major tick.
        bottom: Value at the bottom edge of the y-axis. If None, it moves to a major tick.

    Notes:
        Call this after plotting, because it works from the limits the data produce.
        The limits mean the same as in ``ax.set_xlim(left, right)`` and
        ``ax.set_ylim(bottom, top)``: on an inverted y-axis, ``bottom`` is the larger value.
    """
    _auto_axis_ticks(ax.xaxis, ax.set_xlim, left, right)
    _auto_axis_ticks(ax.yaxis, ax.set_ylim, bottom, top)


# Major tick spacings, times a power of 10. These are the steps of Matplotlib's default
# AutoLocator; MaxNLocator's own default also allows 1.5, 3, 4, 6 and 8 (ticks like 0, 1.5, 3).
_MAJOR_STEPS = (1, 2, 2.5, 5, 10)

# Snapping a limit out to a tick can make MaxNLocator pick a larger step, which moves the
# outermost ticks again. Each round only widens the range, so this settles within a few rounds.
_MAX_SNAP_ROUNDS = 10


def _auto_axis_ticks(
    axis: Axis,
    set_lim: Callable[[float | None, float | None], object],
    start: float | None,
    end: float | None,
) -> None:
    """Apply :func:`auto_ticks` to one axis.

    Args:
        axis: The axis to set ticks for.
        set_lim: ``ax.set_xlim`` or ``ax.set_ylim``, taking the (start, end) limits.
        start: Fixed limit at the start (left or bottom) edge, or None to snap it to a tick.
        end: Fixed limit at the end (right or top) edge, or None to snap it to a tick.
    """
    if start is not None or end is not None:
        set_lim(start, end)

    converter = _get_converter(axis)
    if isinstance(converter, StrCategoryConverter):
        axis.set_minor_locator(ticker.NullLocator())
        return
    if converter is not None or axis.get_scale() != "linear":
        return

    axis.set_major_locator(ticker.MaxNLocator(nbins=6, steps=_MAJOR_STEPS, min_n_ticks=3))
    for _ in range(_MAX_SNAP_ROUNDS):
        # Ticks are ascending; on an inverted axis the start edge holds the larger value.
        ticks = axis.get_majorticklocs()
        view_start, view_end = axis.get_view_interval()
        inverted = view_start > view_end
        start_tick, end_tick = (ticks[-1], ticks[0]) if inverted else (ticks[0], ticks[-1])
        new_start = view_start if start is not None else float(start_tick)
        new_end = view_end if end is not None else float(end_tick)
        if new_start == view_start and new_end == view_end:
            break
        set_lim(new_start, new_end)

    axis.set_minor_locator(ticker.AutoMinorLocator(_minor_divisions(axis)))


def _minor_divisions(axis: Axis) -> int:
    """Return how many parts minor ticks split each major interval into.

    Fewer visible major ticks get more minor ticks: halves with six or more, quarters with
    five, and fifths with four or fewer. Quarters and fifths are swapped where needed so that
    minor ticks land on round values: a major spacing of 2.5 or 5 (times a power of 10) is
    split into fifths (every 1, not 1.25, between 0 and 5) and a spacing of 2 into quarters
    (every 0.5, not 0.4, between 0 and 2).
    """
    low, high = sorted(axis.get_view_interval())
    ticks = np.asarray(axis.get_majorticklocs())
    tol = 1e-9 * (high - low)
    n_visible = int(np.count_nonzero((ticks >= low - tol) & (ticks <= high + tol)))
    if n_visible >= 6:
        return 2
    preferred = 4 if n_visible == 5 else 5
    if len(ticks) < 2:
        return preferred
    step = float(ticks[1] - ticks[0])
    mantissa = step / 10 ** math.floor(math.log10(step))
    if any(math.isclose(mantissa, m, rel_tol=1e-6) for m in (2.5, 5)):
        return 5
    if math.isclose(mantissa, 2, rel_tol=1e-6):
        return 4
    return preferred


def _get_converter(axis: Axis) -> object:
    """Return the axis' unit converter, or None for plain numbers.

    ``Axis.get_converter()`` is new in Matplotlib 3.10, which deprecated ``Axis.converter``.
    """
    get_converter = getattr(axis, "get_converter", None)
    if callable(get_converter):
        return get_converter()
    return getattr(axis, "converter", None)
