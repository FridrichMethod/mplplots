"""Plot primitives that each draw one element of the style.

- ``plot_mean_sem`` draws a mean curve in the edge colour over a ``mean ± sem`` band in the fill
  colour.
- ``plot_distribution`` draws pre-binned counts as a filled curve through the bin centres, in
  percent of samples per bin.
- ``significance_stars`` maps a p or q value to its significance label.
- ``box_axes`` frames a panel with all four spines, the explicit exception to the open axes of
  the style.
"""

import math

import matplotlib as mpl
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.typing import ColorType, LineStyleType
from numpy.typing import ArrayLike, NDArray

from mplplots.colors import BAND_ALPHA, LINE_ALPHA

__all__ = ["box_axes", "plot_distribution", "plot_mean_sem", "significance_stars"]


def _as_float(values: ArrayLike) -> NDArray[np.float64]:
    """Convert values to a float64 array in which masked entries are NaN.

    Matplotlib leaves NaN points out of curves and fills, as it does masked ones.

    Args:
        values: The values, as a sequence, an array or a masked array.

    Returns:
        A plain float64 array.
    """
    return np.asarray(np.ma.filled(np.ma.asarray(values, dtype=np.float64), np.nan))


def significance_stars(p: float) -> str:
    """Map a p or q value to its significance label.

    For a comparison within a family, pass the multiplicity-corrected value.

    Args:
        p: The p or q value.

    Returns:
        ``"***"`` below 0.001, ``"**"`` below 0.01, ``"*"`` below 0.05, and ``"n.s."``
        otherwise, including for a non-finite value.

    Examples:
        >>> significance_stars(0.003)
        '**'
        >>> significance_stars(float("nan"))
        'n.s.'
    """
    if not math.isfinite(p):
        return "n.s."
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "n.s."


def plot_mean_sem(
    ax: Axes,
    x: ArrayLike,
    mean: ArrayLike,
    sem: ArrayLike,
    *,
    fill: ColorType,
    edge: ColorType,
    label: str | None = None,
    linewidth: float = 1.2,
    linestyle: LineStyleType = "-",
    band_alpha: float = BAND_ALPHA,
    line_alpha: float = LINE_ALPHA,
    zorder: float = 3.0,
) -> Line2D:
    """Draw a mean curve over a ``mean ± sem`` band.

    The band is borderless, in the fill colour, at ``zorder``; the curve is in the edge colour,
    which carries the series' identity, at ``zorder + 1``. A second variable within one hue
    takes another line style, such as ``SECONDARY_LINESTYLE``, rather than another colour.
    Points masked in any input are left out of the band and the curve.

    Args:
        ax: The axes to draw on.
        x: The x values.
        mean: The mean at each x value.
        sem: The standard error of the mean at each x value.
        fill: The band colour.
        edge: The curve colour.
        label: The legend label of the curve; ``None`` leaves the curve out of the legend.
        linewidth: The curve width in points.
        linestyle: The curve style.
        band_alpha: The band opacity.
        line_alpha: The curve opacity.
        zorder: The drawing order of the band; the curve is drawn at ``zorder + 1``.

    Returns:
        The mean curve.
    """
    x_values = _as_float(x)
    mean_values = _as_float(mean)
    sem_values = _as_float(sem)
    ax.fill_between(
        x_values,
        mean_values - sem_values,
        mean_values + sem_values,
        facecolor=fill,
        edgecolor="none",
        alpha=band_alpha,
        zorder=zorder,
    )
    (line,) = ax.plot(
        x_values,
        mean_values,
        color=edge,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=line_alpha,
        label=label,
        zorder=zorder + 1,
    )
    return line


def plot_distribution(
    ax: Axes,
    edges: ArrayLike,
    counts: ArrayLike,
    n_total: int,
    *,
    fill: ColorType,
    edge: ColorType,
    alpha: float = BAND_ALPHA,
    linewidth: float = 1.0,
    zorder: float = 2.0,
) -> Patch:
    """Draw a pre-binned distribution as a filled curve through the bin centres.

    The y value of each bin is ``100 * counts / n_total``, the percent of all samples that fall
    in the bin, so series with different sample counts stay comparable on a shared bin grid.
    The counts are plotted at the bin centres as they are, without a staircase and without
    smoothing, so peak heights stay those of the histogram. Peak heights depend on the bin
    width, so the caption names the bin width and the denominator.

    The fill reaches down to zero and carries ``alpha`` on its face only; the curve stays
    opaque and is drawn just above its fill. Masked counts and edges leave a gap.

    Args:
        ax: The axes to draw on.
        edges: The bin edges, one more than ``counts``.
        counts: The number of samples in each bin.
        n_total: The total number of samples the histogram was built from, including any that
            fall outside the binned range.
        fill: The colour of the wash under the curve.
        edge: The curve colour.
        alpha: The opacity of the wash.
        linewidth: The curve width in points.
        zorder: The drawing order of the wash; the curve is drawn just above it.

    Returns:
        A legend proxy with the face, edge and line width of the drawn distribution.

    Raises:
        ValueError: If ``edges`` is not one longer than ``counts`` or ``n_total`` is not
            positive.
    """
    edge_values = _as_float(edges)
    count_values = _as_float(counts)
    if edge_values.size != count_values.size + 1:
        raise ValueError(
            f"edges must be one longer than counts, got {edge_values.size} edges"
            f" for {count_values.size} counts"
        )
    if n_total <= 0:
        raise ValueError(f"n_total must be positive, got {n_total}")
    centres = 0.5 * (edge_values[:-1] + edge_values[1:])
    percent = 100.0 * count_values / float(n_total)
    face = mcolors.to_rgba(fill, alpha)
    ax.fill_between(centres, percent, facecolor=face, linewidth=0, zorder=zorder)
    ax.plot(centres, percent, color=edge, linewidth=linewidth, zorder=zorder + 0.1)
    return Patch(facecolor=face, edgecolor=edge, linewidth=linewidth)


def box_axes(ax: Axes, *, linewidth: float | None = None) -> None:
    """Frame a panel with all four spines and keep its ticks on the left and bottom.

    The style hides the top and right spines; use this only for a panel that is meant to be
    boxed.

    Args:
        ax: The axes to frame.
        linewidth: The spine width in points; ``None`` uses ``rcParams["axes.linewidth"]``.
    """
    width = mpl.rcParams["axes.linewidth"] if linewidth is None else linewidth
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(width)
    ax.tick_params(which="both", top=False, right=False)
