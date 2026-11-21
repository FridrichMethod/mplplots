"""The ``mplplots`` command: the packaged styles, the style guide and the agent skill.

- ``mplplots styles`` lists the packaged styles, marks the default and gives each file's path.
- ``mplplots rules`` prints the rules snippet for a project's ``AGENTS.md``, verbatim.
- ``mplplots guide`` prints the style guide, verbatim.
- ``mplplots install-skill --project DIR`` copies the skill and its style guide into a project:
  to ``DIR/.claude/skills/mplplots/`` for Claude Code and ``DIR/.agents/skills/mplplots/`` for
  Codex, with a marker line after the skill's front matter that names the mplplots version.
  ``--rules`` also copies the rules snippet to ``DIR/.claude/rules/mplplots.md``. Codex reads no
  rules file, so for Codex it prints a hint instead.

Copies are idempotent. ``--check`` writes nothing and exits 1 when a copy is missing or differs
from what would be written. Nothing is written when ``DIR`` is not a directory or is the home
directory itself, whose copies would load in every project, or when the way to a target runs
into a loop of links or resolves, through a link, to a path outside ``DIR``. A write that fails
stops the command after the lines for the copies already handled.
"""

import argparse
import errno
import os
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from importlib.resources import files
from pathlib import Path

from mplplots import __version__
from mplplots.styles import DEFAULT_STYLE, STYLES, style_path

__all__ = ["main"]

_EXIT_OK = 0
_EXIT_FAILURE = 1

_CLIENTS = ("claude", "codex")
_SKILL_DIRS = {"claude": ".claude/skills/mplplots", "codex": ".agents/skills/mplplots"}
_SKILL = ("skills", "mplplots", "SKILL.md")
_GUIDE = ("skills", "mplplots", "references", "style-guide.md")
_RULES = ("rules", "figures.md")
_RULES_COPY = ".claude/rules/mplplots.md"
_MARKER = (
    f"<!-- installed by mplplots {__version__} via mplplots install-skill; "
    "edits are overwritten -->\n"
)
_FRONT_MATTER_END = "\n---\n"
_CODEX_RULES_HINT = (
    "hint: Codex reads no rules file; append the output of `mplplots rules` to the project's "
    "AGENTS.md"
)

type _Handler = Callable[[argparse.Namespace], int]


def _packaged(parts: Sequence[str]) -> str:
    """Return the text of a data file shipped in ``mplplots/data``.

    Args:
        parts: The file's path below ``mplplots/data``, one component per item.

    Returns:
        The file's text.
    """
    return files("mplplots").joinpath("data", *parts).read_text(encoding="utf-8")


def _marked_skill() -> str:
    """Return the packaged ``SKILL.md`` with the marker line right after its front matter.

    Returns:
        The text that ``install-skill`` writes to each ``SKILL.md`` copy.
    """
    text = _packaged(_SKILL)
    end = text.index(_FRONT_MATTER_END, len("---")) + len(_FRONT_MATTER_END)
    return text[:end] + _MARKER + text[end:]


def _wanted_files(clients: Iterable[str], *, rules: bool) -> dict[str, str]:
    """Return the copies that ``install-skill`` makes, as project-relative path to text.

    Args:
        clients: The agent clients to install for, from ``claude`` and ``codex``.
        rules: Whether Claude Code also gets the rules snippet.

    Returns:
        The text of each copy, keyed by its path relative to the project, in POSIX form.
    """
    skill, guide = _marked_skill(), _packaged(_GUIDE)
    wanted: dict[str, str] = {}
    for client in clients:
        wanted[f"{_SKILL_DIRS[client]}/SKILL.md"] = skill
        wanted[f"{_SKILL_DIRS[client]}/references/style-guide.md"] = guide
        if rules and client == "claude":
            wanted[_RULES_COPY] = _packaged(_RULES)
    return wanted


def _home() -> Path | None:
    """Return the resolved home directory.

    Returns:
        The home directory, or ``None`` when neither ``HOME`` nor the user database gives one.
    """
    try:
        return Path.home().resolve()
    except RuntimeError:
        return None


def _in_link_loop(path: Path) -> bool:
    """Return whether the way to ``path`` runs into a loop of symbolic links.

    Args:
        path: The path to look up.

    Returns:
        Whether looking the path up fails with ``ELOOP``.
    """
    try:
        path.stat()
    except OSError as error:
        return error.errno == errno.ELOOP
    return False


def _refused_targets(project: Path, paths: Iterable[str]) -> list[str]:
    """Return why each target that ``install-skill`` must not touch is refused.

    A link that stays inside the project is followed. A target is refused when the way to it
    runs into a loop of links or cannot be resolved, or when it resolves to a path outside the
    project.

    Args:
        project: The resolved project directory.
        paths: The targets, relative to the project.

    Returns:
        One ``"target: reason"`` entry per refused target.
    """
    refused = []
    for relative in paths:
        target = project / relative
        if _in_link_loop(target):
            refused.append(f"{relative}: a loop of symbolic links")
            continue
        try:
            resolved = target.resolve()
        except (OSError, RuntimeError) as error:
            refused.append(f"{relative}: cannot be resolved ({error})")
            continue
        if not resolved.is_relative_to(project):
            refused.append(f"{relative} -> {resolved}: a link leads out of {project}")
    return refused


def _copy_state(path: Path, text: str) -> str:
    """Compare a copy on disk with the text that would be written.

    Args:
        path: The copy's path.
        text: The text that ``install-skill`` writes there.

    Returns:
        ``missing`` if there is no copy, ``unchanged`` if it holds exactly ``text`` and
        ``stale`` otherwise.
    """
    if not path.exists():
        return "missing"
    try:
        current = path.read_text(encoding="utf-8") if path.is_file() else None
    except (OSError, UnicodeDecodeError):
        current = None
    return "unchanged" if current == text else "stale"


def _fail(message: str) -> int:
    """Report a failure on standard error.

    Args:
        message: What failed.

    Returns:
        The failure exit code.
    """
    print(f"mplplots: {message}", file=sys.stderr)
    return _EXIT_FAILURE


def _print_states(states: Mapping[str, str]) -> None:
    """Print one line per target: its state, then its project-relative path.

    Args:
        states: The state of each target, keyed by its project-relative path.
    """
    for relative, state in states.items():
        print(f"{state:<9}  {relative}")


def _styles(_args: argparse.Namespace) -> int:
    """List the packaged styles: name, ``(default)`` for the default, and the file path.

    Returns:
        The success exit code.
    """
    labels = {name: f"{name} (default)" if name == DEFAULT_STYLE else name for name in STYLES}
    width = max(len(label) for label in labels.values())
    for name in STYLES:
        print(f"{labels[name]:<{width}}  {style_path(name)}")
    return _EXIT_OK


def _rules(_args: argparse.Namespace) -> int:
    """Print the packaged rules snippet verbatim.

    Returns:
        The success exit code.
    """
    print(_packaged(_RULES), end="")
    return _EXIT_OK


def _guide(_args: argparse.Namespace) -> int:
    """Print the packaged style guide verbatim.

    Returns:
        The success exit code.
    """
    print(_packaged(_GUIDE), end="")
    return _EXIT_OK


def _install_skill(args: argparse.Namespace) -> int:
    """Write, or with ``--check`` only compare, the project's copies of the skill.

    Prints one line per target: its state, then its project-relative path. When a write fails,
    it prints the lines of the targets before it, then the error, and leaves the rest alone.

    Args:
        args: The parsed ``install-skill`` arguments.

    Returns:
        0 on success; 1 when ``DIR`` is not a directory or is the home directory itself, a target
        leads out of it or cannot be resolved, a write fails, or ``--check`` finds a missing or
        stale copy.
    """
    try:
        project = args.project.expanduser().resolve()
    except (OSError, RuntimeError) as error:
        return _fail(f"--project {args.project}: {error}; nothing written")
    if not project.is_dir():
        return _fail(f"--project {args.project}: not a directory; nothing written")
    if project == _home():
        return _fail(
            f"--project {args.project}: HOME itself, where copies load in every project; "
            "nothing written"
        )
    clients = _CLIENTS if args.client == "all" else (args.client,)
    wanted = _wanted_files(clients, rules=args.rules)
    refused = _refused_targets(project, wanted)
    if refused:
        return _fail(f"{'; '.join(refused)}; nothing written")
    states = {relative: _copy_state(project / relative, text) for relative, text in wanted.items()}
    if not args.check:
        done: dict[str, str] = {}
        for relative, text in wanted.items():
            if states[relative] != "unchanged":
                target = project / relative
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text, encoding="utf-8")
                except OSError as error:
                    _print_states(done)
                    return _fail(f"{relative}: {error}; the targets after it are not written")
                states[relative] = "written"
            done[relative] = states[relative]
    _print_states(states)
    if args.rules and "codex" in clients:
        print(_CODEX_RULES_HINT)
    failed = args.check and any(state != "unchanged" for state in states.values())
    return _EXIT_FAILURE if failed else _EXIT_OK


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser of the ``mplplots`` command.

    Returns:
        The parser, with one subcommand per command and each subcommand's handler as
        ``handler``.
    """
    parser = argparse.ArgumentParser(
        prog="mplplots", description="Matplotlib styles, the style guide and the agent skill."
    )
    parser.add_argument("--version", action="version", version=f"mplplots {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    commands.add_parser("styles", help="list the packaged styles and their files").set_defaults(
        handler=_styles
    )
    commands.add_parser("rules", help="print the rules snippet for AGENTS.md").set_defaults(
        handler=_rules
    )
    commands.add_parser("guide", help="print the style guide").set_defaults(handler=_guide)

    install = commands.add_parser(
        "install-skill", help="copy the mplplots skill (and the rules) into a project"
    )
    install.add_argument(
        "--project", required=True, type=Path, metavar="DIR", help="the project's root directory"
    )
    install.add_argument(
        "--client",
        choices=(*_CLIENTS, "all"),
        default="all",
        help="the agent to install for: Claude Code, Codex or both (default: all)",
    )
    install.add_argument(
        "--rules", action="store_true", help=f"also copy the rules to DIR/{_RULES_COPY}"
    )
    install.add_argument(
        "--check", action="store_true", help="write nothing; exit 1 if a copy is missing or stale"
    )
    install.set_defaults(handler=_install_skill)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``mplplots`` command.

    Args:
        argv: The arguments after the program name; ``None`` reads them from ``sys.argv``.

    Returns:
        The exit code: 0 on success, 1 on a failure, a failed ``--check`` or a reader of standard
        output that has gone. A usage error raises ``SystemExit`` with code 2, and ``--help``
        and ``--version`` raise it with 0.
    """
    # With file descriptor 1 closed, ``sys.stdout`` is None and ``print`` writes nothing, so a
    # command run without standard output does its work and exits as it would otherwise.
    try:
        try:
            args = _parser().parse_args(argv)
            handler: _Handler = args.handler
            return handler(args)
        finally:
            # Flush here, so that a closed pipe fails inside the try, not at interpreter exit.
            if sys.stdout is not None:
                sys.stdout.flush()
    except BrokenPipeError:
        # A reader such as ``head`` may close the pipe before the output is written. Standard
        # output is pointed at the null device so that Python's final flush does not fail too.
        if sys.stdout is not None:
            os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return _EXIT_FAILURE
