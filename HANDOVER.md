# HANDOVER.md — session handover, block-rotated (TEMPLATE)

> Written BEFORE every compact/session end (`/keel-handover`). The repo is durable disk; the context
> window is volatile RAM — what is not written here is assumed lost. `@`-imported every session. Full
> guide — rotation, archiving, per-area scaling: **`docs/memory-files.md`**. Cap: `.claude/keel-caps`.
>
> - One dated block per session, newest first: **(a)** completed · **(b)** tried and FAILED, with the
>   reason · **(c)** latest updates · **(d)** next steps. (b) is the highest-value part.
> - **English** (rules §9.31); quoted owner wording may stay as-is.
> - On overflow run `/keel-distill`: critical facts → `LESSONS.md`, raw block verbatim →
>   `docs/handover-archive.md` (never imported, grep-able forever).
> - Strip session narration as you write (commit counts, sha ranges, "ran /keel-distill") — keep
>   decisions and their WHY.
>
> This header is DOCTRINE. Anything dated, measured, or awaiting a decision goes in the BODY.

_Last updated: <YYYY-MM-DD> — <short status>._

---

## Session blocks (newest first — a fresh session reads the TOP block first)
<!-- Insert each new session block HERE, directly below this comment (newest first; older blocks get
     pushed down). ONE BLOCK PER SESSION, not per day: the heading carries HH:MM, so several same-day
     sessions stay separate; a /keel-handover re-run in the SAME session updates its own block (keeping
     its original time). Max 3 blocks — then run /keel-distill. On the FIRST real session, REPLACE the
     placeholder block below (don't stack a real block on top of it, or the phantom placeholder lingers
     forever). -->

### <YYYY-MM-DD HH:MM> — <one-line status>   <!-- ← REPLACE this whole placeholder block on the first session -->
- **(a) Completed:** <what was done, briefly>. (Details/decisions → ADR / docs; done TASKS.md items land here as one-liners.)
- **(b) Tried, didn't work (don't retry):** <approach> — FAILED, reason: <...>. (Highest-value lines — never lost: `/keel-distill` moves them to `LESSONS.md [fail]`, not to the trash.)
- **(c) Latest updates:** <most recent changes>
- **(d) Next steps:** <what to do next session, in priority order>

---

## Open questions / pending user decisions
<!-- GLOBAL section — survives rotation untouched until each item is resolved (then delete it). -->
- <topics awaiting a decision>

---

## Scaling: per-area handovers (optional)
Default: this single root file. On a large multi-area project an area may get its own
`<area>/HANDOVER.md` behind a nested `<area>/CLAUDE.md`, with this file as the program-level index —
see `docs/memory-files.md`. Register any split in `docs/architecture.md`.
