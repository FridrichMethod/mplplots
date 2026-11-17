"""Shared setup for the example scripts: the Arial check and saving in three formats.

Every figure is laid out in round inches with ``mplplots.utils.add_axes_inches``,
``legend_inches`` and ``suptitle_inches``: the figure size, the position and size of
each axes, and the anchors of legends and figure titles are multiples of 0.1, 0.25, 0.5
or 1 in. ``save`` writes each figure uncropped, so the files keep that size, as PNG
(600 dpi), SVG and PDF.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from matplotlib import font_manager

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

STYLE = "mplplots.styles.GraphPadPrism"
OUT = Path(__file__).resolve().parent
FORMATS = ("png", "svg", "pdf")
DPI = 600

# Without a fixed date and SVG id salt, every run would write different SVG and PDF files
# for the same figure. "standard" keeps the files uncropped even if a matplotlibrc asks
# for a tight bounding box.
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
