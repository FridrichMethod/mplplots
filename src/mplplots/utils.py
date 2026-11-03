"""Utility functions for mplplots."""

import math
import os
from collections.abc import Callable, MutableMapping

import matplotlib.font_manager as fm
import matplotlib.text as mtext
import numpy as np
import numpy.typing as npt
from matplotlib import ticker
from matplotlib.axes import Axes
from matplotlib.axis import Axis
from matplotlib.category import StrCategoryConverter
from matplotlib.mathtext import MathTextParser
from matplotlib.transforms import Transform

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
    """Give both axes of a plot Prism-like ticks, ending each axis on a major tick.

    How each axis is handled depends on its data and scale:

    - **Linear numeric axes** get about six major ticks, spaced 1, 2, 2.5 or 5 times a
      power of 10. Minor ticks split each major interval into halves with six or more
      visible major ticks, quarters with five (fifths if the spacing is 2.5 or 5, so minor
      ticks stay on round values), and fifths with four or fewer.
    - **Log and other non-linear scales, dates and other units** keep Matplotlib's own
      ticks.
    - **Categorical axes** (string data, as in ``ax.bar(["A", "B"], ...)``) keep one tick
      per category and lose their minor ticks. Their limits are not changed.

    On every axis except categorical ones, each limit left unset moves out to the nearest
    major tick, so the axis starts and ends on a tick. A limit you pass is kept as given. On
    a linear axis the tick spacing is then chosen so that this limit is a major tick too
    (``right=7`` gives a tick every 1), if a round spacing with at most 10 intervals allows
    it; otherwise that end stays between ticks (for example ``bottom=-1.2``). Inverted axes
    stay inverted.

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

# Major intervals wanted on a linear axis: MaxNLocator(nbins=6) gives up to 6. A spacing chosen
# to put a fixed limit on a tick may give up to _MAX_INTERVALS when no spacing gives 6 or fewer.
_NBINS = 6
_MAX_INTERVALS = 10

# Snapping a limit out to a tick can change the ticks (MaxNLocator may pick a larger step for
# the wider range), so snapping repeats until the ends sit on ticks.
_MAX_SNAP_ROUNDS = 10

# Times a view is widened while looking for a tick beyond one of its ends.
_MAX_PROBES = 5

type _SetLim = Callable[[float | None, float | None], object]


def _auto_axis_ticks(axis: Axis, set_lim: _SetLim, start: float | None, end: float | None) -> None:
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
        _snap_ends(axis, set_lim, start, end)
        return

    # Each pass only widens the axis. Repeating until nothing changes makes the result a fixed
    # point, so calling auto_ticks again leaves the axis as it is.
    for _ in range(_MAX_SNAP_ROUNDS):
        view = _view_interval(axis)
        _set_linear_ticks(axis, set_lim, start, end)
        if _view_interval(axis) == view:
            break
    axis.set_minor_locator(ticker.AutoMinorLocator(_minor_divisions(axis)))


def _set_linear_ticks(axis: Axis, set_lim: _SetLim, start: float | None, end: float | None) -> None:
    """Set the major locator of a linear numeric axis and snap its unset ends to ticks.

    With a fixed limit, the spacing is chosen so that the limit is a tick. If no round
    spacing does that, the default ticks are used and the fixed end stays between ticks.
    """
    step = None
    if start is not None or end is not None:
        step = _step_through_fixed_ends(_view_interval(axis), start, end)
    if step is None:
        locator: ticker.Locator = ticker.MaxNLocator(
            nbins=_NBINS, steps=_MAJOR_STEPS, min_n_ticks=3
        )
    else:
        locator = ticker.MultipleLocator(step)
    axis.set_major_locator(locator)
    _snap_ends(axis, set_lim, start, end)


def _view_interval(axis: Axis) -> tuple[float, float]:
    """Return the axis' (start, end) view limits; start > end on an inverted axis."""
    view_start, view_end = axis.get_view_interval()
    return float(view_start), float(view_end)


def _snap_ends(axis: Axis, set_lim: _SetLim, start: float | None, end: float | None) -> None:
    """Move each unset end of the axis out to the nearest major tick at or beyond it.

    If the ends do not settle on ticks, the limits are left as they were.
    """
    if start is not None and end is not None:
        return
    before = _view_interval(axis)
    for _ in range(_MAX_SNAP_ROUNDS):
        view_start, view_end = _view_interval(axis)
        tick_start, tick_end = _outer_ticks(axis, view_start, view_end)
        new_start = view_start if start is not None or tick_start is None else tick_start
        new_end = view_end if end is not None or tick_end is None else tick_end
        if new_start == view_start and new_end == view_end:
            return
        set_lim(new_start, new_end)
    set_lim(*before)


def _outer_ticks(
    axis: Axis, view_start: float, view_end: float
) -> tuple[float | None, float | None]:
    """Return where each (start, end) end of the view should move to reach a major tick.

    An end that is already on one of the view's ticks (up to rounding error) is returned
    unchanged. Otherwise the nearest tick beyond it is returned, or None if none is found.
    """
    transform = axis.get_transform()
    low, high = sorted((view_start, view_end))
    t_low, t_high = (float(v) for v in transform.transform(np.array([low, high])))
    tol = 1e-9 * (t_high - t_low)

    # Whether an end is on a tick is decided by the ticks of the view itself.
    ticks, scaled = _scaled_major_ticks(axis, transform, low, high)
    tick_low = low if np.any(np.abs(scaled - t_low) <= tol) else None
    tick_high = high if np.any(np.abs(scaled - t_high) <= tol) else None

    # Otherwise look for the nearest tick beyond the end. MaxNLocator and LogLocator return
    # ticks beyond the view; other locators (the date locators, for example) do not, so
    # widen the view by a tick spacing at a time and ask again.
    probe_low, probe_high = t_low, t_high
    for _ in range(_MAX_PROBES):
        if tick_low is None and np.any(below := scaled < t_low - tol):
            tick_low = float(ticks[int(np.argmax(np.where(below, scaled, -np.inf)))])
        if tick_high is None and np.any(above := scaled > t_high + tol):
            tick_high = float(ticks[int(np.argmin(np.where(above, scaled, np.inf)))])
        if tick_low is not None and tick_high is not None:
            break
        spacing = float(np.max(np.diff(np.sort(scaled)))) if scaled.size >= 2 else t_high - t_low
        probe_low, probe_high = probe_low - spacing, probe_high + spacing
        wider = transform.inverted().transform(np.array([probe_low, probe_high]))
        ticks, scaled = _scaled_major_ticks(axis, transform, float(wider[0]), float(wider[1]))
    if view_start > view_end:
        return tick_high, tick_low
    return tick_low, tick_high


def _scaled_major_ticks(
    axis: Axis, transform: Transform, low: float, high: float
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Return the major ticks for a view of (low, high), and the same ticks in scale space."""
    ticks = _major_ticks_for_view(axis, low, high)
    scaled = np.asarray(transform.transform(ticks), dtype=float)
    finite = np.isfinite(scaled)
    return ticks[finite], scaled[finite]


def _major_ticks_for_view(axis: Axis, low: float, high: float) -> npt.NDArray[np.float64]:
    """Return the major tick locations the axis' locator gives for a view of (low, high)."""
    saved = _view_interval(axis)
    axis.set_view_interval(low, high, ignore=True)
    try:
        return np.asarray(axis.get_majorticklocs(), dtype=float)
    finally:
        axis.set_view_interval(*saved, ignore=True)


def _step_through_fixed_ends(
    view: tuple[float, float], start: float | None, end: float | None
) -> float | None:
    """Return a round tick spacing that puts every fixed end on a tick, or None.

    The spacing is 1, 2, 2.5 or 5 times a power of 10. Unset ends move out to a multiple of
    it, and the axis must get 2 to ``_MAX_INTERVALS`` major intervals. Like MaxNLocator, the
    smallest spacing with at most ``_NBINS`` intervals wins; if every spacing gives more,
    the one with the fewest intervals wins.
    """
    view_start, view_end = view
    inverted = view_start > view_end
    low, high = sorted(view)
    low_fixed = (end if inverted else start) is not None
    high_fixed = (start if inverted else end) is not None
    span = high - low
    if span <= 0:
        return None
    best: float | None = None
    best_key: tuple[bool, int, float] | None = None
    first_exponent = math.floor(math.log10(span / _MAX_INTERVALS)) - 1
    for exponent in range(first_exponent, math.ceil(math.log10(span)) + 1):
        for mantissa in _MAJOR_STEPS[:-1]:
            step = mantissa * 10.0**exponent
            if (low_fixed and not _is_multiple(low, step)) or (
                high_fixed and not _is_multiple(high, step)
            ):
                continue
            lo = low if low_fixed else math.floor(low / step + 1e-9) * step
            hi = high if high_fixed else math.ceil(high / step - 1e-9) * step
            n_intervals = round((hi - lo) / step)
            if not 2 <= n_intervals <= _MAX_INTERVALS:
                continue
            key = (n_intervals > _NBINS, abs(n_intervals - _NBINS), -step)
            if best_key is None or key < best_key:
                best, best_key = step, key
    return best


def _is_multiple(value: float, step: float) -> bool:
    """Whether value is a whole multiple of step, up to rounding error."""
    k = value / step
    return abs(k - round(k)) <= 1e-9 * max(1.0, abs(k))


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
