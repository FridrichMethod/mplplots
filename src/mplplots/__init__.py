"""mplplots: Matplotlib styles (Personal by default) and a toolkit for publication figures."""

import importlib.metadata
from importlib.resources import files
from pathlib import Path

from matplotlib import style

from mplplots.check import (
    RULES,
    Issue,
    Severity,
    StyleError,
    StyleWarning,
    assert_figure,
    check_figure,
)
from mplplots.colors import (
    BAND_ALPHA,
    LINE_ALPHA,
    REFERENCE_LINE,
    SCATTER_ALPHA,
    SECONDARY_LINESTYLE,
    ColorPair,
    check_palette,
    contrast_ratio,
    darken,
    lighten,
    relative_luminance,
)
from mplplots.export import FORMATS, save_figure
from mplplots.layout import (
    COLUMN_WIDTHS,
    ColumnWidth,
    LegendCorner,
    add_axes_inches,
    add_shared_ylabel,
    align_legends_left,
    figure_size,
    grid_inches,
    legend_inches,
    suptitle_inches,
)
from mplplots.palettes import get_colors, set_palette
from mplplots.plots import box_axes, plot_distribution, plot_mean_sem, significance_stars
from mplplots.styles import DEFAULT_STYLE, STYLES, context, style_path, use
from mplplots.utils import add_custom_fonts, auto_ticks

__all__ = [
    "BAND_ALPHA",
    "COLUMN_WIDTHS",
    "DEFAULT_STYLE",
    "FORMATS",
    "LINE_ALPHA",
    "REFERENCE_LINE",
    "RULES",
    "SCATTER_ALPHA",
    "SECONDARY_LINESTYLE",
    "STYLES",
    "STYLE_PATH",
    "ColorPair",
    "ColumnWidth",
    "Issue",
    "LegendCorner",
    "Severity",
    "StyleError",
    "StyleWarning",
    "__version__",
    "add_axes_inches",
    "add_custom_fonts",
    "add_shared_ylabel",
    "align_legends_left",
    "assert_figure",
    "auto_ticks",
    "box_axes",
    "check_figure",
    "check_palette",
    "context",
    "contrast_ratio",
    "darken",
    "figure_size",
    "get_colors",
    "grid_inches",
    "legend_inches",
    "lighten",
    "plot_distribution",
    "plot_mean_sem",
    "prism_style",
    "relative_luminance",
    "save_figure",
    "set_palette",
    "significance_stars",
    "style_path",
    "suptitle_inches",
    "use",
]

__version__: str = importlib.metadata.version("mplplots")

STYLE_PATH = Path(str(files(__package__).joinpath("styles", "GraphPadPrism.mplstyle")))


def prism_style() -> None:
    """Set a prism style for Matplotlib plots."""
    style.use(STYLE_PATH)
