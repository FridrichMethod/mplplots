"""Figure sizes and multi-panel layouts given in inches.

Every dimension here is physical: column widths, axis lengths, margins and gaps are inches, so a
figure keeps its proportions and its text size whatever the dpi. ``grid_inches`` lays out a grid
of panels with :func:`~mplplots.utils.add_axes_inches`, and ``add_shared_ylabel`` and
``align_legends_left`` finish a layout once the panels are drawn.

The inch helpers of :mod:`mplplots.utils` (``add_axes_inches``, ``legend_inches``,
``suptitle_inches`` and ``LegendCorner``) are importable from here as well.
"""

import math
from collections.abc import Mapping, Sequence
from numbers import Real
from types import MappingProxyType
from typing import Any, Literal

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Text

from mplplots.utils import LegendCorner, add_axes_inches, legend_inches, suptitle_inches

__all__ = [
    "COLUMN_WIDTHS",
    "ColumnWidth",
    "LegendCorner",
    "add_axes_inches",
    "add_shared_ylabel",
    "align_legends_left",
    "figure_size",
    "grid_inches",
    "legend_inches",
    "suptitle_inches",
]

# A journal column-width preset.
type ColumnWidth = Literal["single", "onehalf", "double"]

COLUMN_WIDTHS: Mapping[ColumnWidth, float] = MappingProxyType({
    "single": 3.5,
    "onehalf": 5.0,
    "double": 7.0,
})
"""The width of each column preset, in inches."""

# Height / width of a figure_size() figure when neither height nor aspect is given.
_DEFAULT_ASPECT = 0.7

# Derived inch lengths (sums and products) are rounded to this many decimals, so that sizes
# such as 0.6 + 2 + 2 + 2 + 0.6 + 0.6 + 0.1 and 3.5 * 0.7 come out as 7.9 in and 2.45 in, not
# 7.899999999999999 in and 2.4499999999999997 in, which Agg truncates to one pixel less than
# the figure's size at 600 dpi.
_INCH_DECIMALS = 9


def figure_size(
    width: ColumnWidth | float = "single",
    *,
    height: float | None = None,
    aspect: float | None = None,
) -> tuple[float, float]:
    """Return ``(width, height)`` in inches for a column preset or a width in inches.

    Args:
        width: A column preset from ``COLUMN_WIDTHS`` (``"single"`` 3.5 in, ``"onehalf"``
            5.0 in, ``"double"`` 7.0 in) or a width in inches.
        height: The height in inches. It wins over ``aspect`` when both are given.
        aspect: The height as a fraction of the width; 0.7 when neither ``height`` nor
            ``aspect`` is given.

    Returns:
        The figure size in inches, ready for ``plt.figure(figsize=...)``.

    Raises:
        ValueError: If ``width`` is an unknown preset, or a width, height or aspect is not
            positive.

    Examples:
        >>> figure_size("double", aspect=0.5)
        (7.0, 3.5)
        >>> figure_size(4.0, height=2.0)
        (4.0, 2.0)
    """
    if isinstance(width, str):
        if width not in COLUMN_WIDTHS:
            raise ValueError(
                f"unknown column width {width!r}; choose from {', '.join(COLUMN_WIDTHS)}"
            )
        width_in = COLUMN_WIDTHS[width]
    else:
        width_in = float(width)
    for name, value in (("width", width_in), ("height", height), ("aspect", aspect)):
        if value is not None and not value > 0:
            raise ValueError(f"{name} must be positive, got {value}")
    if height is not None:
        return width_in, float(height)
    aspect_value = _DEFAULT_ASPECT if aspect is None else float(aspect)
    return width_in, round(width_in * aspect_value, _INCH_DECIMALS)


def grid_inches(
    nrows: int = 1,
    ncols: int = 1,
    *,
    width: float | Sequence[float],
    height: float | Sequence[float],
    left: float = 0.6,
    right: float = 0.2,
    top: float = 0.1,
    bottom: float = 0.4,
    wspace: float | Sequence[float] = 0.6,
    hspace: float | Sequence[float] = 0.5,
    sharex: bool = False,
    sharey: bool = False,
    **figure_kwargs: Any,
) -> tuple[Figure, list[Axes]]:
    """Make a figure with an ``nrows`` by ``ncols`` grid of axes laid out in inches.

    Every dimension is given in inches and the figure size follows from them::

        figure width  = left + sum(width) + sum(wspace) + right
        figure height = top + sum(height) + sum(hspace) + bottom

    Each panel is placed with :func:`~mplplots.utils.add_axes_inches`, so its axis lengths stay
    the same when the figure is resized and at any dpi.

    Args:
        nrows: Number of rows of panels.
        ncols: Number of columns of panels.
        width: Length of the x-axis of each column, left to right, in inches. A number applies
            to every column.
        height: Length of the y-axis of each row, top to bottom, in inches. A number applies to
            every row.
        left: Distance from the figure's left edge to the first column's y-axis, in inches.
        right: Distance from the last column's right edge to the figure's right edge, in inches.
            The default holds the label of a tick at the end of the x-axis, which overhangs the
            axes by half its width, up to six characters of 8 pt text.
        top: Distance from the figure's top edge to the first row's top edge, in inches.
        bottom: Distance from the last row's x-axis to the figure's bottom edge, in inches.
        wspace: Gap between adjacent columns, in inches: one number for every gap, or
            ``ncols - 1`` numbers, left to right.
        hspace: Gap between adjacent rows, in inches: one number for every gap, or
            ``nrows - 1`` numbers, top to bottom.
        sharex: Share the x-axis across all panels and show x tick labels on the bottom row
            only, as ``plt.subplots(sharex=True)`` does.
        sharey: Share the y-axis across all panels and show y tick labels in the left column
            only, as ``plt.subplots(sharey=True)`` does.
        **figure_kwargs: Passed on to ``plt.figure``, e.g. ``num`` or ``facecolor``.

    Returns:
        The figure and its axes as a flat list in row-major order, top row first.

    Raises:
        ValueError: If ``nrows`` or ``ncols`` is below 1, an axis length is not positive, a
            margin or gap is negative, or a sequence has the wrong length.

    Examples:
        Three stacked panels sharing a 5.1 in x-axis, each with a 0.8 in y-axis and 0.2 in
        between, in a 5.9 by 3.3 in figure:

        >>> fig, axes = grid_inches(3, 1, width=5.1, height=0.8, hspace=0.2, sharex=True)
        >>> tuple(float(size) for size in fig.get_size_inches())
        (5.9, 3.3)
    """
    if nrows < 1 or ncols < 1:
        raise ValueError(f"nrows and ncols must be at least 1, got {nrows} and {ncols}")
    widths = _per_slot("width", width, ncols)
    heights = _per_slot("height", height, nrows)
    wspaces = _per_slot("wspace", wspace, ncols - 1)
    hspaces = _per_slot("hspace", hspace, nrows - 1)
    for name, lengths in (("width", widths), ("height", heights)):
        if not all(length > 0 for length in lengths):
            raise ValueError(f"every {name} must be positive, got {lengths}")
    margins = {"left": [left], "right": [right], "top": [top], "bottom": [bottom]}
    for name, gaps in {**margins, "wspace": wspaces, "hspace": hspaces}.items():
        if not all(gap >= 0 for gap in gaps):
            raise ValueError(f"{name} must not be negative, got {gaps}")

    fig_width = _inch_sum([left, *widths, *wspaces, right])
    fig_height = _inch_sum([top, *heights, *hspaces, bottom])
    # Column j starts after the left margin, j columns and j gaps; row i (from the top) sits
    # above the bottom margin, the rows below it and the gaps below it.
    lefts = [_inch_sum([left, *widths[:j], *wspaces[:j]]) for j in range(ncols)]
    bottoms = [_inch_sum([bottom, *heights[i + 1 :], *hspaces[i:]]) for i in range(nrows)]

    # Imported here, so that importing mplplots leaves pyplot and its backend alone.
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(fig_width, fig_height), **figure_kwargs)
    axes: list[Axes] = []
    for i in range(nrows):
        for j in range(ncols):
            share: dict[str, Axes] = {}
            if axes and sharex:
                share["sharex"] = axes[0]
            if axes and sharey:
                share["sharey"] = axes[0]
            ax = add_axes_inches(fig, lefts[j], bottoms[i], widths[j], heights[i], **share)
            if sharex and i < nrows - 1:
                ax.tick_params(axis="x", which="both", labelbottom=False)
                ax.xaxis.get_offset_text().set_visible(False)
            if sharey and j > 0:
                ax.tick_params(axis="y", which="both", labelleft=False)
                ax.yaxis.get_offset_text().set_visible(False)
            axes.append(ax)
    return fig, axes


def _per_slot(name: str, value: float | Sequence[float], count: int) -> list[float]:
    """Return one length per slot: a number repeated ``count`` times, or a sequence as floats.

    Raises:
        ValueError: If ``value`` is a sequence whose length is not ``count``.
    """
    if isinstance(value, (int, float, Real)):
        return [float(value)] * count
    values = [float(item) for item in value]
    if len(values) != count:
        raise ValueError(f"{name} needs {count} values, got {len(values)}")
    return values


def _inch_sum(lengths: Sequence[float]) -> float:
    """Return the sum of lengths in inches, without accumulated rounding error."""
    return round(math.fsum(lengths), _INCH_DECIMALS)


def add_shared_ylabel(fig: Figure, axes: Sequence[Axes], text: str, **kwargs: Any) -> Text:
    """Add one y label for a stack or grid of panels, at the standard label gap.

    Use this instead of ``fig.supylabel(..., x=<guess>)``: a hard-coded figure x puts the label
    a different distance from the ticks in every figure, because tick labels differ in width.
    This measures the panels' leftmost ink (their tick labels, since the panels carry no y label
    of their own) and puts the label's right edge ``rcParams["axes.labelpad"]`` points to the
    left of it, the gap Matplotlib gives an ordinary ``ax.set_ylabel``. The label is rotated
    90 degrees and centred on the vertical span of ``axes``.

    The label is placed by drawing the figure, so call this after the panels are populated and
    the layout is final.

    Args:
        fig: The figure that holds the panels.
        axes: The panels the label belongs to.
        text: The label text.
        **kwargs: Passed on to ``fig.text``, e.g. ``color``.

    Returns:
        The label.

    Raises:
        ValueError: If none of ``axes`` is drawn, so there is nothing to measure.

    Examples:
        >>> fig, axes = grid_inches(3, 1, width=3.0, height=0.8, hspace=0.2, sharex=True)
        >>> label = add_shared_ylabel(fig, axes, "Signal")
    """
    fig.draw_without_rendering()
    # Leftmost ink of the panel block and its vertical centre.
    boxes = [box for ax in axes if (box := ax.get_tightbbox()) is not None]
    if not boxes:
        raise ValueError("add_shared_ylabel: no drawable axes to measure")
    left_px = min(box.x0 for box in boxes)
    positions = [ax.get_position() for ax in axes]
    y_centre = 0.5 * (min(pos.y0 for pos in positions) + max(pos.y1 for pos in positions))

    label = fig.text(
        0.0,
        y_centre,
        text,
        rotation=90,
        ha="left",
        va="center",
        fontsize=kwargs.pop("fontsize", mpl.rcParams["axes.labelsize"]),
        **kwargs,
    )
    # Second pass: shift the label so its right edge sits labelpad points left of the ink. The
    # anchor of rotated text is hard to predict, so the drawn extent is measured instead.
    fig.draw_without_rendering()
    pad_px = mpl.rcParams["axes.labelpad"] * fig.dpi / 72.0
    right_px = label.get_window_extent().x1
    dx_px = (left_px - pad_px) - right_px
    label.set_x(label.get_position()[0] + dx_px / (fig.get_figwidth() * fig.dpi))
    return label


def align_legends_left(axes: Sequence[Axes], *, right: float = 0.985, y: float = 0.97) -> float:
    """Give every panel legend in ``axes`` the same left edge, and return that edge.

    Legends whose entries differ in width line up on the right but are ragged on the left under
    ``loc="upper right"``. This measures the widest legend and anchors every legend's upper-left
    corner at ``(right - widest, y)`` in axes coordinates, so their left edges line up and the
    widest one still ends at ``right``.

    Call this after all panels and legends are populated. Axes without a legend are skipped.

    Args:
        axes: The panels whose legends to align.
        right: Where the widest legend ends, as a fraction of the axes width.
        y: Where the legends' top edges sit, as a fraction of the axes height.

    Returns:
        The common left edge as a fraction of the axes width, or NaN if no axes has a legend.

    Examples:
        >>> fig, axes = grid_inches(2, 1, width=3.0, height=1.0)
        >>> for ax, name in zip(axes, ["short", "a longer label"]):
        ...     _ = ax.plot([0, 1], [0, 1], label=name)
        ...     _ = ax.legend()
        >>> x0 = align_legends_left(axes)
    """
    drawable = [(ax, legend) for ax in axes if (legend := ax.get_legend()) is not None]
    if not drawable:
        return float("nan")
    fig = _root_figure(drawable[0][0])
    fig.draw_without_rendering()
    widest = max(
        legend.get_window_extent().transformed(ax.transAxes.inverted()).width
        for ax, legend in drawable
    )
    x0 = right - widest
    for ax, legend in drawable:
        legend.set_loc("upper left")
        legend.set_bbox_to_anchor((x0, y), transform=ax.transAxes)
    return x0


def _root_figure(ax: Axes) -> Figure:
    """Return the top-level figure that holds ax, also when ax is in a nested subfigure.

    ``ax.figure`` is the figure or subfigure that holds ``ax``, and the ``figure`` of either is
    the top-level figure on every supported Matplotlib version. ``SubFigure.get_figure()``
    without ``root`` would warn on Matplotlib 3.10 and 3.11 for a nested subfigure.
    """
    return ax.figure.figure
