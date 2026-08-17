---
name: keel-handover
description: Add this session's block to HANDOVER.md before ending or compacting — done / tried-failed / latest / next. Rotates via /keel-distill when the 3-block cap is hit.
---

# /keel-handover — write the session block

Add a new **session block** to the TOP of `HANDOVER.md`'s "Session blocks" section (rules.md §1.4).
Newest first; never edit past blocks. **Write the block in ENGLISH** even on a non-English project
(§9.31: HANDOVER/LESSONS are machine-read and `@`-imported every session — EN is the cheaper token
surface); TASKS/PLAN/reports lines you touch stay in the project language, and the user's verbatim
words may stay quoted as-is.

Steps:
1. Read the current `HANDOVER.md`. If it already has **3 blocks** (or exceeds ~150 lines), run
   `/keel-distill` first to rotate the oldest block out (critical facts → `LESSONS.md`, raw block →
   `docs/handover-archive.md`).
2. Write this session's block: `### <YYYY-MM-DD HH:MM> — @<git user.name> — <one-line status>` (time =
   when the block was first created; the `@<git user.name>` attributes the session's author so multi-user
   handovers stay legible — read it from `git config user.name`; single-user projects still get it, at
   zero cost). **One block per SESSION, not per day:** if THIS session already wrote a block
   (a mid-session handover, or /keel-compact re-running this), UPDATE that block in place — keep its
   original HH:MM. A NEW session always adds a NEW block, even on the same day — same-day sessions
   must stay distinguishable. The block contains:
   - **(a) Completed** — what was done, dated; link decisions to their ADR/docs; include one-liners for
     TASKS.md items finished this session (then delete them from TASKS.md). **Multi-user exception**
     (`.claude/project-owner` exists and you are NOT the owner): do not delete your finished items —
     MOVE each to a TASKS `## Review` section (create it if missing) as
     `- [x] <id> ... (@you) — evidence: reports/team/<@you>/<task>_fix_<date>.md`. **The evidence is a
     FILE — verify it EXISTS before writing the line** (a chat summary is not a delivery, rules.md
     §10.40): the solution note sits in YOUR author folder and its index line lands in
     `reports/team/README.md` as `delivered`. Pathless lines and missing files are flagged at session
     start, and the owner's probe may also test your UNDERSTANDING of the delivery (rules.md §10.41).
     Review ROUTING is then the owner/orchestrator's: mechanical verification is delegated and appends
     `— verified ✓ (owner part: <one sentence>)` to the line; on accept the OWNER deletes the item and
     flips the index line to `closed <date> accepted` (reject → back to `## Now` + one reason line,
     index back to `wip`). The owner's own items follow the normal delete flow.
   - **(b) Tried, didn't work** — approaches that failed + the reason, so they aren't retried. This is
     the highest-value section — don't skip it.
   - **(c) Latest updates** — the most recent concrete changes.
   - **(d) Next steps** — prioritized, for the next session.

   **Signal only — a block is project STATE for the next session, not a transcript.** Before writing a
   line, test it: would a FRESH session need it to continue, AND is it not already in `git log` or
   `.claude/ritual-log`? If it fails either test, drop it. EXCLUDE: VCS/ritual bookkeeping ("committed/
   pushed N commits", sha ranges, "ran /keel-distill / /keel-compact") and conversational meta ("user
   asked if I saved", "don't rush", who said what). A DECISION that merely touches git is different —
   keep the WHY ("left settings.json unstaged — it holds the machine's allow-list"), drop the mechanics.
   At the ~150-line cap this noise is exactly what crowds out the facts that matter.
3. **PLAN.md** (if the project uses it): flip the phase statuses that changed this session, refresh
   _Current focus_, regenerate the diagram block from the table (see `/keel-plan` step 2) — patch the file,
   never rewrite it wholesale. If the wip phase's gate looks MET (its `## Now` items all checked, gate
   evidence exists), **propose `/keel-phase-review`** to the user — don't run it unasked: flipping a
   phase to `done` is the review's job, not this skill's (rules.md §2.7).
4. Update the global **Open questions / pending user decisions** section (add new, delete resolved).
5. **Drain TASKS `## Discovered`** (an INBOX, not storage — this includes project variants like
   `## Discovered-team`): converge every line OUT — a real task → `## Next` (with a done-when) · a
   domain/provider fact → `docs/` (architecture "known limitations" / the project's R-request or
   integration doc) · a lesson → `LESSONS.md` · a design decision → an ADR · resolved/superseded →
   DELETE (git keeps it). Entries are ONE line; anything longer is a report/spec/ADR fragment — write
   it there, leave a pointer. A line that survives two handovers is in the wrong file; leave only this
   session's genuinely untriaged finds (the re-ground hook flags week-old leftovers).
6. Sweep the conversation for unwritten agreements (rules §9.31): any rule/test/gotcha agreed this
   session that isn't in `LESSONS.md` yet — ask, then append.
7. Set the `_Last updated:_` line to today's date + a one-line status.
8. Do NOT commit/push without user approval (rules.md §1.3, §6.15).
