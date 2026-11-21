"""Saving figures as PNG, PDF and SVG at the exact figure size, reproducibly.

``save_figure`` writes one file per format next to each other, uncropped unless asked. SVG and
PDF are written with fixed metadata, so saving the same figure again gives the same bytes, as it
does for PGF and for the raster formats such as PNG. SVGZ, PS and EPS record the time of the save.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import matplotlib as mpl
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.figure import Figure

from mplplots.utils import StrPath

__all__ = ["FORMATS", "save_figure"]

FORMATS: tuple[str, ...] = ("png", "pdf", "svg")
"""The formats ``save_figure`` writes by default, in the order it writes them."""

# Margin kept around the drawn content when a figure is saved cropped.
_CROP_PAD_INCHES = 0.02

# Without fixed dates, every save writes different SVG and PDF bytes for the same figure.
_METADATA: dict[str, dict[str, None]] = {"svg": {"Date": None}, "pdf": {"CreationDate": None}}


def save_figure(
    fig: Figure,
    path: StrPath,
    *,
    formats: Sequence[str] = FORMATS,
    dpi: float | None = None,
    caption: str | None = None,
    crop: bool = False,
    editable_svg_text: bool = False,
    close: bool = True,
) -> tuple[Path, ...]:
    """Save a figure in several formats, uncropped, with reproducible PNG, PDF and SVG output.

    Each format's extension is appended to ``path``, so a stem that contains a dot is kept
    whole, and missing parent directories are created. The saved files have the figure's size
    whatever ``savefig.bbox`` is set to. SVG is written without a date and with a fixed id salt,
    PDF without a creation date, so saving the same figure twice gives identical PNG, PDF and
    SVG files.

    Args:
        fig: The figure to save.
        path: The output path without an extension, for example ``"figures/fig01"``.
        formats: The file formats to write, each one ``Figure.savefig`` can write, such as
            ``"png"``, ``"pdf"`` or ``"svg"``. PDF, SVG, PGF and the raster formats (PNG,
            TIFF, JPEG, WebP, ...) are reproducible; SVGZ, PS and EPS record the time of the
            save, so their bytes differ from one save to the next.
        dpi: The resolution of raster output, in dots per inch. ``None`` uses
            ``rcParams["savefig.dpi"]``, which is 600 under every packaged style.
        caption: A caption draft. When it is not blank, it is written, stripped and
            newline-terminated, to ``<path>_caption.txt``.
        crop: Trim the saved files to the drawn content with a 0.02 in margin
            (``bbox_inches="tight"``) instead of keeping the figure's size.
        editable_svg_text: Keep SVG text as text elements instead of storing it as paths.
        close: Close the figure after saving it.

    Returns:
        The written paths in the order of ``formats``, followed by the caption file when one is
        written.

    Raises:
        ValueError: If ``formats`` is empty or names a format that neither the figure's canvas
            nor a registered canvas can write. Nothing is written in that case.

    Examples:
        >>> fig = plt.figure(figsize=(3.5, 2.5))
        >>> save_figure(fig, "figures/fig01", caption="Mean +/- SEM.")  # doctest: +SKIP
        (PosixPath('figures/fig01.png'), PosixPath('figures/fig01.pdf'),
         PosixPath('figures/fig01.svg'), PosixPath('figures/fig01_caption.txt'))
    """
    if not formats:
        raise ValueError("formats is empty; give at least one format, such as 'png'")
    # Figure.savefig writes a format the figure's canvas lacks through the canvas registered for
    # it, so a pdf, svg, ps or pgf backend still reaches every registered format.
    supported = {
        **FigureCanvasBase.get_supported_filetypes(),
        **fig.canvas.get_supported_filetypes(),
    }
    unsupported = [fmt for fmt in formats if fmt not in supported]
    if unsupported:
        raise ValueError(
            f"cannot save as {', '.join(map(repr, unsupported))}; "
            f"supported formats are {', '.join(sorted(supported))}"
        )

    base = Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    crop_kwargs: dict[str, Any] = (
        {"bbox_inches": "tight", "pad_inches": _CROP_PAD_INCHES} if crop else {}
    )
    written: list[Path] = []
    # "standard" keeps the file at the figure's size even if a matplotlibrc or style crops.
    with mpl.rc_context({
        "savefig.bbox": "standard",
        "svg.hashsalt": "mplplots",
        "svg.fonttype": "none" if editable_svg_text else "path",
    }):
        for fmt in formats:
            target = base.with_name(f"{base.name}.{fmt}")
            # Only formats with fixed metadata get the keyword: the pgf printer rejects it.
            metadata_kwargs: dict[str, Any] = (
                {"metadata": _METADATA[fmt]} if fmt in _METADATA else {}
            )
            fig.savefig(target, format=fmt, dpi=dpi, **metadata_kwargs, **crop_kwargs)
            written.append(target)

    if caption is not None and caption.strip():
        caption_path = base.with_name(f"{base.name}_caption.txt")
        caption_path.write_text(caption.strip() + "\n", encoding="utf-8")
        written.append(caption_path)

    if close:
        # Imported here, so that importing mplplots leaves pyplot and its backend alone.
        import matplotlib.pyplot as plt

        plt.close(fig)
    return tuple(written)
