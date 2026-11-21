import re
import subprocess
import sys
from importlib.resources import files
from pathlib import Path
from types import ModuleType

import matplotlib.pyplot as plt
import numpy as np
import pytest

import mplplots as mpp
from mplplots import check, colors, export, layout, plots, styles

PUBLIC = (
    "BAND_ALPHA", "COLUMN_WIDTHS", "DEFAULT_STYLE", "LINE_ALPHA", "REFERENCE_LINE",
    "SCATTER_ALPHA", "SECONDARY_LINESTYLE", "STYLES", "STYLE_PATH", "ColorPair", "Issue",
    "StyleError", "StyleWarning", "add_axes_inches", "add_custom_fonts", "add_shared_ylabel",
    "align_legends_left", "assert_figure", "auto_ticks", "box_axes", "check_figure",
    "check_palette", "context", "contrast_ratio", "darken", "figure_size", "get_colors",
    "grid_inches", "legend_inches", "lighten", "plot_distribution", "plot_mean_sem",
    "prism_style", "save_figure", "set_palette", "significance_stars", "style_path",
    "suptitle_inches", "use",
)  # fmt: skip
DOCUMENTS = ("SKILL.md", "references/style-guide.md")
PYTHON_BLOCK = re.compile(r"^```python\n(.*?)^```", re.MULTILINE | re.DOTALL)
TOOLKIT_MODULES = (styles, colors, layout, export, plots, check)


def test_public_names() -> None:
    assert set(PUBLIC) <= set(mpp.__all__)
    assert all(hasattr(mpp, name) for name in PUBLIC)


@pytest.mark.parametrize("module", TOOLKIT_MODULES, ids=lambda module: module.__name__)
def test_every_toolkit_name_is_exported(module: ModuleType) -> None:
    for name in module.__all__:
        assert name in mpp.__all__, name
        assert getattr(mpp, name) is getattr(module, name), name


def test_all_names_resolve_once() -> None:
    assert len(set(mpp.__all__)) == len(mpp.__all__)
    assert all(hasattr(mpp, name) for name in mpp.__all__)
    assert "__version__" in mpp.__all__


def test_importing_mplplots_leaves_rcparams_alone() -> None:
    script = (
        "import matplotlib; before = dict(matplotlib.rcParams); "
        "import mplplots; assert dict(matplotlib.rcParams) == before"
    )
    subprocess.run([sys.executable, "-c", script], check=True)


def test_importing_mplplots_does_not_load_pyplot() -> None:
    # pyplot picks a GUI backend on import, which a library should leave to the caller.
    script = "import sys, mplplots; assert 'matplotlib.pyplot' not in sys.modules"
    subprocess.run([sys.executable, "-c", script], check=True)


def test_a_personal_figure_from_the_toolkit_checks_clean_and_saves(tmp_path: Path) -> None:
    mpp.use()
    pair = mpp.ColorPair(fill="#c7e9c0", edge="#4f9d58")
    x = np.linspace(0, 10, 50)
    fig, axes = mpp.grid_inches(1, 2, width=2.0, height=1.5)
    for ax in axes:
        mpp.plot_mean_sem(
            ax, x, np.sin(x), np.full_like(x, 0.1), fill=pair.fill, edge=pair.edge, label="Mean"
        )
        ax.axhline(0.0, **mpp.REFERENCE_LINE)
        # Autoscaled, the x axis ends at 12.5, whose label overhangs the 0.1 in right margin.
        ax.set_xlim(0.0, 10.0)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Signal")
        ax.legend()
    issues = mpp.check_figure(fig)
    assert {issue.rule for issue in issues} <= {"font-fallback"}
    paths = mpp.save_figure(fig, tmp_path / "demo", caption="A demo figure.")
    assert [path.name for path in paths] == [
        "demo.png", "demo.pdf", "demo.svg", "demo_caption.txt",
    ]  # fmt: skip


@pytest.mark.parametrize("document", DOCUMENTS)
def test_documented_examples_run(
    document: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    text = (files("mplplots") / "data" / "skills" / "mplplots" / document).read_text("utf-8")
    blocks = PYTHON_BLOCK.findall(text)
    assert blocks
    namespace = {"plt": plt, "np": np, "mpp": mpp}
    for block in blocks:
        exec(compile(block, document, "exec"), namespace)
