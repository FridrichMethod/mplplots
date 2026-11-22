# For coding agents

mplplots ships an agent skill for Claude Code and Codex, a rules snippet for a project's
`AGENTS.md`, and the [style guide](../src/mplplots/data/skills/mplplots/references/style-guide.md):
the Personal style's rules for typography, lines and marks, color, layout, statistics, and export,
each with an id (T1, L4, C7, ...). The [skill](../src/mplplots/data/skills/mplplots/SKILL.md)
gives an agent a six-step workflow: apply the style, take colors from the project palette, lay out
in inches, draw and set the ticks with `auto_ticks`, `assert_figure`, `save_figure`.

## Installing the skill and the rules

```bash
mplplots install-skill --project .           # the skill, for Claude Code and Codex
mplplots install-skill --project . --rules   # also the rules, for Claude Code
mplplots install-skill --project . --check   # exit 1 if a copy is missing or out of date
mplplots rules >> AGENTS.md                  # the rules, for Codex
mplplots guide                               # print the style guide
```

`install-skill` writes `.claude/skills/mplplots/` (Claude Code) and `.agents/skills/mplplots/`
(Codex) in the project, each with `SKILL.md` and `references/style-guide.md`. `--client claude` or
`--client codex` limits it to one agent. `--rules` also writes `.claude/rules/mplplots.md`; Codex
reads no rules file, so for Codex it prints a hint to append `mplplots rules` to `AGENTS.md`
instead. Each `SKILL.md` copy names the mplplots version that wrote it, and running the command
again after an upgrade refreshes the copies. It prints one line per copy, `written` or
`unchanged`, and writes nothing outside the project.

## The `mplplots` command

Installing mplplots installs the `mplplots` command, with the subcommands `install-skill`,
`rules`, and `guide` above and `styles`, which lists the packaged styles and their files (see
[Styles](styles.md#packaged-styles)). `mplplots --version` prints the installed version, and
`python -m mplplots` runs the same command.
