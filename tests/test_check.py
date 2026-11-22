import json
import os
import subprocess
import sys
import warnings
from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredText
from matplotlib.text import Annotation, Text

import mplplots
from mplplots import check
from mplplots.check import RULES, Issue, StyleError, StyleWarning, assert_figure, check_figure

SEVERITY = {
    "font-size": "error",
    "font-weight": "error",
    "font-family": "error",
    "font-fallback": "warning",
    "script-glyph": "error",
    "unicode-minus": "warning",
    "spine-width": "error",
    "open-spines": "warning",
    "legend-frame": "error",
    "layout-engine": "error",
    "round-inches": "warning",
    "off-canvas": "error",
    "text-overlap": "warning",
    "panel-letter": "warning",
    "default-color": "warning",
}


@pytest.fixture
def clean() -> tuple[Figure, Axes]:
    """A 3 x 2 in Personal figure with axes at (0.6, 0.4) in, 2.2 x 1.4 in, and no issue."""
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    ax = fig.add_axes((0.6 / 3.0, 0.4 / 2.0, 2.2 / 3.0, 1.4 / 2.0))
    ax.plot([0, 1], [0, 1], color="#4f9d58", label="series")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")
    ax.legend()
    return fig, ax


def rules(issues: list[Issue]) -> set[str]:
    return {issue.rule for issue in issues}


def found(fig: Figure, rule: str, *, style: str = mplplots.DEFAULT_STYLE) -> list[Issue]:
    return [issue for issue in check_figure(fig, style=style) if issue.rule == rule]


def test_rules_table() -> None:
    assert list(RULES) == list(SEVERITY)
    assert all(RULES.values())


def test_a_clean_figure_has_no_issue_except_a_missing_font(clean: tuple[Figure, Axes]) -> None:
    assert rules(check_figure(clean[0])) <= {"font-fallback"}


Mutation = Callable[[Figure, Axes], object]

MUTATIONS: dict[str, Mutation] = {
    "font-size": lambda _fig, ax: ax.set_title("Title", fontsize=10),
    "font-weight": lambda _fig, ax: ax.set_xlabel("Time (s)", fontweight="bold"),
    "font-family": lambda _fig, ax: ax.text(0.5, 0.5, "serif", family="serif"),
    "script-glyph": lambda _fig, ax: ax.set_ylabel("Area (\u00c5\u00b2)"),
    "unicode-minus": lambda _fig, ax: ax.text(0.5, 0.5, "\u22122"),
    "spine-width": lambda _fig, ax: ax.spines["left"].set_linewidth(1.5),
    "open-spines": lambda _fig, ax: ax.spines["top"].set_visible(True),
    "legend-frame": lambda _fig, ax: ax.legend(frameon=True),
    "layout-engine": lambda fig, _ax: fig.set_layout_engine("tight"),
    "round-inches": lambda fig, _ax: fig.set_size_inches(3.03, 2.0),
    "off-canvas": lambda _fig, ax: ax.text(1.5, 0.5, "outside", transform=ax.transAxes),
    "text-overlap": lambda _fig, ax: ax.text(0.0, -0.11, "note", transform=ax.transAxes),
    "panel-letter": lambda fig, _ax: fig.text(0.02, 0.92, "a"),
    "default-color": lambda _fig, ax: ax.plot([0, 1], [1, 0]),
}


@pytest.mark.parametrize("rule", MUTATIONS)
def test_each_rule_fires_with_its_severity(clean: tuple[Figure, Axes], rule: str) -> None:
    fig, ax = clean
    MUTATIONS[rule](fig, ax)
    found = [issue for issue in check_figure(fig) if issue.rule == rule]
    assert found, rule
    assert {issue.severity for issue in found} == {SEVERITY[rule]}


def test_messages_name_the_artist(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_ylabel("Signal", fontsize=12)
    (issue,) = [issue for issue in check_figure(fig) if issue.rule == "font-size"]
    assert "Signal" in issue.message
    assert "12" in issue.message


def test_math_exponents_and_tick_letters_pass(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_ylabel("Area (\u00c5$^2$)")
    ax.bar(["A", "B", "C"], [1, 2, 3], color="#4f9d58")
    assert not rules(check_figure(fig)) & {"script-glyph", "panel-letter"}


def test_allow_font_sizes(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.text(0.5, 0.5, "small", fontsize=6)
    assert "font-size" in rules(check_figure(fig))
    assert "font-size" not in rules(check_figure(fig, allow_font_sizes=[6]))


def test_allow_font_weights(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.text(0.2, 0.5, "medium", fontweight=500)
    ax.text(0.6, 0.5, "bold", fontweight="bold")
    assert "font-weight" in rules(check_figure(fig))
    # A weight is allowed by name or by number, whichever way the text gives it.
    (issue,) = [i for i in check_figure(fig, allow_font_weights=[700]) if i.rule == "font-weight"]
    assert "'medium'" in issue.message
    assert "font-weight" not in rules(check_figure(fig, allow_font_weights=["medium", "bold"]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", StyleWarning)
        assert_figure(fig, allow_font_weights=[500, 700])  # Does not raise.
    with pytest.raises(ValueError, match="heavyish"):
        check_figure(fig, allow_font_weights=["heavyish"])


def test_hidden_artists_are_ignored(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Hidden", fontsize=20)
    ax.title.set_visible(False)
    hidden = fig.add_axes((0.11, 0.13, 0.2, 0.2))
    hidden.set_ylabel("Hidden", fontweight="bold")
    hidden.set_visible(False)
    assert not rules(check_figure(fig)) & {"font-size", "font-weight", "round-inches"}


def test_ignore_and_unknown_rule(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Title", fontsize=10)
    assert "font-size" not in rules(check_figure(fig, ignore={"font-size"}))
    with pytest.raises(ValueError, match="font-sise"):
        check_figure(fig, ignore={"font-sise"})


def test_the_expected_values_follow_the_named_style() -> None:
    mplplots.use("GraphPadPrism")
    fig = plt.figure(figsize=(3.0, 2.0))
    ax = fig.add_axes((0.2, 0.2, 0.7, 0.7))
    ax.plot([0, 1], [0, 1], color="#4f9d58")
    assert "spine-width" not in rules(check_figure(fig, style="GraphPadPrism"))
    assert "spine-width" in rules(check_figure(fig, style="Personal"))


def test_personal_messages_name_its_one_size_and_regular(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Title", fontsize=10)
    ax.set_xlabel("Time (s)", fontweight="bold")
    (size,) = found(fig, "font-size")
    assert size.message == "axes 0 title 'Title': font size 10 pt, expected 8 pt"
    (weight,) = found(fig, "font-weight")
    assert weight.message == "axes 0 x label 'Time (s)': font weight bold, expected regular"


def test_text_sizes_and_weights_come_from_the_style_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    style = tmp_path / "Sparse.mplstyle"
    style.write_text(
        "font.size: 10\naxes.titlesize: x-large\naxes.titleweight: bold\nxtick.labelsize: 9\n"
    )
    monkeypatch.setattr(check, "style_path", lambda _name: style)
    expected = check._Expected.read("Sparse")
    # A relative size resolves against the style's font.size, and a key the style omits takes
    # Matplotlib's default: "medium" axis labels, y tick labels and legend (10 pt), a "large"
    # figure title and figure labels (12 pt), and a legend title of font.size, all regular.
    assert expected.font_sizes == pytest.approx((9.0, 10.0, 12.0, 14.4))
    assert expected.font_weights == {400, 700}
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    fig.text(0.1, 0.5, "Note", fontsize=20, fontweight="light")
    (size,) = found(fig, "font-size", style="Sparse")
    assert size.message == "figure text 'Note': font size 20 pt, expected 9, 10, 12 or 14.4 pt"
    (weight,) = found(fig, "font-weight", style="Sparse")
    assert weight.message == "figure text 'Note': font weight light, expected regular or bold"


# Every rcParam that gives a kind of text its size or weight, listed here rather than read from
# check.py, so that a key missing there fails its case below.
TEXT_SIZE_KEYS = (
    "font.size",
    "axes.labelsize",
    "axes.titlesize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
    "figure.titlesize",
    "figure.labelsize",
)
TEXT_WEIGHT_KEYS = (
    "font.weight",
    "axes.labelweight",
    "axes.titleweight",
    "figure.titleweight",
    "figure.labelweight",
)


@pytest.mark.parametrize("key", TEXT_SIZE_KEYS)
def test_each_text_size_key_is_read(
    key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Every other size is 9 pt, so 13.5 pt can only come from the key under test.
    style = tmp_path / "Sizes.mplstyle"
    style.write_text(
        "".join(f"{other}: {13.5 if other == key else 9}\n" for other in TEXT_SIZE_KEYS)
    )
    monkeypatch.setattr(check, "style_path", lambda _name: style)
    assert check._Expected.read("Sizes").font_sizes == (9.0, 13.5)


@pytest.mark.parametrize("key", TEXT_WEIGHT_KEYS)
def test_each_text_weight_key_is_read(
    key: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Every other weight is regular, so semibold can only come from the key under test.
    style = tmp_path / "Weights.mplstyle"
    style.write_text(
        "".join(f"{other}: {600 if other == key else 'normal'}\n" for other in TEXT_WEIGHT_KEYS)
    )
    monkeypatch.setattr(check, "style_path", lambda _name: style)
    assert check._Expected.read("Weights").font_weights == {400, 600}


def test_font_fallback_is_one_warning(
    clean: tuple[Figure, Axes], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(check, "_installed", lambda _family: False)
    issues = check_figure(clean[0])
    assert [issue.rule for issue in issues].count("font-fallback") == 1
    assert "font-family" not in rules(issues)


def polar() -> Figure:
    fig = plt.figure()
    fig.add_subplot(projection="polar").plot([0, 1], [0, 1])
    return fig


def three_d() -> Figure:
    fig = plt.figure()
    fig.add_subplot(projection="3d").plot([0, 1], [0, 1], [0, 1])
    return fig


def twin_log_and_colorbar() -> Figure:
    fig, ax = plt.subplots()
    twin = ax.twinx()
    twin.set_yscale("log")
    twin.plot([0, 1], [1, 10])
    fig.colorbar(ax.imshow([[0, 1], [1, 0]]), ax=ax)
    return fig


def axis_off() -> Figure:
    fig, ax = plt.subplots()
    ax.axis("off")
    return fig


@pytest.mark.parametrize("build", [plt.figure, polar, three_d, twin_log_and_colorbar, axis_off])
def test_unusual_figures_do_not_crash(build: Callable[[], Figure]) -> None:
    mplplots.use()
    assert isinstance(check_figure(build()), list)


def test_assert_figure_passes_a_clean_figure(clean: tuple[Figure, Axes]) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", StyleWarning)
        assert_figure(clean[0])


def test_assert_figure_raises_on_errors(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Title", fontsize=10)
    with pytest.raises(StyleError, match="font-size"):
        assert_figure(fig)


def test_assert_figure_warns_or_raises_on_warnings(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.plot([0, 1], [1, 0])
    with pytest.warns(StyleWarning, match="default-color"):
        assert_figure(fig)
    with pytest.raises(StyleError, match="default-color"):
        assert_figure(fig, warnings_as_errors=True)


def test_assert_figure_warns_once_per_warning_and_raises_only_for_errors(
    clean: tuple[Figure, Axes], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(check, "_installed", lambda _family: True)
    fig, ax = clean
    ax.plot([0, 1], [1, 0])
    ax.plot([0, 1], [0.5, 0.5])
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert_figure(fig)
    messages = [str(w.message) for w in caught if issubclass(w.category, StyleWarning)]
    assert len(messages) == 2
    assert all(message.startswith("default-color: ") for message in messages)
    ax.set_title("Title", fontsize=10)
    with pytest.raises(StyleError) as raised:
        assert_figure(fig)
    assert [line.split(": ", 1)[0] for line in str(raised.value).splitlines()] == ["font-size"]
    with pytest.raises(StyleError) as raised:
        assert_figure(fig, warnings_as_errors=True)
    assert [line.split(": ", 1)[0] for line in str(raised.value).splitlines()] == [
        "font-size",
        "default-color",
        "default-color",
    ]


# Cases beyond the rule table: where a rule could misfire, and more unusual figures.


def test_messages_name_role_text_and_axes(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_xlabel("Time (s)", fontweight="bold")
    ax.spines["left"].set_linewidth(1.5)
    ax.plot([0, 1], [1, 0], label="fit")
    (weight,) = found(fig, "font-weight")
    assert weight.message.startswith("axes 0 x label 'Time (s)': ")
    assert "bold" in weight.message
    (spine,) = found(fig, "spine-width")
    assert spine.message.startswith("axes 0 left spine: ")
    assert "1.5" in spine.message
    (color,) = found(fig, "default-color")
    assert color.message.startswith("axes 0 Line2D 'fit': ")
    assert "#1f77b4" in color.message


def test_tick_labels_are_reported_once_per_axis(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.tick_params(axis="x", labelsize=6)
    (issue,) = found(fig, "font-size")
    assert issue.message.startswith("axes 0 x tick labels '")
    assert "'0.0'" in issue.message
    assert "6 pt" in issue.message


def test_math_text_and_italic_text_pass(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_xlabel("$t$ (s)")
    ax.set_ylabel(r"$\sin(x)$")
    ax.text(0.1, 0.6, r"$\mathrm{Cohen's}\ d = 0.52$" + "\n" + "$n = 3$", linespacing=1.35)
    ax.text(0.1, 0.3, "italic", fontstyle="italic")
    checked = {"font-size", "font-weight", "font-family", "script-glyph", "panel-letter"}
    assert not rules(check_figure(fig)) & checked


def test_figure_labels_legend_titles_and_colorbar_labels_pass_at_the_style_size() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    ax = fig.add_axes((0.6 / 3.0, 0.4 / 2.0, 1.6 / 3.0, 1.4 / 2.0))
    cax = fig.add_axes((2.4 / 3.0, 0.4 / 2.0, 0.1 / 3.0, 1.4 / 2.0))
    ax.plot([0, 1], [0, 1], color="#4f9d58", label="series")
    ax.legend(title="Group")
    colorbar = fig.colorbar(
        ax.imshow([[0, 1], [1, 0]], extent=(0, 1, 0, 1)), cax=cax, label="Level"
    )
    colorbar.outline.set_linewidth(0.6)
    fig.supxlabel("Time (s)", y=0.0, va="bottom")
    fig.suptitle("Overview", y=1.0, va="top")
    checked = {"font-size", "font-weight", "font-family", "spine-width", "open-spines"}
    assert not rules(check_figure(fig)) & checked


def test_legend_titles_figure_titles_and_colorbar_labels_are_checked() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    ax = fig.add_axes((0.6 / 3.0, 0.4 / 2.0, 1.6 / 3.0, 1.4 / 2.0))
    cax = fig.add_axes((2.4 / 3.0, 0.4 / 2.0, 0.1 / 3.0, 1.4 / 2.0))
    ax.plot([0, 1], [0, 1], color="#4f9d58", label="series")
    ax.legend(title="Group", title_fontsize=10)
    colorbar = fig.colorbar(ax.imshow([[0, 1], [1, 0]], extent=(0, 1, 0, 1)), cax=cax)
    colorbar.set_label("Level", fontsize=10)
    fig.suptitle("Overview", y=1.0, va="top", fontsize=10)
    messages = [issue.message for issue in found(fig, "font-size")]
    assert any(message.startswith("axes 0 legend title 'Group': ") for message in messages)
    assert any(message.startswith("axes 1 (color bar) y label 'Level': ") for message in messages)
    assert any(message.startswith("figure title 'Overview': ") for message in messages)
    assert len(messages) == 3


def test_single_letters_other_than_tick_labels_are_panel_letters(
    clean: tuple[Figure, Axes],
) -> None:
    fig, ax = clean
    ax.set_xticks([0.0, 1.0], labels=["A", "B"])
    ax.set_xlabel("$x$")
    ax.set_ylabel("(b)")
    ax.plot([0, 1], [0.5, 0.5], color="#dd6692", label="C")
    ax.legend(title="n")
    fig.supylabel("y")
    subjects = {issue.message.split(": ", 1)[0] for issue in found(fig, "panel-letter")}
    assert subjects == {
        "axes 0 y label '(b)'",
        "axes 0 legend label 'C'",
        "axes 0 legend title 'n'",
        "figure y label 'y'",
    }


def test_titles_and_anchored_text_can_be_panel_letters(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("(b)", loc="left")
    ax.add_artist(AnchoredText("C", loc="center", frameon=False))
    messages = [issue.message for issue in found(fig, "panel-letter")]
    assert len(messages) == 2
    assert any(message.startswith("axes 0 title '(b)': ") for message in messages)
    assert any(message.startswith("axes 0 text 'C': ") for message in messages)


def test_tick_labels_outside_the_view_are_not_inspected() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    # The axes reach the top edge of the canvas.
    ax = fig.add_axes((0.6 / 3.0, 0.4 / 2.0, 2.2 / 3.0, 1.6 / 2.0))
    ax.plot([0, 1], [0, 1], color="#4f9d58")
    ax.set_ylim(0.05, 0.95)
    # The locator proposes a tick above the view whose label would cross the top edge.
    assert max(ax.yaxis.get_majorticklocs()) > 0.95
    assert not found(fig, "off-canvas")


@pytest.mark.parametrize(("width", "reported"), [(3.0009, False), (3.0011, True)])
def test_round_inches_tolerates_a_thousandth_of_an_inch(
    clean: tuple[Figure, Axes], width: float, reported: bool
) -> None:
    fig, _ = clean
    fig.set_size_inches(width, 2.0)
    assert any(issue.message.startswith("figure: ") for issue in found(fig, "round-inches")) is (
        reported
    )


@pytest.mark.parametrize(("overhang", "reported"), [(0.4, False), (0.6, True)])
def test_off_canvas_tolerates_half_a_pixel(
    clean: tuple[Figure, Axes], overhang: float, reported: bool
) -> None:
    fig, _ = clean
    text = fig.text(0.5, 0.5, "Edge")
    fig.draw_without_rendering()
    # Shift the text so that its left edge lies `overhang` pixels left of the canvas.
    text.set_x(0.5 - (text.get_window_extent().x0 + overhang) / fig.bbox.width)
    fig.draw_without_rendering()
    assert text.get_window_extent().x0 == pytest.approx(-overhang, abs=1e-6)
    assert bool(found(fig, "off-canvas")) is reported


def test_a_legend_off_the_canvas_is_reported(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    (issue,) = found(fig, "off-canvas")
    assert issue.message.startswith("axes 0 legend 'series': ")
    assert "right" in issue.message


def test_a_legend_kept_with_add_artist_is_checked_as_a_legend(clean: tuple[Figure, Axes]) -> None:
    # Matplotlib's way to show two legends on one axes: keep the first with add_artist.
    fig, ax = clean
    (line,) = ax.lines
    (other,) = ax.plot([0, 1], [1, 0], color="#dd6692", label="other")
    first = ax.legend(handles=[line], loc="upper left", frameon=True, title="A", title_fontsize=10)
    ax.add_artist(first)
    ax.legend(handles=[other], loc="lower right")
    (frame,) = found(fig, "legend-frame")
    assert frame.message.startswith("axes 0 legend 'A': ")
    (size,) = found(fig, "font-size")
    assert size.message.startswith("axes 0 legend title 'A': ")
    (letter,) = found(fig, "panel-letter")
    assert letter.message.startswith("axes 0 legend title 'A': ")


def test_a_legend_kept_with_add_artist_off_the_canvas_is_reported_as_a_legend(
    clean: tuple[Figure, Axes],
) -> None:
    fig, ax = clean
    (line,) = ax.lines
    (other,) = ax.plot([0, 1], [1, 0], color="#dd6692", label="other")
    ax.add_artist(ax.legend(handles=[line], loc="upper left", bbox_to_anchor=(1.0, 1.0)))
    ax.legend(handles=[other], loc="lower right")
    (issue,) = found(fig, "off-canvas")
    assert issue.message.startswith("axes 0 legend 'series': ")
    assert "right" in issue.message


def test_a_legend_that_is_also_kept_with_add_artist_is_reported_once(
    clean: tuple[Figure, Axes],
) -> None:
    fig, ax = clean
    ax.add_artist(ax.legend(frameon=True))
    assert len(found(fig, "legend-frame")) == 1


def test_artists_added_to_the_figure_are_checked(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    fig.add_artist(Text(0.5, 0.5, "Note", fontsize=10))
    fig.add_artist(Text(1.02, 0.5, "Outside"))
    fig.add_artist(
        Annotation("Arrow", xy=(0.5, 0.3), xycoords="figure fraction", fontweight="bold")
    )
    fig.add_artist(Line2D([0.1, 0.9], [0.05, 0.05]))  # Matplotlib's default line color, C0.
    fig.add_artist(Legend(fig, [ax.lines[0]], ["Key"], frameon=True))
    sub = fig.subfigures(1, 1, squeeze=False)[0, 0]
    sub.add_artist(Text(0.5, 0.9, "Sub", fontsize=10))
    subjects = {
        rule: [issue.message.split(": ", 1)[0] for issue in found(fig, rule)]
        for rule in ("font-size", "font-weight", "off-canvas", "default-color", "legend-frame")
    }
    assert subjects == {
        "font-size": ["figure text 'Note'", "subfigure 0 text 'Sub'"],
        "font-weight": ["figure annotation 'Arrow'"],
        "off-canvas": ["figure text 'Outside'"],
        "default-color": ["figure Line2D"],
        "legend-frame": ["figure legend 'Key'"],
    }


def test_artists_in_hidden_containers_are_ignored(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.legend(title="Hidden", title_fontsize=20, frameon=True).set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_xlabel("Hidden", fontsize=20)
    ax.text(0.5, 0.5, "", fontsize=20)
    ax.text(0.5, 0.5, "   ", fontsize=20)
    ax.text(0.5, 0.5, "Hidden", fontsize=20, visible=False)
    ax.plot([0, 1], [1, 0], visible=False)
    sub = fig.subfigures(1, 1, squeeze=False)[0, 0]
    sub.text(0.5, 0.5, "Hidden", fontsize=20)
    sub.add_axes((0.11, 0.13, 0.2, 0.2)).set_title("Hidden", fontsize=20)
    sub.set_visible(False)
    hidden = {"font-size", "legend-frame", "default-color", "round-inches"}
    assert not rules(check_figure(fig)) & hidden


def test_spines_that_are_not_drawn_are_ignored(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.spines["top"].set_linewidth(2.0)  # hidden by the style
    assert not found(fig, "spine-width")
    ax.spines["left"].set_linewidth(2.0)
    ax.set_frame_on(False)
    assert not found(fig, "spine-width")


def test_the_right_spine_of_a_twin_axis_is_not_open(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    twin = ax.twinx()
    twin.spines["right"].set_visible(True)
    twin.plot([0, 1], [1, 2], color="#dd6692")
    assert not found(fig, "open-spines")


def test_marks_that_show_no_default_color_pass(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.plot([0, 1], [1, 0], "o")  # The style's markers are black; the C0 line is not drawn.
    ax.scatter([0, 1], [0, 1], c=[0.0, 1.0])  # Color-mapped.
    ax.plot([0, 1], [0.2, 0.2], color="C0", visible=False)
    assert not found(fig, "default-color")


def test_default_colors_in_bars_and_bands_are_reported(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.bar([0.5], [0.5], width=0.2)
    ax.fill_between([0, 1], [0, 0.1], [0.2, 0.3])
    messages = [issue.message for issue in found(fig, "default-color")]
    assert any("Rectangle" in message for message in messages)
    assert any("Collection" in message for message in messages)


def test_unicode_minus_follows_the_style(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.plot([-1, 0], [-1, 0], color="#4f9d58")  # Negative tick labels use the hyphen-minus.
    assert not found(fig, "unicode-minus")
    ax.text(0.5, 0.5, "\u22122")
    assert found(fig, "unicode-minus")
    assert not found(fig, "unicode-minus", style="GraphPadPrism")


# Constrained layout warns about axes placed with add_axes; the warning is about the figure.
@pytest.mark.filterwarnings("ignore:There are no gridspecs with layoutgrids:UserWarning")
def test_only_tight_and_constrained_layout_engines_are_reported(
    clean: tuple[Figure, Axes],
) -> None:
    fig, _ = clean
    fig.set_layout_engine("tight")
    fig.set_layout_engine("none")  # Leaves a placeholder engine that moves nothing.
    assert not found(fig, "layout-engine")
    fig.set_layout_engine("constrained")
    (issue,) = found(fig, "layout-engine")
    assert "ConstrainedLayoutEngine" in issue.message


def test_axes_in_subfigures_are_measured_in_inches() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(4.0, 2.0))
    left, right = fig.subfigures(1, 2, squeeze=False)[0]
    for sub in (left, right):
        # 0.5 in from the left and 0.4 in from the bottom of a 2 x 2 in subfigure, 1.4 x 1.4 in.
        sub.add_axes((0.25, 0.2, 0.7, 0.7)).plot([0, 1], [0, 1], color="#4f9d58")
    assert not found(fig, "round-inches")


def test_fixed_aspect_axes_placed_in_inches_are_on_the_grid() -> None:
    # A fixed aspect shrinks the drawn axes inside the box that the axes locator places; the
    # box, not the shrunk axes, is the layout. The color bar recipe of add_axes_inches.
    mplplots.use()
    fig, (ax, cax) = mplplots.grid_inches(
        1, 2, width=[2.0, 0.1], height=1.5, wspace=0.15, right=0.6, top=0.35
    )
    fig.colorbar(ax.imshow(np.arange(21.0).reshape(3, 7)), cax=cax, label="Value")
    boxed = mplplots.add_axes_inches(fig, 0.6, 0.0, 0.5, 0.3)
    boxed.set_box_aspect(1.0)
    boxed.set_axis_off()
    assert not found(fig, "round-inches")
    fig.set_size_inches(3.5, 2.5)  # The locators keep every box in inches.
    assert not found(fig, "round-inches")


@pytest.mark.parametrize("extend", ["min", "max", "both"])
def test_a_color_bar_with_extensions_is_measured_by_the_box_it_was_given(extend: str) -> None:
    # Matplotlib shrinks a color bar's axes by its extensions at each draw; the layout is the
    # box the axes were given, with or without an axes locator.
    mplplots.use()
    fig, (ax, cax) = mplplots.grid_inches(
        1, 2, width=[2.0, 0.1], height=1.5, wspace=0.15, right=0.6
    )
    image = ax.imshow(np.arange(21.0).reshape(3, 7), aspect="auto")
    fig.colorbar(image, cax=cax, extend=extend)
    assert not found(fig, "round-inches")

    fig = plt.figure(figsize=(3.0, 2.0))
    ax = fig.add_axes((0.2, 0.2, 0.6, 0.7))  # 0.6, 0.4 in; 1.8 x 1.4 in
    cax = fig.add_axes((0.85, 0.2, 0.05, 0.7))  # 2.55, 0.4 in; 0.15 x 1.4 in
    fig.colorbar(ax.imshow(np.zeros((3, 7)), aspect="auto"), cax=cax, extend=extend)
    assert not found(fig, "round-inches")


def test_a_color_bar_with_extensions_placed_off_the_grid_is_reported() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    ax = mplplots.add_axes_inches(fig, 0.6, 0.4, 1.8, 1.4)
    cax = mplplots.add_axes_inches(fig, 2.53, 0.4, 0.1, 1.4)
    fig.colorbar(ax.imshow(np.zeros((3, 7)), aspect="auto"), cax=cax, extend="both")
    (issue,) = found(fig, "round-inches")
    assert "position (2.53, 0.4) in and size 0.1 x 1.4 in" in issue.message


def test_a_color_bar_outline_is_as_wide_as_a_minor_tick() -> None:
    mplplots.use()
    fig, (ax, cax) = mplplots.grid_inches(
        1, 2, width=[2.0, 0.1], height=1.5, wspace=0.15, right=0.6
    )
    colorbar = fig.colorbar(ax.imshow(np.zeros((3, 7)), aspect="auto"), cax=cax)
    (issue,) = found(fig, "spine-width")
    assert issue.message == (
        "axes 1 (color bar) outline spine: line width 0.8 pt, expected 0.6 pt, the minor tick width"
    )
    colorbar.outline.set_linewidth(0.6)
    assert not found(fig, "spine-width")


def test_a_color_bar_outline_follows_the_style_that_is_checked() -> None:
    # GraphPadPrism draws axis lines and minor ticks at 1 pt, so the default outline passes.
    with mplplots.context("GraphPadPrism"):
        fig = plt.figure(figsize=(3.0, 2.0))
        ax = mplplots.add_axes_inches(fig, 0.6, 0.4, 1.8, 1.4)
        cax = mplplots.add_axes_inches(fig, 2.55, 0.4, 0.1, 1.4)
        fig.colorbar(ax.imshow(np.zeros((3, 7)), aspect="auto"), cax=cax)
        issues = check_figure(fig, style="GraphPadPrism")
    assert "spine-width" not in rules(issues)


def test_a_fixed_aspect_axes_placed_off_the_grid_is_reported() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(3.0, 2.0))
    mplplots.add_axes_inches(fig, 0.63, 0.4, 2.2, 1.4).imshow(np.zeros((3, 7)))
    (issue,) = found(fig, "round-inches")
    assert "position (0.63, 0.4) in and size 2.2 x 1.4 in" in issue.message


def test_each_overlap_is_reported_once_under_the_first_text(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.text(0.5, 0.5, "first")
    ax.text(0.5, 0.5, "second")
    ax.text(0.52, 0.52, "third")
    issues = found(fig, "text-overlap")
    assert [issue.message for issue in issues] == [
        "axes 0 text 'first': overlaps axes 0 text 'second', 'third'",
        "axes 0 text 'second': overlaps axes 0 text 'third'",
    ]
    assert {issue.severity for issue in issues} == {"warning"}


def test_texts_that_only_touch_do_not_overlap(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.text(0.5, 0.5, "upper", va="bottom")
    lower = ax.text(0.5, 0.5, "lower", va="top")
    assert not found(fig, "text-overlap")
    to_data = ax.transData.inverted().transform
    point = (to_data((0.0, fig.dpi / 72.0)) - to_data((0.0, 0.0)))[1]  # 1 pt in data units
    lower.set_y(0.5 + 0.4 * point)  # The line boxes are 0.4 pt into each other.
    assert not found(fig, "text-overlap")
    lower.set_y(0.5 + 2.0 * point)
    (issue,) = found(fig, "text-overlap")
    assert issue.message == "axes 0 text 'upper': overlaps axes 0 text 'lower'"


def test_the_arrow_of_an_annotation_is_not_part_of_its_text(clean: tuple[Figure, Axes]) -> None:
    # The extent of an annotation spans its arrow as well, which may pass close to other text.
    fig, ax = clean
    ax.annotate("note", xy=(0.1, 0.1), xytext=(0.6, 0.6), arrowprops={"arrowstyle": "->"})
    ax.text(0.2, 0.42, "label")
    assert not found(fig, "text-overlap")
    ax.text(0.6, 0.6, "over the note")
    (issue,) = found(fig, "text-overlap")
    assert issue.message == "axes 0 annotation 'note': overlaps axes 0 text 'over the note'"


def test_crowded_tick_labels_are_reported_per_axis(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_xlim(0.0, 1.0)
    ax.set_xticks(np.linspace(0.0, 1.0, 41))
    (issue,) = found(fig, "text-overlap")
    assert issue.message.startswith("axes 0 x tick labels '0.000', '0.025', ")
    assert issue.message.endswith(": overlap each other")


def test_a_legend_entry_over_a_text_is_reported(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    legend = ax.get_legend()
    assert legend is not None
    fig.draw_without_rendering()
    box = legend.get_texts()[0].get_window_extent()
    x, y = ax.transData.inverted().transform((box.x0, box.y0))
    ax.text(x, y, "over the legend", va="bottom")
    (issue,) = found(fig, "text-overlap")
    assert "legend label 'series'" in issue.message
    assert "'over the legend'" in issue.message


def test_rotated_texts_are_not_compared(clean: tuple[Figure, Axes]) -> None:
    # The bounding boxes of labels turned by 30 degrees overlap although the labels do not.
    fig, ax = clean
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0], ["alpha-one", "beta-two", "gamma", "delta", "eps"])
    ax.tick_params(axis="x", labelrotation=30)
    ax.set_xlabel("")
    assert not found(fig, "text-overlap")
    for label in ax.get_xticklabels():
        label.set_rotation(90)  # A quarter turn keeps the box exact.
    assert not found(fig, "text-overlap")


def test_clipped_and_hidden_texts_do_not_overlap(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.text(0.5, 0.5, "shown")
    ax.text(0.5, 0.5, "hidden", visible=False)
    ax.text(5.0, 5.0, "clipped away", clip_on=True)
    ax.text(5.0, 5.0, "clipped too", clip_on=True)
    assert not found(fig, "text-overlap")


def test_an_empty_figure_has_no_issue(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check, "_installed", lambda _family: False)
    mplplots.use()
    assert check_figure(plt.figure(figsize=(3.0, 2.0))) == []


def test_installed() -> None:
    assert check._installed("DejaVu Sans")
    assert not check._installed("No Such Font Family")


def test_ignore_accepts_a_single_rule_id(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Title", fontsize=10)
    assert "font-size" not in rules(check_figure(fig, ignore="font-size"))


def test_unknown_style_is_rejected(clean: tuple[Figure, Axes]) -> None:
    with pytest.raises(ValueError, match="GraphPadPrism, Personal"):
        check_figure(clean[0], style="Nope")


def test_style_error_lists_one_line_per_issue(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.set_title("Title", fontsize=10)
    ax.set_xlabel("Time (s)", fontweight="bold")
    with pytest.raises(StyleError) as raised:
        assert_figure(fig)
    lines = str(raised.value).splitlines()
    assert [line.split(": ", 1)[0] for line in lines] == ["font-size", "font-weight"]


def images_insets_and_tables() -> Figure:
    fig, ax = plt.subplots()
    ax.imshow([[0, 1], [1, 0]])
    fig.figimage([[0, 1], [1, 0]])
    ax.inset_axes((0.6, 0.6, 0.3, 0.3)).plot([0, 1], [0, 1])
    ax.secondary_xaxis("top")
    ax.table(cellText=[["1", "2"]], loc="bottom")
    ax.add_artist(AnchoredText("note", loc="upper left"))
    return fig


def subfigures_and_3d_text() -> Figure:
    fig = plt.figure()
    left, right = fig.subfigures(1, 2, squeeze=False)[0]
    left.suptitle("Left")
    left.add_subplot().plot([0, 1], [0, 1])
    ax3d = right.add_subplot(projection="3d")
    ax3d.text(0, 0, 0, "origin")
    ax3d.set_zlabel("z")
    return fig


def empty_log_axes() -> Figure:
    fig, ax = plt.subplots()
    ax.set_xscale("log")
    ax.set_yscale("log")
    return fig


def hidden_figure() -> Figure:
    fig, ax = plt.subplots()
    ax.set_title("Hidden", fontsize=20)
    fig.set_visible(False)
    return fig


@pytest.mark.parametrize(
    "build", [images_insets_and_tables, subfigures_and_3d_text, empty_log_axes, hidden_figure]
)
def test_more_unusual_figures_do_not_crash(build: Callable[[], Figure]) -> None:
    mplplots.use()
    assert isinstance(check_figure(build()), list)


def test_check_figure_leaves_3d_tick_labels_where_the_draw_put_them() -> None:
    mplplots.use()
    fig = plt.figure(figsize=(4.0, 3.0))
    ax = fig.add_subplot(projection="3d")
    ax.plot([0, 1], [0, 1], [0, 1], color="#4f9d58")
    fig.draw_without_rendering()
    before = [tick.label1.get_position() for tick in ax.xaxis.get_major_ticks()]
    issues = check_figure(fig)
    assert [tick.label1.get_position() for tick in ax.xaxis.get_major_ticks()] == before
    assert "off-canvas" not in rules(issues)
    # The recorder removes the wrapper it puts on each axis for the draw.
    assert "_update_ticks" not in vars(ax.xaxis)
    assert "_update_ticks" not in vars(ax.yaxis)


def test_secondary_and_inset_axes_are_checked(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.secondary_xaxis("top").set_xlabel("Frequency (Hz)", fontsize=10)
    inset = ax.inset_axes((0.1, 0.5, 0.3, 0.3))
    inset.set_title("Zoom", fontweight="bold")
    (size,) = found(fig, "font-size")
    assert size.message.startswith("axes 0 child 0 x label 'Frequency (Hz)': ")
    (weight,) = found(fig, "font-weight")
    assert weight.message.startswith("axes 0 child 1 title 'Zoom': ")
    assert not found(fig, "open-spines")


# Runs in a fresh interpreter, because Matplotlib caches font lookups per process. Removing
# every family of the style's list except DejaVu Sans from the font list before any lookup
# stands in for a machine without Arial and its metric clones.
FALLBACK_SCRIPT = r"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import mplplots
from mplplots.check import check_figure

hidden = set(sys.argv[1:])
fm.fontManager.ttflist[:] = [f for f in fm.fontManager.ttflist if f.name not in hidden]
matplotlib.rcdefaults()
mplplots.use()
fig = plt.figure(figsize=(3.0, 2.0))
ax = fig.add_axes((0.6 / 3.0, 0.4 / 2.0, 2.2 / 3.0, 1.4 / 2.0))
ax.plot([0, 1], [0, 1], color="#4f9d58", label="series")
ax.set_xlabel("$t$ (s)")
ax.set_ylabel("Signal")
ax.legend()
issues = check_figure(fig)
print(json.dumps({
    "text_font": fm.get_font(fm.findfont(ax.xaxis.label.get_fontproperties())).family_name,
    "issues": [[issue.rule, issue.severity] for issue in issues],
}))
"""


def test_without_arial_the_only_issue_is_one_font_fallback_warning() -> None:
    hidden = ["Arial", "Helvetica", "Liberation Sans", "Arimo", "Nimbus Sans"]
    result = subprocess.run(
        [sys.executable, "-c", FALLBACK_SCRIPT, *hidden],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout.strip().splitlines()[-1])
    assert report["text_font"] == "DejaVu Sans"
    assert report["issues"] == [["font-fallback", "warning"]]
