import math
import warnings

import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.transforms import Bbox

from mplplots import layout, utils
from mplplots.layout import (
    COLUMN_WIDTHS,
    add_shared_ylabel,
    align_legends_left,
    figure_size,
    grid_inches,
)


def inches(ax: Axes) -> tuple[float, float, float, float]:
    """Left, bottom, width and height of ax in inches."""
    fig = ax.get_figure()
    assert isinstance(fig, Figure)
    width, height = fig.get_size_inches()
    box = ax.get_position()
    return (box.x0 * width, box.y0 * height, box.width * width, box.height * height)


def tight_box(ax: Axes) -> Bbox:
    """The tight bounding box of ax in pixels, which must exist."""
    box = ax.get_tightbbox()
    assert box is not None
    return box


def legend_of(ax: Axes) -> Legend:
    """The legend of ax, which must exist."""
    legend = ax.get_legend()
    assert legend is not None
    return legend


def test_column_widths() -> None:
    assert dict(COLUMN_WIDTHS) == {"single": 3.5, "onehalf": 5.0, "double": 7.0}


def test_figure_size() -> None:
    assert figure_size() == pytest.approx((3.5, 2.45))
    assert figure_size("double", aspect=0.5) == pytest.approx((7.0, 3.5))
    assert figure_size("onehalf", height=1.8) == pytest.approx((5.0, 1.8))
    assert figure_size(4.0, height=2.0, aspect=0.9) == pytest.approx((4.0, 2.0))


@pytest.mark.parametrize("kwargs", [{"width": "triple"}, {"width": 0.0}, {"height": -1.0}])
def test_figure_size_rejects(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        figure_size(**kwargs)  # type: ignore[arg-type]


def test_grid_inches_geometry() -> None:
    fig, axes = grid_inches(2, 3, width=2.0, height=1.5)
    assert tuple(fig.get_size_inches()) == pytest.approx((7.9, 4.0))
    assert len(axes) == 6
    assert inches(axes[0]) == pytest.approx((0.6, 2.4, 2.0, 1.5))
    assert inches(axes[5]) == pytest.approx((5.8, 0.4, 2.0, 1.5))


def test_grid_inches_single_panel_with_margins() -> None:
    fig, (ax,) = grid_inches(width=2.25, height=1.5, left=0.5, right=0.25, top=0.35, bottom=0.4)
    assert tuple(fig.get_size_inches()) == pytest.approx((3.0, 2.25))
    assert inches(ax) == pytest.approx((0.5, 0.4, 2.25, 1.5))


def test_grid_inches_per_row_and_per_column_sizes() -> None:
    fig, axes = grid_inches(2, 2, width=[2.0, 1.0], height=[0.8, 1.6], wspace=0.5, hspace=0.2)
    assert tuple(fig.get_size_inches()) == pytest.approx((4.2, 3.1))
    assert inches(axes[0]) == pytest.approx((0.6, 2.2, 2.0, 0.8))
    assert inches(axes[3]) == pytest.approx((3.1, 0.4, 1.0, 1.6))


def test_grid_inches_keeps_axis_lengths_when_the_figure_is_resized() -> None:
    fig, (ax,) = grid_inches(width=2.0, height=1.0)
    fig.set_size_inches(6.0, 4.0)
    fig.draw_without_rendering()
    assert inches(ax)[2:] == pytest.approx((2.0, 1.0))


def test_grid_inches_shares_axes_and_hides_inner_tick_labels() -> None:
    fig, axes = grid_inches(2, 2, width=1.5, height=1.0, sharex=True, sharey=True)
    axes[3].set_xlim(0, 5)
    assert axes[0].get_xlim() == (0, 5)
    fig.draw_without_rendering()
    assert not any(label.get_visible() for label in axes[0].get_xticklabels())
    assert any(label.get_visible() for label in axes[2].get_xticklabels())
    assert not any(label.get_visible() for label in axes[1].get_yticklabels())
    assert any(label.get_visible() for label in axes[0].get_yticklabels())


@pytest.mark.parametrize(
    "kwargs",
    [
        {"nrows": 0, "width": 1.0, "height": 1.0},
        {"width": 0.0, "height": 1.0},
        {"width": 1.0, "height": 1.0, "left": -0.1},
        {"ncols": 2, "width": [1.0, 1.0, 1.0], "height": 1.0},
        {"ncols": 3, "width": 1.0, "height": 1.0, "wspace": [0.5]},
    ],
)
def test_grid_inches_rejects(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        grid_inches(**kwargs)  # type: ignore[arg-type]


def test_grid_inches_passes_figure_kwargs() -> None:
    fig, _ = grid_inches(width=1.0, height=1.0, num="named")
    assert fig.get_label() == "named"


def test_shared_ylabel_sits_labelpad_from_the_tick_labels() -> None:
    plt.rcParams["axes.labelpad"] = 3.0
    fig, axes = grid_inches(3, 1, width=3.0, height=0.8, hspace=0.2, sharex=True)
    label = add_shared_ylabel(fig, axes, "Shared label")
    fig.draw_without_rendering()
    ink_left = min(tight_box(ax).x0 for ax in axes)
    gap_pt = (ink_left - label.get_window_extent().x1) * 72 / fig.dpi
    assert gap_pt == pytest.approx(3.0, abs=0.5)
    boxes = [ax.get_position() for ax in axes]
    centre = (min(box.y0 for box in boxes) + max(box.y1 for box in boxes)) / 2
    assert label.get_position()[1] == pytest.approx(centre)
    assert label.get_rotation() == 90


def test_shared_ylabel_needs_axes() -> None:
    with pytest.raises(ValueError):
        add_shared_ylabel(plt.figure(), [], "label")


def test_align_legends_left() -> None:
    fig, axes = grid_inches(2, 1, width=3.0, height=1.0)
    axes[0].plot([0, 1], [0, 1], label="short")
    axes[1].plot([0, 1], [0, 1], label="a much longer legend label")
    for ax in axes:
        ax.legend(loc="upper right")
    x0 = align_legends_left(axes)
    fig.draw_without_rendering()
    lefts = [legend_of(ax).get_window_extent().x0 for ax in axes]
    assert lefts[0] == pytest.approx(lefts[1], abs=0.5)
    assert 0.0 < x0 < 1.0


def test_align_legends_left_without_legends() -> None:
    _, axes = grid_inches(2, 1, width=1.0, height=1.0)
    assert math.isnan(align_legends_left(axes))


def test_align_legends_left_in_a_nested_subfigure_does_not_warn() -> None:
    fig = plt.figure(figsize=(10.0, 4.0))
    outer = fig.add_subfigure(fig.add_gridspec(1, 2)[0])
    inner = outer.add_subfigure(outer.add_gridspec(2, 1)[0])
    axes = [inner.add_subplot(2, 1, 1), inner.add_subplot(2, 1, 2)]
    axes[0].plot([0, 1], [0, 1], label="short")
    axes[1].plot([0, 1], [0, 1], label="a much longer legend label")
    for ax in axes:
        ax.legend(loc="upper right")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        x0 = align_legends_left(axes)
    fig.draw_without_rendering()
    lefts = [legend_of(ax).get_window_extent().x0 for ax in axes]
    assert lefts[0] == pytest.approx(lefts[1], abs=0.5)
    assert 0.0 < x0 < 1.0


def test_layout_reexports_the_inch_helpers() -> None:
    for name in ("add_axes_inches", "legend_inches", "suptitle_inches"):
        assert getattr(layout, name) is getattr(utils, name)


# Tests beyond the plan's list.


@pytest.mark.parametrize(
    "kwargs",
    [{"aspect": 0.0}, {"aspect": -0.5}, {"width": float("nan")}, {"height": 0.0}],
)
def test_figure_size_rejects_non_positive_and_nan(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        figure_size(**kwargs)  # type: ignore[arg-type]


def test_figure_size_takes_a_number_as_inches() -> None:
    assert figure_size(2.5) == pytest.approx((2.5, 1.75))
    assert figure_size(6, aspect=0.5) == pytest.approx((6.0, 3.0))


def test_grid_inches_orders_axes_row_major_from_the_top() -> None:
    _, axes = grid_inches(2, 3, width=[1.0, 1.5, 2.0], height=[0.5, 1.0], wspace=0.25, hspace=0.3)
    assert [inches(ax) for ax in axes] == [
        pytest.approx((0.6, 1.7, 1.0, 0.5)),
        pytest.approx((1.85, 1.7, 1.5, 0.5)),
        pytest.approx((3.6, 1.7, 2.0, 0.5)),
        pytest.approx((0.6, 0.4, 1.0, 1.0)),
        pytest.approx((1.85, 0.4, 1.5, 1.0)),
        pytest.approx((3.6, 0.4, 2.0, 1.0)),
    ]


def test_grid_inches_takes_per_gap_spaces() -> None:
    fig, axes = grid_inches(3, 3, width=1.0, height=1.0, wspace=[0.25, 0.5], hspace=[0.1, 0.2])
    assert tuple(fig.get_size_inches()) == pytest.approx((4.45, 3.8))
    assert [inches(ax)[0] for ax in axes[:3]] == pytest.approx([0.6, 1.85, 3.35])
    assert [inches(ax)[1] for ax in axes[::3]] == pytest.approx([2.7, 1.6, 0.4])


def test_grid_inches_figure_is_whole_pixels_at_600_dpi() -> None:
    # 0.6 + 2 + 2 + 2 + 0.6 + 0.6 + 0.1 summed left to right is 7.899999999999999 in, which
    # Agg truncates to 4739 px at 600 dpi. Matplotlib 3.10 and later tolerate 1e-8 px in
    # get_width_height and 3.8 does not, so the exact size is checked as well.
    fig, _ = grid_inches(2, 3, width=2.0, height=1.5)
    assert tuple(float(size) for size in fig.get_size_inches()) == (7.9, 4.0)
    fig.set_dpi(600)
    assert fig.canvas.get_width_height() == (4740, 2400)


@pytest.mark.parametrize(
    ("args", "kwargs", "size", "pixels"),
    [
        ((), {}, (3.5, 2.45), (2100, 1470)),
        (("double",), {}, (7.0, 4.9), (4200, 2940)),
        ((7.0,), {"aspect": 0.35}, (7.0, 2.45), (4200, 1470)),
        ((3.5,), {"aspect": 0.55}, (3.5, 1.925), (2100, 1155)),
    ],
)
def test_figure_size_is_exact_and_whole_pixels_at_600_dpi(
    args: tuple[object, ...],
    kwargs: dict[str, float],
    size: tuple[float, float],
    pixels: tuple[int, int],
) -> None:
    # 3.5 * 0.7 is 2.4499999999999997 in floating point, which Agg truncates to 1469 px at
    # 600 dpi on Matplotlib 3.8. The exact comparison catches that on every version.
    result = figure_size(*args, **kwargs)  # type: ignore[arg-type]
    assert result == size
    fig = plt.figure(figsize=result, dpi=600)
    assert fig.canvas.get_width_height() == pixels


def test_grid_inches_sharex_only_keeps_every_y_label() -> None:
    fig, axes = grid_inches(2, 2, width=1.5, height=1.0, sharex=True)
    axes[0].set_ylim(0, 2)
    axes[3].set_xlim(0, 5)
    fig.draw_without_rendering()
    assert axes[1].get_ylim() == (0, 1)
    assert axes[0].get_xlim() == (0, 5)
    assert all(any(label.get_visible() for label in ax.get_yticklabels()) for ax in axes)
    assert not any(label.get_visible() for ax in axes[:2] for label in ax.get_xticklabels())
    assert all(any(label.get_visible() for label in ax.get_xticklabels()) for ax in axes[2:])
    assert not axes[0].xaxis.get_offset_text().get_visible()
    assert axes[2].xaxis.get_offset_text().get_visible()


def test_grid_inches_sharey_only_keeps_every_x_label() -> None:
    fig, axes = grid_inches(2, 2, width=1.5, height=1.0, sharey=True)
    axes[0].set_xlim(0, 2)
    axes[3].set_ylim(0, 5)
    fig.draw_without_rendering()
    assert axes[1].get_xlim() == (0, 1)
    assert axes[0].get_ylim() == (0, 5)
    assert all(any(label.get_visible() for label in ax.get_xticklabels()) for ax in axes)
    assert not any(label.get_visible() for ax in axes[1::2] for label in ax.get_yticklabels())
    assert all(any(label.get_visible() for label in ax.get_yticklabels()) for ax in axes[::2])
    assert not axes[1].yaxis.get_offset_text().get_visible()
    assert axes[0].yaxis.get_offset_text().get_visible()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"ncols": -1, "width": 1.0, "height": 1.0},
        {"nrows": 2, "width": 1.0, "height": [1.0, -1.0]},
        {"width": 1.0, "height": float("nan")},
        {"width": 1.0, "height": 1.0, "right": -0.1},
        {"width": 1.0, "height": 1.0, "top": -0.1},
        {"width": 1.0, "height": 1.0, "bottom": -0.1},
        {"nrows": 2, "width": 1.0, "height": 1.0, "hspace": -0.1},
        {"ncols": 3, "width": 1.0, "height": 1.0, "wspace": [0.5, -0.5]},
        {"nrows": 2, "width": 1.0, "height": [1.0]},
        {"nrows": 3, "width": 1.0, "height": 1.0, "hspace": [0.1, 0.1, 0.1]},
    ],
)
def test_grid_inches_rejects_bad_counts_lengths_and_gaps(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        grid_inches(**kwargs)  # type: ignore[arg-type]


def test_grid_inches_creates_no_figure_when_rejecting() -> None:
    before = plt.get_fignums()
    with pytest.raises(ValueError):
        grid_inches(width=1.0, height=-1.0)
    assert plt.get_fignums() == before
