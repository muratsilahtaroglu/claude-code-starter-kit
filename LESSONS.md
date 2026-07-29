# LESSONS.md — critical project knowledge, written the moment it appears (TEMPLATE)

> The project's **editable lessons database** (the "scratchpad" pattern: what the AI and the user agree
> on DURING work — rules discovered mid-project, must-run tests, gotchas, failed approaches). Different
> from `rules.md` (the general constitution written at project start): this file **accumulates during
> the project** and is `@`-imported every session, so agreements survive any number of compactions.
>
> **Write policy (hot path — rules.md §9.31):** the MOMENT the user corrects you, an approach fails, a
> must-run test or a mid-project rule is agreed — ask **"shall I note this?"** and on approval append it
> HERE immediately. Do NOT wait for session end or compaction: conversation-only agreements are exactly
> what compaction destroys.
>
> **Format:** atomic one-line entries, dated + tagged, newest first within a tag group. Never silently
> delete: mark superseded entries as `SUPERSEDED by <entry/date>` (or remove them during `/keel-distill` once
> promoted to rules.md/a skill). **Cap: ~250 lines** (team override: `.claude/keel-caps`, rules §10.40)
> — `/keel-distill` dedups, merges, and promotes.
>
> **Long projects — two pressure valves before you ever raise the cap** (the file is `@`-imported every
> session, so every line is a permanent token + attention tax): (1) **graduate** — a 3×-applied entry
> leaves for `rules.md`/a skill/an ADR, and a permanent DOMAIN fact (data quirk, API contract) moves to
> `docs/` (architecture "known limitations" / a guide), not here; (2) **per-area split** on big
> multi-area projects — see the section at the bottom.

## [rule] — mid-project agreements on how to work
- <YYYY-MM-DD> — <e.g. "never regenerate the lock file on Fridays before the release cut">

## [test] — must-run / periodic checks
- <YYYY-MM-DD> — <e.g. "after touching the parser, always run `pytest tests/integration/test_parser.py` + the e2e smoke">

## [fail] — tried, didn't work (distilled from HANDOVER blocks — permanent)
- <YYYY-MM-DD> — <approach> → FAILED: <reason>. (full trace: docs/handover-archive.md, block <date>)

## [gotcha] — surprising facts that cost time once
- <YYYY-MM-DD> — <e.g. "ENTITY_KEY is float64-lossy — always JOIN on ENTITY_KEY_STR">
<!-- A [gotcha] that is a PERMANENT domain fact (not situational) graduates to docs/ at /keel-distill —
     see the graduation note at the top — so this section stays the HOT set, not a growing archive. -->

---

## Scaling: per-area lessons (optional)
**Default: this single file.** On a **large multi-area** project (backend + frontend + agent), when an
area's active lesson set needs its own room, give it `<area>/LESSONS.md` (same `[rule]/[test]/[fail]/
[gotcha]` format + the ~150 cap), `@`-imported by that area's nested `<area>/CLAUDE.md` so it loads
ONLY when working there — exactly how per-area HANDOVER works (see `HANDOVER.md` → "Scaling"). Register
the split in `docs/architecture.md`. This is how a long project holds MANY lessons without paying for
all of them every session — the alternative to just enlarging the always-loaded file. Split only when
one file hurts.
