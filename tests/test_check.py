import json
import os
import subprocess
import sys
import warnings
from collections.abc import Callable

import matplotlib.pyplot as plt
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
    fig.colorbar(ax.imshow([[0, 1], [1, 0]], extent=(0, 1, 0, 1)), cax=cax, label="Level")
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
    assert any(message.startswith("axes 1 (colour bar) y label 'Level': ") for message in messages)
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
    fig.add_artist(Line2D([0.1, 0.9], [0.05, 0.05]))  # Matplotlib's default line colour, C0.
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


def test_marks_that_show_no_default_colour_pass(clean: tuple[Figure, Axes]) -> None:
    fig, ax = clean
    ax.plot([0, 1], [1, 0], "o")  # The style's markers are black; the C0 line is not drawn.
    ax.scatter([0, 1], [0, 1], c=[0.0, 1.0])  # Colour-mapped.
    ax.plot([0, 1], [0.2, 0.2], color="C0", visible=False)
    assert not found(fig, "default-color")


def test_default_colours_in_bars_and_bands_are_reported(clean: tuple[Figure, Axes]) -> None:
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
