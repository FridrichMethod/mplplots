"""Check a figure against a packaged style and the style guide's rules.

``check_figure`` returns the issues it finds; ``assert_figure`` raises ``StyleError`` on errors
and emits a ``StyleWarning`` for each warning. The expected values (font size, font list, spine
width, hidden spines, legend frame, minus sign) are read from the named style's file, so the
check follows the style instead of restating it.

Only artists that are drawn are inspected: visible, with visible ancestors, and for text,
non-empty. Each message names the artist: its role, its text and the index of its axes in
``fig.axes`` (``axes 0``; an inset or secondary axes of it is ``axes 0 child 0``). The tick
labels of one axis that share a problem are reported in one message.
"""

from __future__ import annotations

import math
import re
import warnings
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast

import matplotlib.collections as mcollections
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import font_manager, rc_params_from_file, rcParamsDefault
from matplotlib.artist import Artist
from matplotlib.axis import Axis, Tick
from matplotlib.figure import Figure, SubFigure
from matplotlib.font_manager import FontProperties
from matplotlib.layout_engine import PlaceHolderLayoutEngine
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.spines import Spine
from matplotlib.table import Table
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox, BboxBase

from mplplots.styles import DEFAULT_STYLE, style_path

if TYPE_CHECKING:
    from matplotlib.axes._base import _AxesBase  # Axes, and SecondaryAxis among child axes
    from matplotlib.backend_bases import RendererBase
    from matplotlib.typing import RcKeyType  # Matplotlib 3.10+

__all__ = [
    "RULES",
    "Issue",
    "Severity",
    "StyleError",
    "StyleWarning",
    "assert_figure",
    "check_figure",
]

type Severity = Literal["error", "warning"]


@dataclass(frozen=True, slots=True)
class Issue:
    """One way in which a figure departs from a style.

    Attributes:
        rule: The rule id, a key of ``RULES``.
        severity: ``"error"`` or ``"warning"``.
        message: What is wrong, naming the artist: its role, its text and the index of its axes.
    """

    rule: str
    severity: Severity
    message: str


class StyleError(AssertionError):
    """Raised by ``assert_figure`` for a figure that breaks a rule, with one line per issue."""


class StyleWarning(UserWarning):
    """Emitted by ``assert_figure`` for each warning that ``check_figure`` reports."""


_RULE_TABLE: tuple[tuple[str, Severity, str], ...] = (
    ("font-size", "error", "Text whose size is neither the style's font.size nor an allowed size."),
    ("font-weight", "error", "Text whose weight is not regular."),
    ("font-family", "error", "Text that resolves to a font outside the style's font.sans-serif."),
    (
        "font-fallback",
        "warning",
        "The style's first-choice font is missing, so text uses a fallback.",
    ),
    ("script-glyph", "error", "Text with a precomposed superscript or subscript character."),
    ("unicode-minus", "warning", "Text with U+2212 when the style sets axes.unicode_minus: False."),
    (
        "spine-width",
        "error",
        "A drawn spine whose line width differs from axes.linewidth, or a color bar outline whose"
        " width differs from the minor tick width.",
    ),
    ("open-spines", "warning", "A drawn top or right spine where the style hides it."),
    ("legend-frame", "error", "A legend with a frame when the style sets legend.frameon: False."),
    ("layout-engine", "error", "A figure with a layout engine (tight or constrained)."),
    ("round-inches", "warning", "A figure or axes size or position off the 0.05 in grid."),
    ("off-canvas", "error", "Text or a legend that extends beyond the canvas."),
    ("text-overlap", "warning", "Texts whose drawn boxes overlap each other."),
    (
        "panel-letter",
        "warning",
        "Text other than a tick label that is a single letter: a, B, (c).",
    ),
    (
        "default-color",
        "warning",
        "A line, patch or collection in a Matplotlib default-cycle color.",
    ),
)

RULES: Mapping[str, str] = MappingProxyType({
    rule: description for rule, _, description in _RULE_TABLE
})
"""The rule ids that ``check_figure`` applies, each with a one-line description."""

_SEVERITY: Mapping[str, Severity] = {rule: severity for rule, severity, _ in _RULE_TABLE}

_GRID_INCHES = 0.05
_GRID_TOLERANCE_INCHES = 0.001
_CANVAS_TOLERANCE_PIXELS = 0.5
_OVERLAP_TOLERANCE_POINTS = 1.0
_SIZE_TOLERANCE_POINTS = 1e-6
_REGULAR_WEIGHT = 400
_SCRIPT_GLYPH = re.compile("[\u00b2\u00b3\u00b9\u2070-\u209f]")
_MINUS_SIGN = "\u2212"
_PANEL_LETTER = re.compile(r"[A-Za-z]|\([A-Za-z]\)")
_LEGEND_TEXT_ROLES = frozenset({"legend label", "legend title"})
_GENERIC_FAMILIES = frozenset({"serif", "sans-serif", "sans", "cursive", "fantasy", "monospace"})
# Matplotlib's default color cycle is tab10; these are its ten hex values.
_DEFAULT_COLORS: Mapping[str, str] = {
    mcolors.to_hex(value): name for name, value in mcolors.TABLEAU_COLORS.items()
}
_NO_LINE = frozenset({"None", "none", "", " "})


@dataclass(frozen=True, slots=True)
class _Expected:
    """The values a style sets, falling back to Matplotlib's defaults for keys it omits."""

    font_size: float
    font_list: tuple[str, ...]
    unicode_minus: bool
    spine_width: float
    colorbar_outline_width: float
    hide_top: bool
    hide_right: bool
    legend_frame: bool

    @classmethod
    def read(cls, style: str) -> _Expected:
        """Read the expected values from the file of a packaged style."""
        rc = rc_params_from_file(style_path(style), use_default_template=False)

        def value(key: RcKeyType) -> Any:
            """Return the style's value for a key, or Matplotlib's default."""
            return rc[key] if key in rc else rcParamsDefault[key]

        return cls(
            font_size=float(value("font.size")),
            font_list=tuple(value("font.sans-serif")),
            unicode_minus=bool(value("axes.unicode_minus")),
            spine_width=float(value("axes.linewidth")),
            colorbar_outline_width=float(value("xtick.minor.width")),
            hide_top=not value("axes.spines.top"),
            hide_right=not value("axes.spines.right"),
            legend_frame=bool(value("legend.frameon")),
        )


@dataclass(frozen=True, slots=True)
class _Text:
    """A drawn text: the artist, where it is (``figure``, ``axes 0``) and its role there."""

    text: Text
    owner: str
    role: str
    measurable: bool = True


@dataclass(slots=True)
class _Scene:
    """The drawn artists of a figure that the rules inspect."""

    texts: list[_Text] = field(default_factory=list)
    legends: list[tuple[str, Legend]] = field(default_factory=list)
    axes: list[tuple[str, _AxesBase]] = field(default_factory=list)
    spines: list[tuple[str, str, Spine, _AxesBase]] = field(default_factory=list)
    marks: list[tuple[str, Artist]] = field(default_factory=list)
    ticks: Mapping[Axis, Sequence[Tick]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _Context:
    """What every rule reads: the figure, its drawn artists and the expected values."""

    fig: Figure
    scene: _Scene
    expected: _Expected
    font_sizes: tuple[float, ...]
    font_weights: frozenset[int]


# --- Collecting the drawn artists ---------------------------------------------------------------


def _every_axes(fig: Figure) -> Iterator[_AxesBase]:
    """Yield the axes of a figure and their inset and secondary axes, depth first."""

    def walk(ax: _AxesBase) -> Iterator[_AxesBase]:
        """Yield an axes and, depth first, its child axes."""
        yield ax
        for child in ax.child_axes:
            yield from walk(child)

    for ax in fig.axes:
        yield from walk(ax)


class _TickRecorder:
    """Records the ticks that each axis of a figure draws.

    ``Axis.draw`` draws exactly the ticks that the private ``Axis._update_ticks`` returns: those
    inside the view interval, while the locator also proposes ticks just outside it. Calling
    ``_update_ticks`` again after the draw is not safe, because a 3D axis moves its tick labels
    after that call; so the recorder wraps it on each axis for the duration of the draw.
    """

    def __init__(self, axes: Iterable[_AxesBase]) -> None:
        """Prepare to record the ticks of every axis of the given axes."""
        self._axes = [axis for ax in axes for _, axis in _axis_items(ax)]
        self._hooked: list[Axis] = []
        self.drawn: dict[Axis, Sequence[Tick]] = {}

    def __enter__(self) -> _TickRecorder:
        """Wrap each axis's ``_update_ticks`` so that the draw records its ticks."""
        for axis in self._axes:
            update = getattr(axis, "_update_ticks", None)
            if callable(update) and "_update_ticks" not in vars(axis):
                vars(axis)["_update_ticks"] = self._recorder(axis, update)
                self._hooked.append(axis)
            elif axis not in self.drawn:
                # Without the private method, fall back to every tick the locator proposes.
                self.drawn[axis] = [*axis.get_major_ticks(), *axis.get_minor_ticks()]
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Remove the wrappers; an axis that drew no ticks records none."""
        for axis in self._hooked:
            vars(axis).pop("_update_ticks", None)
            self.drawn.setdefault(axis, [])

    def _recorder(
        self, axis: Axis, update: Callable[[], Sequence[Tick]]
    ) -> Callable[[], Sequence[Tick]]:
        """Return a wrapper of ``update`` that records the ticks it returns."""

        def record() -> Sequence[Tick]:
            """Return the ticks that the axis draws, recording them."""
            ticks = update()
            self.drawn[axis] = list(ticks)
            return ticks

        return record


def _scene(fig: Figure, ticks: Mapping[Axis, Sequence[Tick]]) -> _Scene:
    """Collect the drawn artists of a figure, given the ticks each axis drew."""
    scene = _Scene(ticks=ticks)
    if not fig.get_visible():
        return scene
    hidden: set[_AxesBase] = set()
    _collect_figure(fig, "figure", scene, hidden)
    for index, ax in enumerate(fig.axes):
        if ax not in hidden:
            _collect_axes(ax, f"axes {index}", scene)
    return scene


def _collect_figure(
    fig: Figure | SubFigure, owner: str, scene: _Scene, hidden: set[_AxesBase]
) -> None:
    """Add the drawn artists of a figure or subfigure and of its subfigures, but not its axes.

    The axes of a hidden subfigure go into ``hidden``.
    """
    for text in fig.texts:
        _add_text(scene, text, owner, _figure_text_role(fig, text))
    for legend in fig.legends:
        _add_legend(scene, owner, legend)
    scene.marks.extend((owner, mark) for mark in (*fig.lines, *fig.patches) if mark.get_visible())
    for artist in fig.artists:
        _add_artist(scene, owner, artist)
    for index, sub in enumerate(fig.subfigs):
        name = f"subfigure {index}" if owner == "figure" else f"{owner}.{index}"
        if sub.get_visible():
            _collect_figure(sub, name, scene, hidden)
        else:
            hidden.update(_subfigure_axes(sub))


def _subfigure_axes(sub: SubFigure) -> Iterator[_AxesBase]:
    """Yield the axes of a subfigure and of its nested subfigures."""
    yield from sub.axes
    for child in sub.subfigs:
        yield from _subfigure_axes(child)


def _figure_text_role(fig: Figure | SubFigure, text: Text) -> str:
    """Return the role of a figure-level text: title, x label, y label or text."""
    for attribute, role in (
        ("_suptitle", "title"),
        ("_supxlabel", "x label"),
        ("_supylabel", "y label"),
    ):
        if getattr(fig, attribute, None) is text:
            return role
    return "text"


def _collect_axes(ax: _AxesBase, owner: str, scene: _Scene) -> None:
    """Add a drawn axes, its texts, spines, legends and marks, and its child axes."""
    if not ax.get_visible():
        return
    if hasattr(ax, "_colorbar"):
        owner += " (color bar)"
    scene.axes.append((owner, ax))
    for title in (ax.title, getattr(ax, "_left_title", None), getattr(ax, "_right_title", None)):
        if isinstance(title, Text):
            _add_text(scene, title, owner, "title")
    # Axes3D sets axison to False and draws its axes itself while _axis3don is true.
    if ax.axison or getattr(ax, "_axis3don", False):
        for name, axis in _axis_items(ax):
            _collect_axis(axis, name, owner, scene)
    # Axes.draw draws the spines only when the axis and the frame are on.
    if ax.axison and ax.get_frame_on():
        scene.spines.extend(
            (owner, name, spine, ax) for name, spine in ax.spines.items() if spine.get_visible()
        )
    _collect_axes_texts(ax, owner, scene)
    if ax.legend_ is not None:
        _add_legend(scene, owner, ax.legend_)
    marks: Sequence[Artist] = (*ax.lines, *ax.patches, *ax.collections)
    scene.marks.extend((owner, mark) for mark in marks if mark.get_visible())
    for index, child in enumerate(ax.child_axes):
        _collect_axes(child, f"{owner} child {index}", scene)


def _collect_axes_texts(ax: _AxesBase, owner: str, scene: _Scene) -> None:
    """Add the texts and tables of an axes and the artists placed on it with ``add_artist``."""
    # A text placed in 3D moves to its projected position only during a draw, so its extent
    # after the draw is wrong and it is not measured.
    flat = ax.name != "3d"
    for text in ax.texts:
        _add_artist(scene, owner, text, measurable=flat)
    for artist in (*ax.artists, *ax.tables):
        _add_artist(scene, owner, artist, measurable=flat)


def _add_artist(scene: _Scene, owner: str, artist: Artist, *, measurable: bool = True) -> None:
    """Add a drawn artist of a figure or axes by its kind.

    A legend is added as a legend, a text or annotation as itself, a line, patch or collection
    as a mark, and any other artist (an offset box, a table) by the texts nested in it. This
    covers the artists placed with ``add_artist``, which a figure keeps in ``artists`` whatever
    their kind.
    """
    if not artist.get_visible():
        return
    if isinstance(artist, Legend):
        _add_legend(scene, owner, artist)
    elif isinstance(artist, Text):
        role = "annotation" if isinstance(artist, Annotation) else "text"
        _add_text(scene, artist, owner, role, measurable=measurable)
    elif isinstance(artist, (Line2D, Patch, mcollections.Collection)):
        scene.marks.append((owner, artist))
    else:
        role = "table text" if isinstance(artist, Table) else "text"
        for text in _nested_texts(artist):
            _add_text(scene, text, owner, role, measurable=measurable)


def _axis_items(ax: _AxesBase) -> list[tuple[str, Axis]]:
    """Return the axes' axis objects with their names: x, y and, in 3D, z."""
    items: list[tuple[str, Axis]] = [("x", ax.xaxis), ("y", ax.yaxis)]
    zaxis = getattr(ax, "zaxis", None)
    if isinstance(zaxis, Axis):
        items.append(("z", zaxis))
    return items


def _collect_axis(axis: Axis, name: str, owner: str, scene: _Scene) -> None:
    """Add the label, offset text and drawn tick labels of a drawn axis."""
    if not axis.get_visible():
        return
    _add_text(scene, axis.label, owner, f"{name} label")
    _add_text(scene, axis.offsetText, owner, f"{name} offset text")
    for tick in scene.ticks.get(axis, ()):
        if tick.get_visible():
            for label in (tick.label1, tick.label2):
                _add_text(scene, label, owner, f"{name} tick label")


def _nested_texts(artist: Artist) -> Iterator[Text]:
    """Yield the drawn texts inside an artist, such as a table or an offset box."""
    if isinstance(artist, Table):
        for cell in artist.get_celld().values():
            if cell.get_visible():
                yield cell.get_text()
        return
    for child in artist.get_children():
        if child.get_visible():
            if isinstance(child, Text):
                yield child
            yield from _nested_texts(child)


def _add_legend(scene: _Scene, owner: str, legend: Legend) -> None:
    """Add a drawn legend and its texts, once even if the figure holds it twice."""
    if not legend.get_visible() or any(legend is known for _, known in scene.legends):
        return
    scene.legends.append((owner, legend))
    for text in legend.texts:
        _add_text(scene, text, owner, "legend label")
    _add_text(scene, legend.get_title(), owner, "legend title")


def _add_text(scene: _Scene, text: Text, owner: str, role: str, *, measurable: bool = True) -> None:
    """Add a text if it is drawn: visible and not blank."""
    if text.get_visible() and text.get_text().strip():
        scene.texts.append(_Text(text, owner, role, measurable))


# --- Naming artists in messages -----------------------------------------------------------------


def _quote(text: str, limit: int = 40) -> str:
    """Return a text quoted for a message, shortened to ``limit`` characters."""
    return repr(text if len(text) <= limit else text[: limit - 3] + "...")


def _quote_all(texts: Sequence[str], limit: int = 4) -> str:
    """Return the first ``limit`` texts quoted and joined for a message."""
    quoted = [_quote(text) for text in texts[:limit]]
    if len(texts) > limit:
        quoted.append("...")
    return ", ".join(quoted)


def _legend_name(legend: Legend) -> str:
    """Return a legend's name for a message: its title, or else its entries."""
    title = legend.get_title().get_text()
    names = [title] if title else [text.get_text() for text in legend.texts]
    return f"legend {_quote_all(names)}" if names else "legend"


def _mark_name(mark: Artist) -> str:
    """Return a mark's name for a message: its type and its label, if it has one."""
    label = str(mark.get_label() or "")
    kind = type(mark).__name__
    return f"{kind} {_quote(label)}" if label and not label.startswith("_") else kind


def _texts(context: _Context, problem: Callable[[_Text], str | None]) -> Iterator[tuple[str, str]]:
    """Yield ``(subject, problem)`` for each text with a problem.

    The tick labels of one axis that share a problem are reported together.
    """
    ticks: dict[tuple[str, str, str], list[str]] = {}
    for item in context.scene.texts:
        found = problem(item)
        if found is None:
            continue
        if item.role.endswith("tick label"):
            ticks.setdefault((item.owner, item.role, found), []).append(item.text.get_text())
        else:
            yield f"{item.owner} {item.role} {_quote(item.text.get_text())}", found
    for (owner, role, found), labels in ticks.items():
        plural = "s" if len(labels) > 1 else ""
        yield f"{owner} {role}{plural} {_quote_all(labels)}", found


# --- The rules ----------------------------------------------------------------------------------

_Check = Callable[[_Context], Iterator[tuple[str, str]]]


def _check_font_size(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text whose size is neither the style's nor an allowed size."""
    expected = context.expected.font_size

    def problem(item: _Text) -> str | None:
        """Return the text's wrong size, or ``None`` if it is allowed."""
        size = item.text.get_fontproperties().get_size_in_points()
        if any(math.isclose(size, ok, abs_tol=_SIZE_TOLERANCE_POINTS) for ok in context.font_sizes):
            return None
        return f"font size {size:g} pt, expected {expected:g} pt"

    return _texts(context, problem)


def _numeric_weight(weight: int | str) -> int | str:
    """Return a font weight as a number; a name that Matplotlib does not know stays as it is."""
    return font_manager.weight_dict.get(weight, weight) if isinstance(weight, str) else weight


def _check_font_weight(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text whose weight is neither regular nor an allowed weight."""

    def problem(item: _Text) -> str | None:
        """Return the text's wrong weight, or ``None`` if it is allowed."""
        weight = item.text.get_fontweight()
        if _numeric_weight(weight) in context.font_weights:
            return None
        return f"font weight {weight}, expected regular"

    return _texts(context, problem)


def _family(text: Text) -> str:
    """Return the family name of the font file that a text renders in."""
    return font_manager.get_font(font_manager.findfont(text.get_fontproperties())).family_name


def _check_font_family(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text that renders in a font outside the style's list."""
    allowed = {name.lower() for name in context.expected.font_list} - _GENERIC_FAMILIES

    def problem(item: _Text) -> str | None:
        """Return the text's font if it is outside the list, else ``None``."""
        family = _family(item.text)
        if family.lower() in allowed:
            return None
        return f"renders in {family!r}, which is not in the style's font.sans-serif list"

    return _texts(context, problem)


def _installed(family: str) -> bool:
    """Return whether ``findfont`` finds a font of ``family`` itself, without falling back."""
    try:
        path = font_manager.findfont(FontProperties(family=family), fallback_to_default=False)
    except ValueError:
        return False
    return font_manager.get_font(path).family_name.lower() == family.lower()


def _check_font_fallback(context: _Context) -> Iterator[tuple[str, str]]:
    """Report once when the style's first-choice font is not installed."""
    fonts = context.expected.font_list
    if not fonts or fonts[0].lower() in _GENERIC_FAMILIES or not context.scene.texts:
        return
    if not _installed(fonts[0]):
        yield "figure", f"{fonts[0]!r} is not installed, so text renders in a fallback font"


def _check_script_glyph(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text with a precomposed superscript or subscript character."""

    def problem(item: _Text) -> str | None:
        """Return the first script character in the text, or ``None``."""
        match = _SCRIPT_GLYPH.search(item.text.get_text())
        if match is None:
            return None
        glyph = match.group()
        return (
            f"contains {glyph!r} (U+{ord(glyph):04X}); write exponents and subscripts as math"
            " text, such as '$^2$'"
        )

    return _texts(context, problem)


def _check_unicode_minus(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text with U+2212 when the style sets ``axes.unicode_minus: False``."""
    if context.expected.unicode_minus:
        return iter(())

    def problem(item: _Text) -> str | None:
        """Return the problem if the text has U+2212, else ``None``."""
        if _MINUS_SIGN in item.text.get_text():
            return "contains U+2212 MINUS SIGN; write the ASCII hyphen-minus"
        return None

    return _texts(context, problem)


def _check_spine_width(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each drawn spine whose line width differs from the style's.

    The outline of a color bar is as wide as a minor tick, lighter than the axis lines of the
    panel it belongs to; every other spine has the width of the axis lines.
    """
    for owner, name, spine, ax in context.scene.spines:
        if name == "outline" and hasattr(ax, "_colorbar"):
            expected, note = context.expected.colorbar_outline_width, ", the minor tick width"
        else:
            expected, note = context.expected.spine_width, ""
        width = spine.get_linewidth()
        if not math.isclose(width, expected, abs_tol=_SIZE_TOLERANCE_POINTS):
            yield (
                f"{owner} {name} spine",
                f"line width {width:g} pt, expected {expected:g} pt{note}",
            )


def _carries_axis(ax: _AxesBase, side: str) -> bool:
    """Return whether the axis on ``side`` has its ticks or label there, as on a twin axis."""
    if side == "top":
        return ax.xaxis.get_ticks_position() == "top" or ax.xaxis.get_label_position() == "top"
    return ax.yaxis.get_ticks_position() == "right" or ax.yaxis.get_label_position() == "right"


def _check_open_spines(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each drawn top or right spine that the style hides."""
    hidden = {"top": context.expected.hide_top, "right": context.expected.hide_right}
    for owner, name, _, ax in context.scene.spines:
        if hidden.get(name, False) and not _carries_axis(ax, name):
            yield f"{owner} {name} spine", "is drawn; the style hides the top and right spines"


def _check_legend_frame(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each drawn legend with a frame when the style draws none."""
    if context.expected.legend_frame:
        return
    for owner, legend in context.scene.legends:
        if legend.get_frame_on():
            yield f"{owner} {_legend_name(legend)}", "has a frame; the style draws none"


def _check_layout_engine(context: _Context) -> Iterator[tuple[str, str]]:
    """Report a tight or constrained layout engine on the figure."""
    engine = context.fig.get_layout_engine()
    if engine is not None and not isinstance(engine, PlaceHolderLayoutEngine):
        yield (
            "figure",
            f"uses the {type(engine).__name__}, which moves the axes; place them in inches",
        )


def _on_grid(inches: float) -> bool:
    """Return whether a length in inches is a multiple of 0.05 in, within 0.001 in."""
    return abs(inches - round(inches / _GRID_INCHES) * _GRID_INCHES) <= _GRID_TOLERANCE_INCHES


def _renderer(fig: Figure) -> RendererBase | None:
    """Return the renderer that Matplotlib measures a figure's artists with, or ``None``."""
    # Text.get_window_extent() and Legend.get_window_extent() measure with this renderer too.
    get_renderer = getattr(fig, "_get_renderer", None)
    return get_renderer() if callable(get_renderer) else None


def _axes_box_inches(ax: _AxesBase, fig: Figure, renderer: RendererBase | None) -> BboxBase:
    """Return the box an axes is placed in, in inches from the figure's lower left corner.

    At each draw, a fixed aspect (``imshow``, ``set_aspect``, ``set_box_aspect``, polar and 3D
    axes) shrinks the drawn axes inside this box, so the box, not the shrunk axes, is what the
    layout chose. An axes locator, as ``add_axes_inches`` and ``grid_inches`` set, returns the
    box at each draw; without a locator, the original position is the box. A color bar with
    extensions wraps its axes' locator in one that shrinks the box by the extensions, so the
    locator it wraps, or the original position when it wraps none, gives the box.
    """
    locator = cast("Callable[[_AxesBase, RendererBase], BboxBase] | None", ax.get_axes_locator())
    if hasattr(ax, "_colorbar"):
        # Matplotlib's private color bar locator keeps the locator it replaced here.
        locator = getattr(locator, "_orig_locator", locator)
    if locator is None:
        position: BboxBase = ax.get_position(original=True)
    elif renderer is not None:
        position = locator(ax, renderer)
    else:
        position = ax.get_position(original=False)
    parent = ax.get_figure()
    to_pixels = parent.transSubfigure if parent is not None else fig.transFigure
    return position.transformed(to_pixels + fig.dpi_scale_trans.inverted())


def _check_round_inches(context: _Context) -> Iterator[tuple[str, str]]:
    """Report a figure size, or an axes position or size, off the grid."""
    width, height = context.fig.get_size_inches()
    if not (_on_grid(width) and _on_grid(height)):
        yield "figure", f"size {width:.4g} x {height:.4g} in is not a multiple of 0.05 in"
    renderer = _renderer(context.fig)
    for owner, ax in context.scene.axes:
        box = _axes_box_inches(ax, context.fig, renderer)
        if not all(_on_grid(value) for value in (box.x0, box.y0, box.width, box.height)):
            yield (
                owner,
                f"position ({box.x0:.4g}, {box.y0:.4g}) in and size {box.width:.4g} x"
                f" {box.height:.4g} in are not all multiples of 0.05 in",
            )


def _overhang(box: BboxBase | None, canvas: BboxBase) -> str | None:
    """Return which edges of the canvas a box crosses, or ``None`` if it is inside."""
    if box is None:
        return None
    tolerance = _CANVAS_TOLERANCE_PIXELS
    sides = [
        side
        for side, beyond in (
            ("left", box.x0 < canvas.x0 - tolerance),
            ("right", box.x1 > canvas.x1 + tolerance),
            ("bottom", box.y0 < canvas.y0 - tolerance),
            ("top", box.y1 > canvas.y1 + tolerance),
        )
        if beyond
    ]
    if not sides:
        return None
    edges = " and ".join(sides) + (" edges" if len(sides) > 1 else " edge")
    return f"extends beyond the {edges} of the canvas, which an uncropped file cuts off"


def _text_box(text: Text, *, with_arrow: bool = True) -> Bbox | None:
    """Return the drawn extent of a text in pixels, cut to its clip box.

    The extent of an annotation spans its arrow as well; ``with_arrow=False`` gives the extent
    of its text alone.
    """
    box = text.get_window_extent() if with_arrow else Text.get_window_extent(text)
    clip_box = text.get_clip_box() if text.get_clip_on() else None
    return Bbox.intersection(box, clip_box) if clip_box is not None else box


def _check_off_canvas(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text and legend that extends beyond the canvas."""
    canvas = context.fig.bbox

    def problem(item: _Text) -> str | None:
        """Return the edges of the canvas the text crosses, or ``None``."""
        # A legend's texts are reported as the legend.
        if not item.measurable or item.role in _LEGEND_TEXT_ROLES:
            return None
        return _overhang(_text_box(item.text), canvas)

    yield from _texts(context, problem)
    for owner, legend in context.scene.legends:
        found = _overhang(legend.get_window_extent(), canvas)
        if found is not None:
            yield f"{owner} {_legend_name(legend)}", found


def _is_quarter_turn(text: Text) -> bool:
    """Return whether a text is upright or turned by a multiple of 90 degrees."""
    remainder = text.get_rotation() % 90.0
    return min(remainder, 90.0 - remainder) < 1e-6


def _check_text_overlap(context: _Context) -> Iterator[tuple[str, str]]:
    """Report the texts whose drawn boxes overlap by more than a point in each direction.

    Only upright texts and texts turned by a multiple of 90 degrees are compared: the bounding
    box of a text at any other angle is larger than the text. An annotation counts by its text,
    without its arrow. Each overlap is reported once, under the text that comes first, and the
    tick labels of one axis that overlap each other are reported together.
    """
    items: list[_Text] = []
    extents: list[Sequence[float]] = []
    for item in context.scene.texts:
        if not item.measurable or not _is_quarter_turn(item.text):
            continue
        box = _text_box(item.text, with_arrow=False)
        if box is not None and box.width > 0 and box.height > 0:
            items.append(item)
            extents.append(box.extents)
    if len(items) < 2:
        return
    tolerance = _OVERLAP_TOLERANCE_POINTS * context.fig.dpi / 72.0
    x0, y0, x1, y1 = np.asarray(extents, dtype=float).T
    wide = np.minimum(x1[:, None], x1[None, :]) - np.maximum(x0[:, None], x0[None, :])
    tall = np.minimum(y1[:, None], y1[None, :]) - np.maximum(y0[:, None], y0[None, :])
    pairs = np.argwhere(np.triu((wide > tolerance) & (tall > tolerance), k=1))

    crowded: dict[tuple[str, str], dict[int, str]] = {}
    partners: dict[int, dict[tuple[str, str], list[str]]] = {}
    for first, second in pairs.tolist():
        a, b = items[first], items[second]
        if a.role.endswith("tick label") and (a.owner, a.role) == (b.owner, b.role):
            labels = crowded.setdefault((a.owner, a.role), {})
            labels[first], labels[second] = a.text.get_text(), b.text.get_text()
        else:
            others = partners.setdefault(first, {})
            others.setdefault((b.owner, b.role), []).append(b.text.get_text())
    for (owner, role), labels in crowded.items():
        yield f"{owner} {role}s {_quote_all(list(labels.values()))}", "overlap each other"
    for first, others in partners.items():
        a = items[first]
        named = " and ".join(
            f"{owner} {role} {_quote_all(texts)}" for (owner, role), texts in others.items()
        )
        yield f"{a.owner} {a.role} {_quote(a.text.get_text())}", f"overlaps {named}"


def _check_panel_letter(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each text other than a tick label that is a letter alone or in parentheses."""

    def problem(item: _Text) -> str | None:
        """Return why the text reads as a panel letter, or ``None`` if it does not."""
        # A tick label names a category, and a variable in any other text is math text ($x$).
        if item.role.endswith("tick label"):
            return None
        if _PANEL_LETTER.fullmatch(item.text.get_text().strip()):
            return "is a single letter; panel letters are added when the manuscript is assembled"
        return None

    return _texts(context, problem)


def _shown_colors(mark: Artist) -> list[Any]:
    """Return the colors a line, patch or collection draws; none for a color-mapped one."""
    if isinstance(mark, Line2D):
        colors: list[Any] = []
        if mark.get_linestyle() not in _NO_LINE and mark.get_linewidth() > 0:
            colors.append(mark.get_color())
        if mark.get_marker() not in _NO_LINE:
            colors.extend((mark.get_markerfacecolor(), mark.get_markeredgecolor()))
        return colors
    if isinstance(mark, Patch):
        colors = [mark.get_facecolor()] if mark.get_fill() else []
        if mark.get_linewidth() > 0:
            colors.append(mark.get_edgecolor())
        return colors
    if isinstance(mark, mcollections.Collection) and mark.get_array() is None:
        colors = list(mark.get_facecolor())
        if np.any(np.asarray(mark.get_linewidth()) > 0):
            colors.extend(mark.get_edgecolor())
        return colors
    return []


def _default_color(mark: Artist) -> str | None:
    """Return the first default-cycle color that a mark shows, or ``None``."""
    for color in _shown_colors(mark):
        rgba = mcolors.to_rgba(color)
        if rgba[3] > 0:
            value = mcolors.to_hex(rgba, keep_alpha=False)
            if value in _DEFAULT_COLORS:
                return value
    return None


def _check_default_color(context: _Context) -> Iterator[tuple[str, str]]:
    """Report each mark that shows a color of Matplotlib's default cycle."""
    for owner, mark in context.scene.marks:
        value = _default_color(mark)
        if value is not None:
            yield (
                f"{owner} {_mark_name(mark)}",
                f"color {value} ({_DEFAULT_COLORS[value]}) is from Matplotlib's default cycle;"
                " take colors from the project's palette",
            )


_CHECKS: Mapping[str, _Check] = {
    "font-size": _check_font_size,
    "font-weight": _check_font_weight,
    "font-family": _check_font_family,
    "font-fallback": _check_font_fallback,
    "script-glyph": _check_script_glyph,
    "unicode-minus": _check_unicode_minus,
    "spine-width": _check_spine_width,
    "open-spines": _check_open_spines,
    "legend-frame": _check_legend_frame,
    "layout-engine": _check_layout_engine,
    "round-inches": _check_round_inches,
    "off-canvas": _check_off_canvas,
    "text-overlap": _check_text_overlap,
    "panel-letter": _check_panel_letter,
    "default-color": _check_default_color,
}


# --- Public functions ---------------------------------------------------------------------------


def _rule_ids(ignore: Collection[str]) -> frozenset[str]:
    """Return the rule ids to skip, raising ``ValueError`` for an unknown one."""
    ids = frozenset((ignore,) if isinstance(ignore, str) else ignore)
    unknown = sorted(ids - RULES.keys())
    if unknown:
        raise ValueError(
            f"unknown rule {', '.join(map(repr, unknown))}; choose from {', '.join(RULES)}"
        )
    return ids


def _font_weights(allowed: Collection[int | str]) -> frozenset[int]:
    """Return regular and the allowed font weights as numbers.

    Raises:
        ValueError: If a name is not a font weight that Matplotlib knows.
    """
    weights = {
        _numeric_weight(weight) for weight in ((allowed,) if isinstance(allowed, str) else allowed)
    }
    unknown = sorted(weight for weight in weights if isinstance(weight, str))
    if unknown:
        raise ValueError(
            f"unknown font weight {', '.join(map(repr, unknown))};"
            f" choose from {', '.join(font_manager.weight_dict)} or give a number"
        )
    return frozenset({_REGULAR_WEIGHT, *(int(weight) for weight in weights)})


def check_figure(
    fig: Figure,
    *,
    style: str = DEFAULT_STYLE,
    ignore: Collection[str] = (),
    allow_font_sizes: Collection[float] = (),
    allow_font_weights: Collection[int | str] = (),
) -> list[Issue]:
    """Check a figure against a packaged style and the style guide's rules.

    The figure is drawn once without output, so that tick labels exist and text extents are
    known. Only drawn artists are inspected: visible, with visible ancestors, and for text,
    non-empty. Unusual figures (polar and 3D axes, color bars, twin axes, hidden or empty axes,
    log scales, images) are checked as far as the rules apply to them.

    Args:
        fig: The figure to check.
        style: The style whose file holds the expected values, one of ``STYLES``.
        ignore: Rule ids (keys of ``RULES``) to skip.
        allow_font_sizes: Font sizes in points accepted besides the style's ``font.size``.
        allow_font_weights: Font weights accepted besides regular, as names (``"bold"``) or
            numbers (``500``), for text that the figure emphasizes on purpose.

    Returns:
        The issues found, ordered by rule as in ``RULES``; an empty list for a clean figure.

    Raises:
        ValueError: If ``style`` is not a packaged style, ``ignore`` holds an unknown rule id or
            ``allow_font_weights`` holds a name that is not a font weight.
    """
    ignored = _rule_ids(ignore)
    weights = _font_weights(allow_font_weights)
    expected = _Expected.read(style)
    with _TickRecorder(_every_axes(fig)) as recorder:
        fig.draw_without_rendering()
    sizes = (expected.font_size, *(float(size) for size in allow_font_sizes))
    context = _Context(fig, _scene(fig, recorder.drawn), expected, sizes, weights)
    return [
        Issue(rule, _SEVERITY[rule], f"{subject}: {problem}")
        for rule, check in _CHECKS.items()
        if rule not in ignored
        for subject, problem in check(context)
    ]


def assert_figure(
    fig: Figure,
    *,
    style: str = DEFAULT_STYLE,
    ignore: Collection[str] = (),
    allow_font_sizes: Collection[float] = (),
    allow_font_weights: Collection[int | str] = (),
    warnings_as_errors: bool = False,
) -> None:
    """Raise if a figure breaks a rule of a packaged style; warn about the rest.

    Args:
        fig: The figure to check.
        style: The style whose file holds the expected values, one of ``STYLES``.
        ignore: Rule ids (keys of ``RULES``) to skip.
        allow_font_sizes: Font sizes in points accepted besides the style's ``font.size``.
        allow_font_weights: Font weights accepted besides regular, as names (``"bold"``) or
            numbers (``500``), for text that the figure emphasizes on purpose.
        warnings_as_errors: Raise for warnings as well as errors.

    Raises:
        StyleError: If ``check_figure`` reports an error, or a warning when
            ``warnings_as_errors`` is true. Its message has one line per issue,
            ``rule: message``.
        ValueError: If ``style`` is not a packaged style, ``ignore`` holds an unknown rule id or
            ``allow_font_weights`` holds a name that is not a font weight.
    """
    issues = check_figure(
        fig,
        style=style,
        ignore=ignore,
        allow_font_sizes=allow_font_sizes,
        allow_font_weights=allow_font_weights,
    )
    failing = [issue for issue in issues if warnings_as_errors or issue.severity == "error"]
    if failing:
        raise StyleError("\n".join(f"{issue.rule}: {issue.message}" for issue in failing))
    for issue in issues:
        warnings.warn(f"{issue.rule}: {issue.message}", StyleWarning, stacklevel=2)
