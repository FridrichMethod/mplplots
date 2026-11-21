"""mplplots: Visual styling helpers for Matplotlib/Seaborn."""

import importlib.metadata
from importlib.resources import files
from pathlib import Path

from matplotlib import style

from mplplots.styles import DEFAULT_STYLE, STYLES, context, style_path, use

__all__ = [
    "DEFAULT_STYLE",
    "STYLES",
    "STYLE_PATH",
    "__version__",
    "context",
    "prism_style",
    "style_path",
    "use",
]

__version__: str = importlib.metadata.version("mplplots")

STYLE_PATH = Path(str(files(__package__).joinpath("styles", "GraphPadPrism.mplstyle")))


def prism_style() -> None:
    """Set a prism style for Matplotlib plots."""
    style.use(STYLE_PATH)
