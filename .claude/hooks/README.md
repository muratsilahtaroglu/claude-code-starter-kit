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
| `star-topology.sh` | `PreToolUse` · SendMessage | **Blocks** a worker messaging another WORKER on the agent-team roster — everything goes through the orchestrator, because the shared memory files have one writer (rules §10.42). Allows the orchestrator to anyone, anyone to the orchestrator, subagents, `main`, off-roster targets, and unadopted sessions. A permission rule cannot express this: `deny` takes the bare tool name and would cut the delivery path too |
| `session-start-reground.sh` | `SessionStart` | Speaks at every session start / compact / resume: re-read directive, memory-file cap warnings (`.claude/keel-caps`), rule-budget check, PLAN table↔diagram drift, ownership + due-date + review-queue + evidence-file checks, LESSONS `## Index` dead-target check, decorative-hook detection, **review-DECAY check** (names deliveries waiting `REVIEW_DAYS`+ in `## Review` with their age — the queue line counts, this one times), **workspace-trust check** (a project's `permissions.allow` rules are withheld until the trust dialog is accepted — the hook names them rather than letting the owner think the allow list works). rules §9 |
| `compact-gate.sh` | `PreCompact` · manual | **Blocks** a manual `/compact` when the tree changed but `HANDOVER.md` didn't — the memory-loss event the whole kit exists to prevent. Bypass: `/compact keel-force`. rules §1.4 |
| `pre-compact-snapshot.sh` | `PreCompact` | Writes a pre-compaction snapshot so state survives even an unclean compaction |
| `handover-reminder.sh` | `Stop` | Nudges when the session is ending with an out-of-date handover |
| `citation-gate.py` | `Stop`(--stop) | **Provenance:** do the artefacts our permanent records CITE exist in HEAD? `git commit -- <path>` skips an untracked file WITHOUT erroring, so a record can keep a reference the artefact never earned. Three classes, none silent: GHOST (on disk, not in HEAD) · UNRESOLVED (counted, never dropped) · BY DESIGN (.gitignore'd — a doc may name a file nobody commits). Resolves through `done/` so a `/keel-distill` sweep breaks nothing, normalises `..` before asking git, and self-tests its own pattern (exit 2 = tool broken, not "clean"). Fires only when the .md set changed — an always-red gate teaches people to walk past it. Allowlist: `.claude/citation-allow`. rules §6.18 · §3.10 · §10.40 |
| `plan-phase-nudge.sh` | `Stop` | Nudges when a `wip` phase's `## Now` items are all checked but its PLAN gate was never flipped. rules §2.7 |
| `entry-budget.py` | `PreToolUse`(Edit\|Write) · `SessionStart`(--check) | Per-ENTRY line budget for the always-imported boards — LESSONS.md (default 8, `LESSONS_ENTRY`) and TASKS.md (default 4, `TASKS_ENTRY`, measured: one project's `## Review` ran 12 items in 211 lines): blocks a write that makes any entry newly oversized or grows an oversized one — simulating the post-edit FILE, so folding material into an existing entry is caught too. --check keeps a monotone backlog baseline (auto-lowers, never auto-raises). Measured origin: raising the file cap "was never enough" — entries were growing, not multiplying. **Renamed from `lessons-entry-budget.py`** when TASKS joined it; a project updating from an older kit deletes the old file and its two registrations, or both fire on LESSONS |
| `ritual-log.sh` | `PreToolUse`(Skill) · `UserPromptSubmit` · `UserPromptExpansion` · `SessionStart` · `PreCompact` | Telemetry: every skill call, user-typed command (custom = `command …`; built-ins like `/compact` = `typed /…` via UserPromptSubmit — first token only, prose NEVER logged), session start and compact boundary → `.claude/ritual-log` (git-ignored, self-trimming), each line tagged with the writing session's `@agent`. Rendered by `/keel-stats` |

## Changing a hook

These are the kit's only executable code, and they enforce §5/§6 at the boundary — so they carry the
kit's only regression suite: **`tests/unit/test_keel_hooks.py`** (148), **`test_keel_telemetry.py`** (13) and
**`test_keel_star_topology.py`** (12). Run it before and after
any edit:

```bash
pytest tests/unit/test_keel_hooks.py -q     # or: make test
```

Three security bypasses shipped because every matrix that verified these hooks was run by hand in a
session and thrown away — the commit messages claimed "40-case matrix green" while
`git log --diff-filter=A -- tests/` was empty (`reports/2026-08-18-hook-audit.md`). Add a row to the
matrix in the same commit as the behaviour change; an ad-hoc probe proves a moment, a committed case
protects a regression.

**Two telemetry contracts** (both learned on 2026-08-19,
`reports/2026-08-19-observability-audit.md`):
- **A hook writes to `.claude/ritual-log` only when `CLAUDE_PROJECT_DIR` is set.** Claude Code exports
  it to every real invocation; a hand-piped probe does not. Without this guard, test runs land in the
  live log — which made the duplicate detector cry "uninstall your plugin" for two days on a machine
  with no plugin. The *guard* never depends on it: losing the log must not lose the wall.
- **Only event lines prove double-firing.** A repeated BLOCK line is normal — one guard legitimately
  stops two commands of the same class in a row. The detector counts `session-start|compact|skill|command`.

**Testing by hand:** pipe a payload *file*, never a command line — writing `rm -rf /` or a dotenv
path into Bash trips this session's own guard (three real occurrences, see `CONTRIBUTING.md`).
