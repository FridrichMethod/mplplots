"""mplplots: Visual styling helpers for Matplotlib/Seaborn."""

from importlib.resources import files
from pathlib import Path

from matplotlib import style

__all__ = ["STYLE_PATH", "prism_style"]


STYLE_PATH = Path(str(files(__package__).joinpath("styles", "GraphPadPrism.mplstyle")))


def prism_style() -> None:
    """Set a prism style for Matplotlib plots."""
    style.use(STYLE_PATH)
