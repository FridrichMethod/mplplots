"""The packaged Matplotlib styles and the functions that apply them.

Each style is a self-contained ``.mplstyle`` file in this package, named after its file stem.
A style also loads without mplplots imported, by its dotted name, for example
``plt.style.use("mplplots.styles.Personal")``.
"""

from contextlib import AbstractContextManager
from importlib.resources import files
from pathlib import Path

import matplotlib.style as mplstyle

__all__ = ["DEFAULT_STYLE", "STYLES", "context", "style_path", "use"]

_SUFFIX = ".mplstyle"

DEFAULT_STYLE: str = "Personal"
"""The style that ``style_path``, ``use`` and ``context`` apply when no name is given."""

STYLES: tuple[str, ...] = tuple(
    sorted(
        entry.name.removesuffix(_SUFFIX)
        for entry in files(__name__).iterdir()
        if entry.is_file() and entry.name.endswith(_SUFFIX)
    )
)
"""The names of the packaged styles, sorted."""


def style_path(name: str = DEFAULT_STYLE) -> Path:
    """Return the path of a packaged style file.

    Args:
        name: The style name, one of ``STYLES``.

    Returns:
        The path of the style's ``.mplstyle`` file.

    Raises:
        ValueError: If ``name`` is not a packaged style.
    """
    if name not in STYLES:
        raise ValueError(f"unknown style {name!r}; choose from {', '.join(STYLES)}")
    return Path(str(files(__name__).joinpath(name + _SUFFIX)))


def use(style: str = DEFAULT_STYLE) -> None:
    """Apply a packaged style to Matplotlib's global settings.

    Args:
        style: The style name, one of ``STYLES``.

    Raises:
        ValueError: If ``style`` is not a packaged style.
    """
    mplstyle.use(style_path(style))


def context(style: str = DEFAULT_STYLE) -> AbstractContextManager[None]:
    """Return a context manager that applies a packaged style inside a ``with`` block.

    Matplotlib's settings are restored when the block exits.

    Args:
        style: The style name, one of ``STYLES``.

    Returns:
        A context manager that applies the style.

    Raises:
        ValueError: If ``style`` is not a packaged style.
    """
    return mplstyle.context(style_path(style))
