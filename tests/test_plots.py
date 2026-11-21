import math

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pytest

import mplplots
from mplplots.colors import SECONDARY_LINESTYLE
from mplplots.plots import box_axes, plot_distribution, plot_mean_sem, significance_stars

FILL, EDGE = "#c7e9c0", "#4f9d58"


@pytest.mark.parametrize(
    ("p", "stars"),
    [
        (0.0009, "***"),
        (0.001, "**"),
        (0.0099, "**"),
        (0.01, "*"),
        (0.049, "*"),
        (0.05, "n.s."),
        (1.0, "n.s."),
        (math.nan, "n.s."),
        (math.inf, "n.s."),
    ],
)
def test_significance_stars(p: float, stars: str) -> None:
    assert significance_stars(p) == stars


def test_significance_stars_treats_minus_infinity_as_not_significant() -> None:
    assert significance_stars(-math.inf) == "n.s."


def test_plot_mean_sem_draws_a_band_and_a_curve() -> None:
    _, ax = plt.subplots()
    line = plot_mean_sem(ax, [0, 1, 2], [1, 2, 3], [0.5, 0.5, 0.5], fill=FILL, edge=EDGE, label="s")
    assert line.get_linewidth() == 1.2
    assert line.get_alpha() == 0.95
    assert line.get_label() == "s"
    assert line.get_zorder() == 4.0
    assert mcolors.same_color(line.get_color(), EDGE)
    (band,) = ax.collections
    assert band.get_alpha() == 0.5
    assert band.get_zorder() == 3.0
    np.testing.assert_array_equal(np.asarray(band.get_facecolor())[0, :3], mcolors.to_rgb(FILL))
    heights = np.asarray(band.get_paths()[0].vertices)[:, 1]
    assert (heights.min(), heights.max()) == (0.5, 3.5)


def test_plot_mean_sem_returns_the_drawn_curve_and_a_borderless_band() -> None:
    _, ax = plt.subplots()
    line = plot_mean_sem(ax, [0, 1], [1, 2], [0.1, 0.1], fill=FILL, edge=EDGE)
    assert list(ax.lines) == [line]
    assert line.get_linestyle() == "-"
    assert str(line.get_label()).startswith("_")
    (band,) = ax.collections
    assert len(band.get_edgecolor()) == 0


def test_plot_mean_sem_keeps_float64_precision() -> None:
    _, ax = plt.subplots()
    x = [2.0**24, 2.0**24 + 1]
    line = plot_mean_sem(ax, x, [1.0 + 1e-9, 2.0], [0.1, 0.1], fill=FILL, edge=EDGE)
    np.testing.assert_array_equal(line.get_xdata(), x)
    np.testing.assert_array_equal(line.get_ydata(), [1.0 + 1e-9, 2.0])


@pytest.mark.parametrize("masked", ["x", "mean", "sem"])
def test_plot_mean_sem_leaves_out_masked_points(masked: str) -> None:
    _, ax = plt.subplots()
    values = {"x": [0.0, 1.0, 2.0], "mean": [1.0, 2.0, 3.0], "sem": [0.1, 0.1, 0.1]}
    values[masked][1] = 1e6
    arrays = {
        name: np.ma.array(v, mask=[False, name == masked, False]) for name, v in values.items()
    }
    plot_mean_sem(ax, arrays["x"], arrays["mean"], arrays["sem"], fill=FILL, edge=EDGE)
    np.testing.assert_allclose(ax.dataLim.intervalx, (0.0, 2.0))
    np.testing.assert_allclose(ax.dataLim.intervaly, (0.9, 3.1))


def test_plot_mean_sem_takes_a_linestyle() -> None:
    _, ax = plt.subplots()
    line = plot_mean_sem(
        ax, [0, 1], [1, 2], [0.1, 0.1], fill=FILL, edge=EDGE, linestyle=SECONDARY_LINESTYLE
    )
    assert line.is_dashed()


def test_plot_distribution_plots_percent_at_bin_centres() -> None:
    _, ax = plt.subplots()
    proxy = plot_distribution(ax, [0, 1, 2, 3], [10, 30, 60], 200, fill=FILL, edge=EDGE)
    (line,) = ax.lines
    np.testing.assert_allclose(np.asarray(line.get_xdata()), [0.5, 1.5, 2.5])
    np.testing.assert_allclose(np.asarray(line.get_ydata()), [5.0, 15.0, 30.0])
    assert line.get_linewidth() == 1.0
    assert mcolors.same_color(proxy.get_edgecolor(), EDGE)
    assert np.asarray(proxy.get_facecolor())[3] == 0.5
    assert proxy.get_linewidth() == 1.0


def test_plot_distribution_fills_to_zero_under_the_curve() -> None:
    _, ax = plt.subplots()
    proxy = plot_distribution(ax, [0, 1, 2, 3], [10, 30, 60], 200, fill=FILL, edge=EDGE)
    (line,) = ax.lines
    (wash,) = ax.collections
    heights = np.asarray(wash.get_paths()[0].vertices)[:, 1]
    assert (heights.min(), heights.max()) == (0.0, 30.0)
    np.testing.assert_allclose(np.asarray(wash.get_facecolor())[0], mcolors.to_rgba(FILL, 0.5))
    np.testing.assert_allclose(np.asarray(proxy.get_facecolor()), mcolors.to_rgba(FILL, 0.5))
    assert mcolors.same_color(line.get_color(), EDGE)
    assert line.get_alpha() is None
    assert wash.get_zorder() == 2.0
    assert line.get_zorder() > wash.get_zorder()


def test_plot_distribution_leaves_out_masked_bins() -> None:
    _, ax = plt.subplots()
    counts = np.ma.array([10, 10**6, 60], mask=[False, True, False])
    plot_distribution(ax, [0, 1, 2, 3], counts, 200, fill=FILL, edge=EDGE)
    (line,) = ax.lines
    np.testing.assert_array_equal(np.asarray(line.get_ydata()), [5.0, np.nan, 30.0])
    np.testing.assert_allclose(ax.dataLim.intervaly, (0.0, 30.0))


@pytest.mark.parametrize(
    ("edges", "counts", "n_total"), [([0, 1, 2], [1, 2, 3], 6), ([0, 1, 2], [1, 2], 0)]
)
def test_plot_distribution_rejects(edges: list[int], counts: list[int], n_total: int) -> None:
    _, ax = plt.subplots()
    with pytest.raises(ValueError):
        plot_distribution(ax, edges, counts, n_total, fill=FILL, edge=EDGE)


def test_box_axes_shows_four_spines_at_the_axes_line_width() -> None:
    with mplplots.context():
        _, ax = plt.subplots()
        box_axes(ax)
        assert all(spine.get_visible() for spine in ax.spines.values())
        assert {spine.get_linewidth() for spine in ax.spines.values()} == {0.8}
        assert ax.xaxis.get_ticks_position() == "bottom"
        assert ax.yaxis.get_ticks_position() == "left"
        box_axes(ax, linewidth=1.5)
        assert {spine.get_linewidth() for spine in ax.spines.values()} == {1.5}


def test_box_axes_reads_the_axes_line_width_of_the_active_style() -> None:
    with mplplots.context("GraphPadPrism"):
        _, ax = plt.subplots()
        box_axes(ax)
        assert {spine.get_linewidth() for spine in ax.spines.values()} == {1.0}


def test_box_axes_turns_off_top_and_right_ticks() -> None:
    _, ax = plt.subplots()
    ax.tick_params(which="both", top=True, right=True)
    box_axes(ax)
    assert ax.xaxis.get_ticks_position() == "bottom"
    assert ax.yaxis.get_ticks_position() == "left"
