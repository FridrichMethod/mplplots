from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from matplotlib.figure import Figure

from mplplots.export import FORMATS, save_figure


def make_figure() -> Figure:
    fig = plt.figure(figsize=(3, 2))
    ax = fig.add_axes((0.2, 0.25, 0.7, 0.65))
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("Label text")
    return fig


def test_formats() -> None:
    assert FORMATS == ("png", "pdf", "svg")


def test_writes_every_format_and_creates_directories(tmp_path: Path) -> None:
    paths = save_figure(make_figure(), tmp_path / "out" / "fig01")
    assert [path.name for path in paths] == ["fig01.png", "fig01.pdf", "fig01.svg"]
    assert all(path.is_file() for path in paths)


def test_a_stem_with_a_dot_is_kept(tmp_path: Path) -> None:
    (png,) = save_figure(make_figure(), tmp_path / "fig1.v2", formats=["png"])
    assert png.name == "fig1.v2.png"


def test_accepts_a_string_path(tmp_path: Path) -> None:
    (png,) = save_figure(make_figure(), str(tmp_path / "f"), formats=["png"])
    assert png == tmp_path / "f.png"
    assert png.is_file()


def test_returns_paths_in_the_order_of_formats(tmp_path: Path) -> None:
    paths = save_figure(make_figure(), tmp_path / "f", formats=["svg", "png"])
    assert [path.name for path in paths] == ["f.svg", "f.png"]


def test_file_has_the_figure_size_even_when_rc_crops(tmp_path: Path) -> None:
    with plt.rc_context({"savefig.bbox": "tight"}):
        (png,) = save_figure(make_figure(), tmp_path / "f", formats=["png"], dpi=100)
    assert plt.imread(png).shape[:2] == (200, 300)


def test_vector_files_have_the_figure_size_even_when_rc_crops(tmp_path: Path) -> None:
    # A 3 x 2 in figure is 216 x 144 pt.
    with plt.rc_context({"savefig.bbox": "tight", "savefig.pad_inches": 0.5}):
        pdf, svg = save_figure(make_figure(), tmp_path / "f", formats=["pdf", "svg"])
    assert b"/MediaBox [ 0 0 216 144 ]" in pdf.read_bytes()
    assert 'width="216pt" height="144pt"' in svg.read_text()


def test_crop_trims_to_the_drawn_content(tmp_path: Path) -> None:
    (png,) = save_figure(make_figure(), tmp_path / "f", formats=["png"], dpi=100, crop=True)
    assert plt.imread(png).shape[:2] != (200, 300)


def test_crop_keeps_a_margin_of_two_hundredths_of_an_inch(tmp_path: Path) -> None:
    fig = make_figure()
    fig.draw_without_rendering()
    tight = fig.get_tightbbox()  # In inches.
    (png,) = save_figure(fig, tmp_path / "f", formats=["png"], dpi=100, crop=True)
    height, width = plt.imread(png).shape[:2]
    assert width == pytest.approx((tight.width + 2 * 0.02) * 100, abs=1)
    assert height == pytest.approx((tight.height + 2 * 0.02) * 100, abs=1)


def test_dpi_defaults_to_rcparams(tmp_path: Path) -> None:
    with plt.rc_context({"savefig.dpi": 200}):
        (png,) = save_figure(make_figure(), tmp_path / "f", formats=["png"])
    assert plt.imread(png).shape[:2] == (400, 600)


def test_output_is_deterministic(tmp_path: Path) -> None:
    first = save_figure(make_figure(), tmp_path / "a")
    second = save_figure(make_figure(), tmp_path / "b")
    for one, two in zip(first, second, strict=True):
        assert one.read_bytes() == two.read_bytes(), one.suffix


def test_other_raster_formats_are_deterministic(tmp_path: Path) -> None:
    first = save_figure(make_figure(), tmp_path / "a", formats=["tif", "jpg"])
    second = save_figure(make_figure(), tmp_path / "b", formats=["tif", "jpg"])
    for one, two in zip(first, second, strict=True):
        assert one.read_bytes() == two.read_bytes(), one.suffix


def test_svg_text_is_paths_unless_editable(tmp_path: Path) -> None:
    (paths_svg,) = save_figure(make_figure(), tmp_path / "paths", formats=["svg"])
    assert "<text" not in paths_svg.read_text()
    (text_svg,) = save_figure(
        make_figure(), tmp_path / "text", formats=["svg"], editable_svg_text=True
    )
    assert "Label text" in text_svg.read_text()


def test_save_settings_do_not_leak_into_rcparams(tmp_path: Path) -> None:
    with plt.rc_context({"savefig.bbox": "tight", "svg.fonttype": "none"}):
        (svg,) = save_figure(make_figure(), tmp_path / "f", formats=["svg"])
        assert plt.rcParams["savefig.bbox"] == "tight"
        assert plt.rcParams["svg.fonttype"] == "none"
    assert "<text" not in svg.read_text()


def test_writes_every_format_from_a_single_format_canvas(tmp_path: Path) -> None:
    # A pdf, svg, ps or pgf backend gives figures a canvas that prints only its own formats;
    # Figure.savefig switches to another canvas for the rest.
    fig = Figure(figsize=(3, 2))
    FigureCanvasPdf(fig)
    paths = save_figure(fig, tmp_path / "f")
    assert [path.suffix for path in paths] == [".png", ".pdf", ".svg"]
    assert all(path.stat().st_size > 0 for path in paths)


def test_writes_pgf_reproducibly(tmp_path: Path) -> None:
    # The pgf printer takes no metadata. A figure without text needs no LaTeX to save as pgf.
    def text_free_figure() -> Figure:
        fig = plt.figure(figsize=(3, 2))
        ax = fig.add_axes((0.2, 0.25, 0.7, 0.65))
        ax.plot([0, 1], [0, 1])
        ax.set_axis_off()
        return fig

    first = save_figure(text_free_figure(), tmp_path / "a", formats=["png", "pgf"])
    second = save_figure(text_free_figure(), tmp_path / "b", formats=["pgf"])
    assert [path.name for path in first] == ["a.png", "a.pgf"]
    assert "\\begin{pgfpicture}" in first[1].read_text()
    assert first[1].read_bytes() == second[0].read_bytes()


def test_caption_sidecar(tmp_path: Path) -> None:
    paths = save_figure(make_figure(), tmp_path / "f", formats=["png"], caption="  A caption.\n\n")
    assert [path.name for path in paths] == ["f.png", "f_caption.txt"]
    assert paths[-1].read_text() == "A caption.\n"


@pytest.mark.parametrize("caption", [None, "", "   "])
def test_no_caption_file_without_a_caption(tmp_path: Path, caption: str | None) -> None:
    paths = save_figure(make_figure(), tmp_path / "f", formats=["png"], caption=caption)
    assert [path.name for path in paths] == ["f.png"]


def test_closes_the_figure_unless_told_not_to(tmp_path: Path) -> None:
    fig = make_figure()
    save_figure(fig, tmp_path / "a", formats=["png"], close=False)
    assert plt.fignum_exists(fig.number)
    save_figure(fig, tmp_path / "b", formats=["png"])
    assert not plt.fignum_exists(fig.number)


@pytest.mark.parametrize("formats", [[], ["png", "xyz"]])
def test_rejects_bad_formats_before_writing(tmp_path: Path, formats: list[str]) -> None:
    with pytest.raises(ValueError):
        save_figure(make_figure(), tmp_path / "f", formats=formats)
    assert list(tmp_path.iterdir()) == []
