# LESSONS.md — critical project knowledge, written the moment it appears (TEMPLATE)

> What the AI and the user agree on DURING the project (`rules.md` is the constitution written at its
> start). `@`-imported every session, so agreements survive any number of compactions. Full guide —
> tiers, promotion, scaling: **`docs/memory-files.md`**. Cap: `.claude/keel-caps`.
>
> - **Hot path:** the MOMENT the user corrects you, an approach fails, or a rule/test is agreed — ask
>   *"shall I note this?"* and append HERE on approval. Never "at compact time". Unsure where it
>   belongs? Here — misfiled beats lost.
> - **English** (rules §9.31). Exceptions: quoted owner wording, and a language-specific domain fact
>   whose example translation would destroy.
> - **Format:** atomic ONE-LINE entries, dated + tagged, newest first in each group. A lesson proven
>   WRONG is retired: the entry moves verbatim to `docs/lessons-retired.md` with its refutation and
>   ONE corrective line stays here — never silently deleted, never a stub paying rent every session.
> - **Keep only ALWAYS-relevant lessons.** File-scoped → a `paths:`-scoped rule (or SKILL, if it must
>   survive a mid-task compaction) · permanent domain fact → `docs/` · retired or promoted →
>   DELETED here. **Promotion deletes the entry**; its one pointer is the `## Index` line below.
>
> This header is DOCTRINE. Anything dated, measured, or awaiting a decision goes in the BODY.

## Index (task router — ONE line per graduated lesson cluster; keep ~10–20 lines)
<!-- The always-loaded map of lessons that live OUTSIDE this file, so they stay findable even when
     their trigger hasn't fired. Format: what → where (when it loads). Maintained by /keel-distill,
     linted mechanically (a dead target or an unlisted cluster is flagged at session start). E.g.:
- <topic, e.g. word-boundary contract> → .claude/rules/<name>.md (loads on <paths glob>)
- <procedure, e.g. release drill> → .claude/skills/<name>/SKILL.md (invoke / loads on <paths glob>)
- <domain quirks, e.g. provider API> → docs/<guide>.md (read before writing queries)
-->

## [rule] — mid-project agreements on how to work
- <YYYY-MM-DD> — <e.g. "never regenerate the lock file on Fridays before the release cut">

## [test] — must-run / periodic checks
- <YYYY-MM-DD> — <e.g. "after touching the parser, always run `pytest tests/integration/test_parser.py` + the e2e smoke">

## [fail] — tried, didn't work (distilled from HANDOVER blocks — permanent)
- <YYYY-MM-DD> — <approach> → FAILED: <reason>. (full trace: docs/handover-archive.md, block <date>)

## [gotcha] — surprising facts that cost time once
- <YYYY-MM-DD> — <e.g. "ENTITY_KEY is float64-lossy — always JOIN on ENTITY_KEY_STR">
---

## Scaling: per-area lessons (optional)
Default: this single file. Scope triage is the FIRST valve; an `<area>/LESSONS.md` behind a nested
`<area>/CLAUDE.md` is the second — see `docs/memory-files.md`. Register any split in
`docs/architecture.md`.
