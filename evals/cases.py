"""Set up and score the eval cases of the mplplots agent skill.

``evals.json`` lists the cases: a prompt, the input files and what a good result looks like.
``setup`` builds a throwaway project for one case, with its inputs and, unless ``--no-skill``
is given, the installed skill and rules; it prints the context and the request to hand to a
fresh agent. ``score`` runs the scripts the agent left in that project and reports what can be
checked mechanically; the assertions of ``evals.json`` that need judgment are read by hand.

Usage::

    python evals/cases.py setup timecourse /tmp/eval-timecourse
    python evals/cases.py score /tmp/eval-timecourse
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CASES = {case["id"]: case for case in json.loads((HERE / "evals.json").read_text())["evals"]}

# Runs a script with every saved figure checked once, before its first save.
WRAPPER = r"""
import json, os, runpy, sys
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from mplplots.check import check_figure

seen, report = set(), []
original = Figure.savefig

def savefig(self, *args, **kwargs):
    if id(self) not in seen:
        seen.add(id(self))
        issues = [[issue.rule, issue.severity, issue.message] for issue in check_figure(self)]
        report.append({"size": [float(value) for value in self.get_size_inches()], "issues": issues})
    return original(self, *args, **kwargs)

Figure.savefig = savefig
script = sys.argv[1]
sys.argv = [script]  # as `python script.py` does, with the script's folder first on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(script)))
try:
    runpy.run_path(script, run_name="__main__")
finally:
    print("EVAL-REPORT " + json.dumps(report))
"""

# Source patterns that the style guide rules out, each with the rule it breaks.
PATTERNS = {
    r"\b(fontsize|labelsize|fontweight|titlesize)\s*=": "a font size or weight argument (T1)",
    r"tight_layout|constrained|set_layout_engine|subplots_adjust": "a layout engine (S2)",
    r"bbox_inches": "a cropped save (X1)",
    r"\.savefig\(": "savefig in place of save_figure (X1)",
    r"sns\.set_(theme|style)|plt\.style\.use|rcParams": "a style applied over mpp.use() (T1)",
    r"colorbar\([^)]*\bax\s*=": "a color bar that takes space from its panel (L10)",
}


def write_kinetics(path: Path) -> None:
    """Write a long-format time course: three conditions, four replicates, eleven times."""
    rng = np.random.default_rng(11)
    rates = {"Wild type": 0.9, "Catalytic mutant": 0.25, "Mutant with activator": 0.6}
    rows = ["time_min,condition,replicate,signal"]
    for condition, rate in rates.items():
        for replicate in range(1, 5):
            for time in np.arange(0.0, 55.0, 5.0):
                signal = 1.0 - np.exp(-rate * time / 10.0) + rng.normal(0.0, 0.04)
                rows.append(f"{time:g},{condition},{replicate},{signal:.4f}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_embedding(path: Path) -> None:
    """Write 20,000 points of a two-dimensional embedding with a score."""
    rng = np.random.default_rng(12)
    centers = rng.uniform(-8.0, 8.0, (6, 2))
    points = centers[rng.integers(0, 6, 20_000)] + rng.normal(0.0, 1.2, (20_000, 2))
    score = np.hypot(*points.T) / 12.0 + rng.normal(0.0, 0.05, 20_000)
    table = np.column_stack([points, score])
    np.savetxt(path, table, delimiter=",", header="x,y,score", comments="", fmt="%.4f")


def write_correlation(path: Path) -> None:
    """Write a 12 by 12 sample correlation matrix with long sample names."""
    rng = np.random.default_rng(13)
    names = [
        f"{tissue}_{state}_rep{replicate}"
        for tissue in ("cortex", "striatum")
        for state in ("control", "treated", "washout")
        for replicate in (1, 2)
    ]
    profiles = rng.normal(0.0, 1.0, (12, 200)) + np.repeat(
        rng.normal(0.0, 1.5, (6, 200)), 2, axis=0
    )
    matrix: list[list[float]] = np.atleast_2d(np.corrcoef(profiles)).tolist()
    rows = ["sample," + ",".join(names)]
    rows += [
        name + "," + ",".join(f"{value:.4f}" for value in row) for name, row in zip(names, matrix)
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


WRITERS = {
    "data/kinetics.csv": write_kinetics,
    "data/embedding.csv": write_embedding,
    "data/correlation.csv": write_correlation,
}


def setup(case_id: str, project: Path, *, skill: bool) -> str:
    """Build the project of a case and return the message to hand to a fresh agent.

    Args:
        case_id: An id of ``evals.json``.
        project: The directory to create; it must not exist.
        skill: Install the skill and rules into the project and describe them in the message,
            as an agent harness does. Without them the message is the baseline.

    Returns:
        The context and the request, as one message.
    """
    case = CASES[case_id]
    project.mkdir(parents=True)
    for name in case["files"]:
        target = project / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name in WRITERS:
            WRITERS[name](target)
        else:
            shutil.copy(HERE / "files" / name, target)
    context = [
        f"You are a coding agent working in the project at {project}, a small computational"
        " biology analysis repository. Work only inside that directory.",
        f"Run Python as {sys.executable}; numpy, pandas, matplotlib, seaborn, plotly and"
        " mplplots are installed, and you must not install anything.",
    ]
    if skill:
        command = [sys.executable, "-m", "mplplots", "install-skill", "--project", str(project)]
        subprocess.run([*command, "--rules"], check=True, capture_output=True)
        rules = (project / ".claude" / "rules" / "mplplots.md").read_text(encoding="utf-8")
        front = (project / ".claude" / "skills" / "mplplots" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        (description,) = re.findall(r"^description: (.*)$", front, flags=re.MULTILINE)
        context += [
            "The project's instructions, which your harness loaded for you:\n\n" + rules.strip(),
            "Skills available in this project (.claude/skills/<name>/SKILL.md):\n\n"
            f"- mplplots: {description}",
        ]
    context += [
        "The user's request:\n\n" + case["prompt"],
        "When you are done, reply with the files you created or changed and what the user"
        " should know.",
    ]
    return "\n\n".join(context)


def score(project: Path) -> int:
    """Run the scripts of a project and print what can be checked mechanically.

    Returns:
        The number of scripts that failed to run plus the number of ``check_figure`` errors.
    """
    scripts = [
        path
        for path in sorted(project.rglob("*.py"))
        if not {".claude", ".agents", ".venv"} & set(path.relative_to(project).parts)
    ]
    failures = 0
    for script in scripts:
        source = script.read_text(encoding="utf-8")
        print(f"== {script.relative_to(project)}")
        uses = {
            name: name in source
            for name in ("mpp.use(", "assert_figure", "save_figure", "check_palette", "rasterized")
        }
        print("   uses:", ", ".join(f"{name}={found}" for name, found in uses.items()))
        for pattern, meaning in PATTERNS.items():
            for match in re.finditer(pattern, source):
                line = source.count("\n", 0, match.start()) + 1
                print(f"   line {line}: {meaning}")
        for match in re.finditer(
            r"^(.*)\b(ignore|allow_font_\w+)\s*=.*$", source, flags=re.MULTILINE
        ):
            line = source.count("\n", 0, match.start()) + 1
            before = source.splitlines()[max(line - 2, 0)]
            if "#" not in match.group(0) and not before.lstrip().startswith("#"):
                print(f"   line {line}: {match.group(2)} without a stated reason")
        result = subprocess.run(
            [sys.executable, "-c", WRAPPER, str(script)],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        reports = [line for line in result.stdout.splitlines() if line.startswith("EVAL-REPORT ")]
        if result.returncode != 0:
            failures += 1
            print(f"   exit {result.returncode}: {result.stderr.strip().splitlines()[-1:]}")
        for figure in json.loads(reports[-1].removeprefix("EVAL-REPORT ")) if reports else []:
            width, height = figure["size"]
            print(f"   figure {width:g} x {height:g} in: {len(figure['issues'])} issue(s)")
            for rule, severity, message in figure["issues"]:
                failures += severity == "error"
                print(f"      {severity} {rule}: {message}")
    outputs = sorted(
        str(path.relative_to(project))
        for path in project.rglob("*")
        if path.suffix in {".png", ".pdf", ".svg", ".html"} or path.name.endswith("_caption.txt")
    )
    print("== outputs:", ", ".join(outputs) or "none")
    return failures


def main() -> int:
    """Run the ``setup`` or ``score`` command."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("setup", help="build the project of a case and print its message")
    build.add_argument("case", choices=sorted(CASES))
    build.add_argument("project", type=Path)
    build.add_argument("--no-skill", action="store_true", help="the baseline: no skill, no rules")
    check = commands.add_parser("score", help="run and check the scripts of a project")
    check.add_argument("project", type=Path)
    args = parser.parse_args()
    if args.command == "setup":
        print(setup(args.case, args.project.resolve(), skill=not args.no_skill))
        return 0
    return 1 if score(args.project.resolve()) else 0


if __name__ == "__main__":
    sys.exit(main())
