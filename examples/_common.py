"""Shared setup for the example scripts: Arial check, round-inch layout and saving.

Every figure is laid out in inches from its lower-left corner. The figure size, the
position and size of each axes, and the anchors of legends and figure titles are round
values: multiples of 0.1, 0.25, 0.5 or 1 in. Figures are saved uncropped, so the files
keep that size, as PNG (600 dpi), SVG and PDF.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import matplotlib.pyplot as plt
from matplotlib import font_manager

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.legend import Legend
    from matplotlib.text import Text
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

STYLE = "mplplots.styles.GraphPadPrism"
OUT = Path(__file__).resolve().parent
FORMATS = ("png", "svg", "pdf")
DPI = 600

# Without a fixed date and SVG id salt, every run would write different SVG and PDF files
# for the same figure.
_METADATA: dict[str, dict[str, Any]] = {"svg": {"Date": None}, "pdf": {"CreationDate": None}}
_SAVE_RC: dict[RcKeyType, Any] = {"savefig.bbox": "standard", "svg.hashsalt": "mplplots"}


def require_arial() -> None:
    """Exit unless Arial is installed.

    Without Arial the style silently falls back to a look-alike font (Liberation Sans,
    ...), so the README images are never written in anything but Arial.
    """
    faces = {(f.name, f.style, f.weight) for f in font_manager.fontManager.ttflist}
    if ("Arial", "normal", 400) not in faces:
        sys.exit("Arial is not installed; install it to regenerate the images.")


def add_axes(fig: Figure, left: float, bottom: float, width: float, height: float) -> Axes:
    """Add axes of width x height inches whose lower-left corner is at (left, bottom).

    Args:
        fig: The figure to add the axes to.
        left: Distance from the figure's left edge to the axes, in inches.
        bottom: Distance from the figure's bottom edge to the axes, in inches.
        width: Width of the axes (the x-axis length), in inches.
        height: Height of the axes (the y-axis length), in inches.

    Returns:
        The new axes.
    """
    fig_width, fig_height = fig.get_size_inches()
    rect = (left / fig_width, bottom / fig_height, width / fig_width, height / fig_height)
    return fig.add_axes(rect)


def legend(
    fig: Figure,
    ax: Axes,
    x: float,
    y: float,
    loc: Literal["upper left", "upper right", "lower left", "lower right"] = "upper left",
    **kwargs: Any,
) -> Legend:
    """Add a legend for ax with its loc corner at (x, y) inches on the figure.

    Args:
        fig: The figure that holds ax.
        ax: The axes whose labelled artists the legend lists.
        x: Distance from the figure's left edge to the legend's loc corner, in inches.
        y: Distance from the figure's bottom edge to the legend's loc corner, in inches.
        loc: Which corner of the legend sits at (x, y).
        **kwargs: Passed on to ``ax.legend``, e.g. ``ncols``.

    Returns:
        The new legend.
    """
    return ax.legend(
        loc=loc,
        bbox_to_anchor=(x, y),
        bbox_transform=fig.dpi_scale_trans,
        borderaxespad=0,
        **kwargs,
    )


def suptitle(fig: Figure, text: str, top: float = 0.1) -> Text:
    """Center a figure title with its top edge top inches below the figure's top edge.

    Args:
        fig: The figure to title.
        text: The title.
        top: Distance from the figure's top edge to the title's top edge, in inches.

    Returns:
        The title text.
    """
    return fig.suptitle(text, y=1 - top / fig.get_size_inches()[1], va="top")


def save(fig: Figure, name: str) -> None:
    """Save fig uncropped as ``examples/<name>.png`` (600 dpi), ``.svg`` and ``.pdf``.

    Args:
        fig: The figure to save; it is closed afterwards.
        name: The file name without extension.
    """
    with plt.rc_context(_SAVE_RC):
        for fmt in FORMATS:
            fig.savefig(OUT / f"{name}.{fmt}", dpi=DPI, metadata=_METADATA.get(fmt))
    plt.close(fig)
