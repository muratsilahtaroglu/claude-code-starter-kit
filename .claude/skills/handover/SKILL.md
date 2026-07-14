---
name: handover
description: Add this session's block to HANDOVER.md before ending or compacting — done / tried-failed / latest / next. Rotates via /distill when the 5-block cap is hit.
---

# /handover — write the session block

Add a new **session block** to the TOP of `HANDOVER.md`'s "Session blocks" section (rules.md §1.4).
Newest first; never edit past blocks.

Steps:
1. Read the current `HANDOVER.md`. If it already has **5 blocks** (or exceeds ~200 lines), run
   `/distill` first to rotate the oldest block out (critical facts → `LESSONS.md`, raw block →
   `docs/handover-archive.md`).
2. Write this session's block: `### <YYYY-MM-DD> — <one-line status>` with:
   - **(a) Completed** — what was done, dated; link decisions to their ADR/docs; include one-liners for
     TASKS.md items finished this session (then delete them from TASKS.md).
   - **(b) Tried, didn't work** — approaches that failed + the reason, so they aren't retried. This is
     the highest-value section — don't skip it.
   - **(c) Latest updates** — the most recent concrete changes.
   - **(d) Next steps** — prioritized, for the next session.
3. **PLAN.md** (if the project uses it): flip the phase statuses that changed this session, refresh
   _Current focus_, regenerate the diagram block from the table (see `/plan` step 2) — patch the file,
   never rewrite it wholesale.
4. Update the global **Open questions / pending user decisions** section (add new, delete resolved).
5. Sweep the conversation for unwritten agreements (rules §9.31): any rule/test/gotcha agreed this
   session that isn't in `LESSONS.md` yet — ask, then append.
6. Set the `_Last updated:_` line to today's date + a one-line status.
7. Do NOT commit/push without user approval (rules.md §1.3, §6.15).
