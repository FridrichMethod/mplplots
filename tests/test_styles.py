"""Tests for mplplots styles."""

import matplotlib
import matplotlib.pyplot as plt

import mplplots

STYLE_PATH = mplplots.STYLE_PATH


class TestGraphPadPrismStyle:
    def test_style_file_exists(self) -> None:
        assert (STYLE_PATH).is_file()

    def test_style_is_loadable(self) -> None:
        style_path = str(STYLE_PATH)
        plt.style.use(style_path)

    def test_style_sets_dpi(self) -> None:
        mplplots.prism_style()
        assert matplotlib.rcParams["figure.dpi"] == 300

    def test_style_hides_top_right_spines(self) -> None:
        mplplots.prism_style()
        assert matplotlib.rcParams["axes.spines.top"] is False
        assert matplotlib.rcParams["axes.spines.right"] is False

    def test_style_applies_to_plot(self) -> None:
        style_path = str(STYLE_PATH)
        with plt.style.context(style_path):
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3], [1, 4, 9])
            assert ax.spines["top"].get_visible() is False
            assert ax.spines["right"].get_visible() is False
            plt.close(fig)
