---
name: keel-distill
description: Consolidate project memory — rotate old HANDOVER blocks to the archive, promote critical facts to LESSONS.md, dedup/merge, and lint for contradictions. Run when caps are exceeded.
---

# /keel-distill — the memory consolidation ritual ("sleep" for the project)

Run when `HANDOVER.md` exceeds **5 session blocks / ~200 lines**, when `LESSONS.md` or `TASKS.md`
exceeds **~100 lines** (the SessionStart hook warns on all of these), or every ~5 sessions as hygiene —
that cadence is yours to keep, the hook only detects cap overflows. Memory that is written but never
reviewed degrades the project — consolidation is what keeps it useful (rules.md §9).

Propose the full plan, get user approval, then apply. Never lossy-delete.

## 1. Rotate HANDOVER blocks (oldest first, until ≤4 blocks AND under ~200 lines)
For each block being rotated, triage by criticality — **content-aware, not age-blind**:
- **(b) Tried, didn't work** → PERMANENT: distill each to one `LESSONS.md [fail]` line
  (`<date> — <approach> → FAILED: <reason>. (full trace: docs/handover-archive.md, block <date>)`).
- **Open questions** live in HANDOVER's global section, not in blocks — leave them until resolved.
- **(a) Completed** → nothing to move: git history + the archive keep it.
- **(c) Latest updates** → superseded by newer blocks — nothing to promote; the verbatim archive keeps it.
- **(d) Next steps** of an old block → dead (that work is done or re-planned) — no promotion.
- Then move the WHOLE block **verbatim** to the TOP of `docs/handover-archive.md` (prepend, newest
  first — restorable compression: the distilled lines keep pointers back to it).

## 2. Consolidate LESSONS.md (write-policy: add / update / supersede — never silent delete)
- Merge duplicates and near-duplicates into the stronger phrasing (keep the earliest date).
- A contradicted entry is marked `SUPERSEDED by <entry/date>` — visible, dated, never just removed.
- **Promote what has graduated:** a lesson applied 3+ times is no longer a lesson — move it into
  `rules.md` (conduct), a `.claude/skills/` skill (procedure), or an ADR (decision), and drop it here.

## 3. Prune TASKS.md
- Verify done items were deleted (their one-liner lives in HANDOVER (a)); delete any stragglers.
- Triage `## Discovered` into `## Next` (or drop with a reason); refill `## Now` (max 3–5).

## 4. Lint the memory set (drift check)
- Contradictions between `rules.md` / `LESSONS.md` / `CLAUDE.md` — flag, ask the user which wins.
- Stale claims (files/commands/paths that no longer exist) — fix or mark superseded.
- Cap check: `HANDOVER.md` ≤ ~200 lines, `LESSONS.md` ≤ ~100, `TASKS.md` ≤ ~100, `CLAUDE.md` ≤ ~200,
  `rules.md` ≤ ~200 (rule budget §10.38 — merge/retire/promote to a hook, don't just append).

## 5. Report → approve → commit
Summarize: N blocks archived, M lessons added/merged/superseded/promoted, lint findings. On approval,
apply + propose a commit (rules.md §6.15). Never push without user approval.
