"""mplplots: Visual styling helpers for Matplotlib/Seaborn."""
from importlib.resources import files

import matplotlib as mpl

EXPORTS = ["prism_style"]


STYLE_PATH = files(__package__).joinpath("styles", "GraphPadPrism.mplstyle")


def prism_style() -> None:
    """Set a prism style for Matplotlib plots."""
    mpl.style.use(STYLE_PATH)
