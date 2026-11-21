"""Shared setup for the example scripts: the style names, the Arial check and saving.

Every figure is laid out in round inches with ``mplplots.grid_inches`` or
``mplplots.add_axes_inches``, ``legend_inches`` and ``suptitle_inches``: the figure size, the
position and size of each axes, and the anchors of legends and figure titles lie on a 0.05 in
grid, mostly on multiples of 0.1, 0.25, 0.5 or 1 in. ``save`` writes each figure through
``mplplots.save_figure``, uncropped and reproducibly, so the files keep that size, as PNG
(600 dpi), SVG and PDF.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from matplotlib import font_manager

import mplplots

if TYPE_CHECKING:
    from matplotlib.figure import Figure

PERSONAL = "mplplots.styles.Personal"
PRISM = "mplplots.styles.GraphPadPrism"
OUT = Path(__file__).resolve().parent
FORMATS = ("png", "svg", "pdf")
DPI = 600


def require_arial() -> None:
    """Exit unless Arial Regular and Arial Italic are installed.

    Without Arial the styles silently fall back to a look-alike font (Liberation Sans,
    ...), so the README images are never written in anything but Arial. Text uses the
    regular face and variables in math text (``$x$``) the italic one.
    """
    faces = {(f.name, f.style, f.weight) for f in font_manager.fontManager.ttflist}
    if not {("Arial", "normal", 400), ("Arial", "italic", 400)} <= faces:
        sys.exit(
            "Arial (regular and italic) is not installed; install it to regenerate the images."
        )


def save(fig: Figure, name: str) -> None:
    """Save fig uncropped as ``examples/<name>.png`` (600 dpi), ``.svg`` and ``.pdf``.

    Args:
        fig: The figure to save; it is closed afterwards.
        name: The file name without extension.
    """
    mplplots.save_figure(fig, OUT / name, formats=FORMATS, dpi=DPI)
