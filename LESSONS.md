# LESSONS.md — critical project knowledge, written the moment it appears (TEMPLATE)

> The project's **editable lessons database** (the "scratchpad" pattern: what the AI and the user agree
> on DURING work — rules discovered mid-project, must-run tests, gotchas, failed approaches). Different
> from `rules.md` (the general constitution written at project start): this file **accumulates during
> the project** and is `@`-imported every session, so agreements survive any number of compactions.
>
> **Write policy (hot path — rules.md §9.31):** the MOMENT the user corrects you, an approach fails, a
> must-run test or a mid-project rule is agreed — ask **"shall I note this?"** and on approval append it
> HERE immediately. Do NOT wait for session end or compaction: conversation-only agreements are exactly
> what compaction destroys. Unsure where a lesson belongs? Write it HERE — misfiled beats lost;
> `/keel-distill` re-files it.
>
> **Language: ENGLISH, on every project** (rules §9.31) — this file and `HANDOVER.md` are read by
> SESSIONS, not humans, and they are `@`-imported every time: EN costs fewer tokens per always-loaded
> line. The user's verbatim words may stay quoted in their own language; human surfaces (TASKS.md,
> PLAN.md, `reports/team/*`, docs) follow the PROJECT language, and anything needing the owner's
> decision is raised in CHAT in that language — the line here stays EN. Adopting mid-project: never
> bulk-translate; lines convert as `/keel-distill` rewrites them.
>
> **Keep this file to ALWAYS-relevant lessons (scope triage — rules §9.33).** Every line is paid in
> EVERY session, and an irrelevant line is not just token cost: context-rot measurements show even a
> single distractor degrades retrieval of the lines that DO apply (`research/web/findings.md`). Field
> audit of a mature project: only ~26% of accumulated lessons were always-relevant; ~52% bound
> specific files; any one task needed ~15% of the file (`reports/2026-08-17-lessons-scope-audit.md`).
> So, per entry (and `/keel-distill` for the stock):
> - **(A) Always-relevant** (verification duty, measurement epistemics, protocol) → stays HERE.
> - **(B) File/area-scoped** (matters only when touching X) → graduates to a `paths:`-scoped
>   `.claude/rules/<name>.md` — or a **`paths:`-scoped SKILL** when the cluster must survive a
>   mid-task compaction (invoked skill bodies re-inject; a path rule waits for the next file match).
> - **(C) Permanent domain/API facts** → `docs/` (architecture "known limitations" / a guide).
> - **(D) Superseded / closed / promoted** → DELETED (git is the archive). **Promotion deletes the
>   entry** — never leave a "moved to X" stub; the `## Index` line below is the only pointer.
>
> **Format:** atomic one-line entries, dated + tagged, newest first within a tag group. An entry that
> is contradicted but still instructive is marked `SUPERSEDED by <entry/date>` — visible, never
> silently removed. **Cap: ~250 lines** for this always-on core (team override: `.claude/keel-caps`,
> rules §10.40). On a large multi-area project the per-area split still applies — see the bottom.

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
**Default: this single file.** On a **large multi-area** project (backend + frontend + agent), when an
area's active lesson set needs its own room, give it `<area>/LESSONS.md` (same format + tiers + cap),
`@`-imported by that area's nested `<area>/CLAUDE.md` so it loads ONLY when working there — exactly
how per-area HANDOVER works (see `HANDOVER.md` → "Scaling"). Register the split in
`docs/architecture.md`. Split only when one file hurts — scope-triage (above) is the FIRST valve;
this is the second.
