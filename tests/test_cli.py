import os
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

import mplplots
from mplplots.cli import main

DATA = files("mplplots") / "data"
SKILL = (DATA / "skills" / "mplplots" / "SKILL.md").read_text(encoding="utf-8")
GUIDE = (DATA / "skills" / "mplplots" / "references" / "style-guide.md").read_text(encoding="utf-8")
RULES = (DATA / "rules" / "figures.md").read_text(encoding="utf-8")
MARKER = (
    f"<!-- installed by mplplots {mplplots.__version__} via mplplots install-skill; "
    "edits are overwritten -->"
)
CLAUDE = Path(".claude/skills/mplplots")
CODEX = Path(".agents/skills/mplplots")


def install(project: Path, *extra: str) -> int:
    return main(["install-skill", "--project", str(project), *extra])


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"mplplots {mplplots.__version__}\n"


def test_no_command_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as exit_info:
        main([])
    assert exit_info.value.code == 2


def test_styles(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["styles"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == len(mplplots.STYLES)
    assert any(line.startswith("Personal (default)") for line in lines)
    assert all(line.endswith(".mplstyle") for line in lines)


def test_rules_and_guide_print_the_packaged_files(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["rules"]) == 0
    assert capsys.readouterr().out == RULES
    assert main(["guide"]) == 0
    assert capsys.readouterr().out == GUIDE


def test_install_writes_both_clients_and_no_rules(tmp_path: Path) -> None:
    assert install(tmp_path) == 0
    for root in (CLAUDE, CODEX):
        lines = (tmp_path / root / "SKILL.md").read_text(encoding="utf-8").splitlines()
        assert lines[0] == "---"
        assert lines[lines.index("---", 1) + 1] == MARKER
        assert (tmp_path / root / "references" / "style-guide.md").read_text(
            encoding="utf-8"
        ) == GUIDE
    assert not (tmp_path / ".claude" / "rules").exists()


def test_install_one_client_with_rules(tmp_path: Path) -> None:
    assert install(tmp_path, "--client", "claude", "--rules") == 0
    assert (tmp_path / ".claude" / "rules" / "mplplots.md").read_text(encoding="utf-8") == RULES
    assert not (tmp_path / ".agents").exists()


def test_codex_gets_a_hint_instead_of_a_rules_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert install(tmp_path, "--client", "codex", "--rules") == 0
    out = capsys.readouterr().out
    assert "mplplots rules" in out
    assert "AGENTS.md" in out
    assert not (tmp_path / ".claude").exists()


def test_install_is_idempotent(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # One line per target: the state, then the project-relative path.
    assert install(tmp_path) == 0
    assert {line.split()[0] for line in capsys.readouterr().out.splitlines()} == {"written"}
    assert install(tmp_path) == 0
    assert {line.split()[0] for line in capsys.readouterr().out.splitlines()} == {"unchanged"}
    assert install(tmp_path, "--check") == 0
    assert {line.split()[0] for line in capsys.readouterr().out.splitlines()} == {"unchanged"}


def test_check_reports_missing_and_stale_copies_without_writing(tmp_path: Path) -> None:
    assert install(tmp_path, "--check") == 1
    assert list(tmp_path.iterdir()) == []
    assert install(tmp_path) == 0
    assert install(tmp_path, "--check") == 0
    skill = tmp_path / CLAUDE / "SKILL.md"
    skill.write_text("edited\n", encoding="utf-8")
    assert install(tmp_path, "--check") == 1
    assert skill.read_text(encoding="utf-8") == "edited\n"
    assert install(tmp_path) == 0
    assert MARKER in skill.read_text(encoding="utf-8")


def test_a_missing_project_fails(tmp_path: Path) -> None:
    assert install(tmp_path / "missing") == 1
    assert not (tmp_path / "missing").exists()


def test_a_link_out_of_the_project_is_refused(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    project = tmp_path / "project"
    outside.mkdir()
    project.mkdir()
    (project / ".claude").symlink_to(outside, target_is_directory=True)
    assert install(project) == 1
    assert list(outside.iterdir()) == []
    assert not (project / ".agents").exists()


def test_module_entry_point() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mplplots", "styles"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "Personal (default)" in result.stdout


def test_skill_front_matter_and_workflow() -> None:
    lines = SKILL.splitlines()
    front = lines[1 : lines.index("---", 1)]
    assert "name: mplplots" in front
    (description,) = [line for line in front if line.startswith("description: ")]
    assert len(description) <= 1024
    for name in (
        "mpp.use()",
        "ColorPair",
        "check_palette",
        "grid_inches",
        "assert_figure",
        "save_figure",
        "references/style-guide.md",
    ):
        assert name in SKILL, name
    assert len(lines) <= 150


def test_rules_snippet_is_short() -> None:
    assert len(RULES.splitlines()) <= 15
    assert "mplplots" in RULES


# Beyond the plan's tests.


def test_copies_are_the_packaged_files_plus_the_marker(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert install(tmp_path, "--rules") == 0
    lines = capsys.readouterr().out.splitlines()
    hints = [line for line in lines if line.startswith("hint:")]
    assert len(hints) == 1
    assert "AGENTS.md" in hints[0]
    reported = {line.split()[1] for line in lines if line not in hints}
    assert reported == {
        (CLAUDE / "SKILL.md").as_posix(),
        (CLAUDE / "references" / "style-guide.md").as_posix(),
        ".claude/rules/mplplots.md",
        (CODEX / "SKILL.md").as_posix(),
        (CODEX / "references" / "style-guide.md").as_posix(),
    }
    for root in (CLAUDE, CODEX):
        copy = (tmp_path / root / "SKILL.md").read_text(encoding="utf-8")
        assert copy.replace(MARKER + "\n", "", 1) == SKILL


def test_check_after_an_upgrade_reports_a_stale_marker(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert install(tmp_path) == 0
    skill = tmp_path / CODEX / "SKILL.md"
    old = skill.read_text(encoding="utf-8").replace(mplplots.__version__, "0.0.1")
    skill.write_text(old, encoding="utf-8")
    capsys.readouterr()
    assert install(tmp_path, "--check") == 1
    lines = capsys.readouterr().out.splitlines()
    states = {path: state for state, path in (line.split() for line in lines)}
    assert states[(CODEX / "SKILL.md").as_posix()] == "stale"
    assert states[(CLAUDE / "SKILL.md").as_posix()] == "unchanged"
    assert skill.read_text(encoding="utf-8") == old


def test_check_reports_missing_copies_by_name(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert install(tmp_path, "--client", "claude", "--check") == 1
    out = capsys.readouterr().out
    assert {line.split()[0] for line in out.splitlines()} == {"missing"}


def test_a_link_out_of_the_project_is_refused_under_check(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    project = tmp_path / "project"
    outside.mkdir()
    project.mkdir()
    (project / ".agents").symlink_to(outside, target_is_directory=True)
    assert install(project, "--check") == 1
    assert list(outside.iterdir()) == []


def test_links_inside_the_project_are_followed(tmp_path: Path) -> None:
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / ".agents").mkdir()
    (tmp_path / ".agents" / "skills").symlink_to("../.claude/skills", target_is_directory=True)
    assert install(tmp_path) == 0
    assert MARKER in (tmp_path / CLAUDE / "SKILL.md").read_text(encoding="utf-8")
    assert install(tmp_path, "--check") == 0


def test_a_file_as_project_fails(tmp_path: Path) -> None:
    project = tmp_path / "file.txt"
    project.write_text("not a directory\n", encoding="utf-8")
    assert install(project) == 1
    assert project.read_text(encoding="utf-8") == "not a directory\n"


def test_unknown_client_is_a_usage_error(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exit_info:
        install(tmp_path, "--client", "vim")
    assert exit_info.value.code == 2
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "command",
    [
        ["guide"],
        ["rules"],
        ["styles"],
        ["install-skill", "--project", "{project}", "--rules"],
        ["install-skill", "--project", "{project}", "--check"],
        ["--version"],
        ["--help"],
    ],
)
def test_a_reader_that_stops_early_gets_no_traceback(tmp_path: Path, command: list[str]) -> None:
    # The pipe has no reader before the command writes, as `mplplots guide | head -1` can leave
    # it, so the first write always fails, whatever the pipe's capacity. Every command, even one
    # that would succeed (the --check runs on an installed project), exits 1 without a traceback.
    assert install(tmp_path, "--rules") == 0
    args = [arg.format(project=tmp_path) for arg in command]
    read_end, write_end = os.pipe()
    os.close(read_end)
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "mplplots", *args], stdout=write_end, stderr=subprocess.PIPE
        )
    finally:
        os.close(write_end)
    _, stderr = process.communicate()
    assert process.returncode == 1
    assert stderr == b""


def run_without_stdout(*args: str) -> subprocess.CompletedProcess[bytes]:
    # File descriptor 1 is closed in the child, as `mplplots styles >&-` leaves it, so Python
    # starts with sys.stdout set to None.
    return subprocess.run(
        [sys.executable, "-m", "mplplots", *args],
        stderr=subprocess.PIPE,
        preexec_fn=lambda: os.close(1),
        check=False,
    )


@pytest.mark.parametrize(
    "command",
    [
        ["guide"],
        ["rules"],
        ["styles"],
        ["install-skill", "--project", "{project}", "--rules"],
        ["install-skill", "--project", "{project}", "--check"],
    ],
)
def test_without_stdout_a_command_does_its_work_and_succeeds(
    tmp_path: Path, command: list[str]
) -> None:
    # print() writes nothing when sys.stdout is None; the command still runs and exits 0. The
    # --check runs on an installed project, the plain install on an empty one.
    if "--check" in command:
        assert install(tmp_path, "--rules") == 0
    result = run_without_stdout(*(arg.format(project=tmp_path) for arg in command))
    assert result.returncode == 0
    assert result.stderr == b""
    if "install-skill" in command:
        assert MARKER in (tmp_path / CLAUDE / "SKILL.md").read_text(encoding="utf-8")
        assert (tmp_path / ".claude" / "rules" / "mplplots.md").read_text(encoding="utf-8") == RULES


@pytest.mark.parametrize("flag", ["--version", "--help"])
def test_without_stdout_version_and_help_exit_0(flag: str) -> None:
    # argparse writes them to standard error when there is no standard output.
    result = run_without_stdout(flag)
    assert result.returncode == 0
    assert b"Traceback" not in result.stderr


def test_home_as_project_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Copies in HOME would load in every project: ~/.claude/skills, ~/.claude/rules.
    monkeypatch.setenv("HOME", str(tmp_path))
    assert install(Path("~"), "--rules") == 1
    assert install(tmp_path, "--check") == 1
    assert list(tmp_path.iterdir()) == []
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.count("mplplots: --project") == 2
    assert "HOME" in captured.err


def test_a_project_inside_home_is_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "project").mkdir()
    assert install(Path("~/project")) == 0
    assert MARKER in (tmp_path / "project" / CLAUDE / "SKILL.md").read_text(encoding="utf-8")


def test_a_link_loop_under_a_target_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".agents").symlink_to("loop", target_is_directory=True)
    (tmp_path / "loop").symlink_to(".agents", target_is_directory=True)
    for extra in ((), ("--check",)):
        assert install(tmp_path, *extra) == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err.startswith("mplplots: ")
        assert (CODEX / "SKILL.md").as_posix() in captured.err
        assert "nothing written" in captured.err
    assert sorted(path.name for path in tmp_path.iterdir()) == [".agents", "loop"]


def test_a_link_loop_as_project_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "project").symlink_to("project", target_is_directory=True)
    assert install(tmp_path / "project") == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("mplplots: --project ")


def test_a_failed_write_reports_the_copies_already_made(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # A directory where the Codex SKILL.md goes: the Claude copies come first and are written.
    (tmp_path / CODEX / "SKILL.md").mkdir(parents=True)
    assert install(tmp_path) == 1
    captured = capsys.readouterr()
    assert captured.out.splitlines() == [
        f"written    {(CLAUDE / 'SKILL.md').as_posix()}",
        f"written    {(CLAUDE / 'references' / 'style-guide.md').as_posix()}",
    ]
    assert captured.err.startswith(f"mplplots: {(CODEX / 'SKILL.md').as_posix()}: ")
    assert not (tmp_path / CODEX / "references").exists()
    # A rerun reports the Claude copies as unchanged before the same failure.
    assert install(tmp_path) == 1
    assert {line.split()[0] for line in capsys.readouterr().out.splitlines()} == {"unchanged"}
