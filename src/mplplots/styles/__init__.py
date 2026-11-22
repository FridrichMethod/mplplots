"""The packaged Matplotlib styles and the functions that apply them.

Each style is a self-contained ``.mplstyle`` file in this package, named after its file stem.
A style also loads without mplplots imported, by its dotted name, for example
``plt.style.use("mplplots.styles.Personal")``.

``use`` and ``context`` first return every setting that any packaged style sets to
Matplotlib's default and then apply the style, so a style looks the same whichever packaged
style was applied before it. ``plt.style.use`` applies only the settings in the file.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import matplotlib.style as mplstyle
from matplotlib import rc_params_from_file, rcParamsDefault

if TYPE_CHECKING:
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

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


@cache
def _style_keys() -> tuple[RcKeyType, ...]:
    """Return the settings that any packaged style sets, sorted."""
    keys: set[str] = set()
    for name in STYLES:
        keys.update(rc_params_from_file(style_path(name), use_default_template=False))
    return cast("tuple[RcKeyType, ...]", tuple(sorted(keys)))


def _from_defaults(style: str) -> list[dict[str, Any] | Path]:
    """Return a style list that resets every packaged style's settings, then applies ``style``.

    Raises:
        ValueError: If ``style`` is not a packaged style.
    """
    path = style_path(style)
    return [{key: rcParamsDefault[key] for key in _style_keys()}, path]


def use(style: str = DEFAULT_STYLE) -> None:
    """Apply a packaged style to Matplotlib's global settings.

    Every setting that any packaged style sets first returns to Matplotlib's default, so
    switching from another packaged style gives the same settings as applying this one alone.

    Args:
        style: The style name, one of ``STYLES``.

    Raises:
        ValueError: If ``style`` is not a packaged style.
    """
    mplstyle.use(_from_defaults(style))


def context(style: str = DEFAULT_STYLE) -> AbstractContextManager[None]:
    """Return a context manager that applies a packaged style inside a ``with`` block.

    Inside the block, every setting that any packaged style sets first returns to Matplotlib's
    default, as in ``use``. Matplotlib's settings are restored when the block exits.

    Args:
        style: The style name, one of ``STYLES``.

    Returns:
        A context manager that applies the style.

    Raises:
        ValueError: If ``style`` is not a packaged style.
    """
    return mplstyle.context(_from_defaults(style))
