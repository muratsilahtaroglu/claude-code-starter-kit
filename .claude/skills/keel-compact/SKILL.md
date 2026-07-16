---
name: keel-compact
description: Pre-compact ritual — bring the disk fully up to date (runs the /keel-handover procedure, which cascades to /keel-distill, PLAN flips and the LESSONS sweep), verify freshness, then hand off to the built-in /compact. One command to remember instead of several.
---

# /keel-compact — refresh the disk, THEN compact

Compaction summarizes the conversation lossily; the pincer (PreCompact snapshot + SessionStart
re-ground) restores only what is ON DISK. This skill exists so a forgotten ritual can't turn a
manual compact into an information-loss event — the failure mode: `/compact` run with a stale
HANDOVER, and the snapshot faithfully backs up the stale file. Run it whenever you are about to
compact (or the context feels near-full). The individual skills stay directly invokable as
always — this is the umbrella, not a replacement.

1. **Run the full `/keel-handover` procedure** (rules.md §1.4) — it already cascades:
   `/keel-distill` when caps are hit, the session block (a)–(d), PLAN.md status flips + the
   regenerated diagram, TASKS.md cleanup, and the §9.31 sweep of unwritten agreements into
   `LESSONS.md`. Do not duplicate its steps here — invoke it.
2. **Freshness gate** — report a short pass/fail checklist; fix gaps before proceeding:
   - [ ] `HANDOVER.md` top block is dated TODAY and describes THIS session (not a stale block).
   - [ ] `TASKS.md ## Now` matches reality; finished items deleted (one-liners in block (a)).
   - [ ] No agreement / gotcha / failed approach from this conversation is still unwritten (§9.31).
   - [ ] Caps respected: HANDOVER ≤ 5 blocks / ~200 lines · LESSONS/TASKS ≤ ~100 (else `/keel-distill`).
   - [ ] `PLAN.md` statuses + _Current focus_ current (if the project uses PLAN.md).
3. **Offer an approved commit** of the memory files (rules.md §1.3, §6.15) — git is the second
   safety net beside `.claude/snapshots/`: even a bad summary then loses nothing.
4. **Hand off:** tell the user — "Disk is fresh; now run `/compact`." A skill CANNOT invoke the
   built-in `/compact` itself; stop here and let the user trigger it.

Scope honesty: this covers MANUAL compacts only. Auto-compact fires without warning — the defense
there remains the hot-path discipline (§9.31: write it the moment it appears) + the pincer. For
full determinism you can disable auto-compact in `/config` and compact only via this ritual
(trade-off: forget too long and the session hits the hard context limit mid-turn).
