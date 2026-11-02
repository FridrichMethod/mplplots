"""Utility functions for mplplots."""

import os
from collections.abc import MutableMapping

import matplotlib.font_manager as fm
import matplotlib.text as mtext
from matplotlib import ticker
from matplotlib.axes import Axes
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


def auto_ticks(  # noqa: C901
    ax: Axes,
    *,
    left: float | None = None,
    right: float | None = None,
    top: float | None = None,
    bottom: float | None = None,
) -> None:
    """Set the major and minor ticks of an axis automatically.

    Args:
        ax (Axes): The axis to set ticks for.
        left (float | None, optional): The left limit of the x-axis. Defaults to None.
        right (float | None, optional): The right limit of the x-axis. Defaults to None.
        bottom (float | None, optional): The bottom limit of the y-axis. Defaults to None.
        top (float | None, optional): The top limit of the y-axis. Defaults to None.

    Notes:
        Put this function after the data are passed to the axis.
    """
    # Set the major and minor ticks of the x-axis
    if left is not None:
        ax.set_xlim(left=left)
    if right is not None:
        ax.set_xlim(right=right)

    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6, min_n_ticks=3))
    x_tick_num = len(ax.get_xticks())
    if x_tick_num >= 6:
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    elif x_tick_num >= 5:
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    else:
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    # For viewing incomplete ticks
    if left is None and (ax.get_xticks()[0] != ax.get_xlim()[0]):
        ax.set_xlim(left=ax.get_xticks()[0])
    if right is None and (ax.get_xticks()[-1] != ax.get_xlim()[-1]):
        ax.set_xlim(right=ax.get_xticks()[-1])

    # Set the major and minor ticks of the y-axis
    if bottom is not None:
        ax.set_ylim(bottom=bottom)
    if top is not None:
        ax.set_ylim(top=top)

    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=6, min_n_ticks=3))
    y_tick_num = len(ax.get_yticks())
    if y_tick_num >= 6:
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    elif y_tick_num >= 5:
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    else:
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))

    # For viewing incomplete ticks
    if bottom is None and (ax.get_yticks()[0] != ax.get_ylim()[0]):
        ax.set_ylim(bottom=ax.get_yticks()[0])
    if top is None and (ax.get_yticks()[-1] != ax.get_ylim()[-1]):
        ax.set_ylim(top=ax.get_yticks()[-1])
