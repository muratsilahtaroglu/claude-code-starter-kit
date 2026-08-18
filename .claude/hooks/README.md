# .claude/hooks/ — the enforced layer

`rules.md` is guidance an agent can talk itself out of. These are shell scripts the harness runs at
tool-call boundaries: they observe, warn, or **block**. Registration lives in `.claude/settings.json`
(the only registry — the plugin-era `hooks.json` was retired with the plugin channel in v0.8.23; a
second registry double-fires every hook, see `docs/steering.md` "Distribution + double-fire trap").

**Contract.** The tool call arrives as JSON on stdin. `exit 2` blocks it; `exit 0` allows.
`SessionStart` stdout is injected into the session's context — the one hook event that can *speak*.

**Fail-open by design.** If `python3` is missing or stdin isn't JSON, a guard allows and complains to
stderr rather than blocking every call: a broken guard must not brick the session. The pre-commit
hooks and CI are the backstops. Each script states its own trade-off in its header — read it before
tightening one.

| Hook | Fires on | What it does |
|---|---|---|
| `block-dangerous.sh` | `PreToolUse` · Bash | **Blocks** recursive deletes of root/home/cwd (globs included), force pushes (`--force`, `-f`, `+refspec`), staging a real `.env`, and piping remote content into a shell. rules §5, §6 |
| `owner-guard.sh` | `PreToolUse` · Bash + Edit/Write/NotebookEdit | Armed only when `.claude/project-owner` exists. **Blocks** non-owner writes to governance files (PLAN · rules · CLAUDE · architecture · ADRs · `.claude/**`) and non-owner pushes to main/master. AI-side wall only — the host is the real one. rules §6, §10.40 |
| `session-start-reground.sh` | `SessionStart` | Speaks at every session start / compact / resume: re-read directive, memory-file cap warnings (`.claude/keel-caps`), rule-budget check, PLAN table↔diagram drift, ownership + due-date + review-queue + evidence-file checks, LESSONS `## Index` dead-target check, decorative-hook detection. rules §9 |
| `compact-gate.sh` | `PreCompact` · manual | **Blocks** a manual `/compact` when the tree changed but `HANDOVER.md` didn't — the memory-loss event the whole kit exists to prevent. Bypass: `/compact keel-force`. rules §1.4 |
| `pre-compact-snapshot.sh` | `PreCompact` | Writes a pre-compaction snapshot so state survives even an unclean compaction |
| `handover-reminder.sh` | `Stop` | Nudges when the session is ending with an out-of-date handover |
| `plan-phase-nudge.sh` | `Stop` | Nudges when a `wip` phase's `## Now` items are all checked but its PLAN gate was never flipped. rules §2.7 |
| `ritual-log.sh` | `PreToolUse`(Skill) · `UserPromptExpansion` · `SessionStart` · `PreCompact` | Telemetry: every skill call, user-typed command (built-ins included), session start and compact boundary → `.claude/ritual-log` (git-ignored, self-trimming). Rendered by `/keel-stats` |

## Changing a hook

These are the kit's only executable code, and they enforce §5/§6 at the boundary — so they carry the
kit's only regression suite: **`tests/unit/test_keel_hooks.py`** (142 cases). Run it before and after
any edit:

```bash
pytest tests/unit/test_keel_hooks.py -q     # or: make test
```

Three security bypasses shipped because every matrix that verified these hooks was run by hand in a
session and thrown away — the commit messages claimed "40-case matrix green" while
`git log --diff-filter=A -- tests/` was empty (`reports/2026-08-18-hook-audit.md`). Add a row to the
matrix in the same commit as the behaviour change; an ad-hoc probe proves a moment, a committed case
protects a regression.

**Testing by hand:** pipe a payload *file*, never a command line — writing `rm -rf /` or a dotenv
path into Bash trips this session's own guard (three real occurrences, see `CONTRIBUTING.md`).
