---
name: plan
description: Create or revise PLAN.md — propose the phase DAG (phases · gates · dependencies) from the user's goal, get approval, write the table and regenerate the colored Mermaid diagram from it. Statuses flip at rituals (/handover, /phase-review); post-completion fixes land in the Fix log.
---

# /plan — build and maintain the phase map

When: at bootstrap right after the tailoring (rules.md §0), whenever the user asks for a plan or a
re-plan, or when scope changes enough that the DAG no longer matches reality. `PLAN.md` is the strategic
view; `TASKS.md` stays the tactical board — never duplicate checkboxes across them.

1. **Propose.** From the user's goal derive phases + sub-phases, each with: id (`p1`, `p1_2` — lowercase
   `[a-z0-9_]`), a **gate** (verifiable done-when, same spirit as TASKS.md), and `after` dependencies
   (siblings with no mutual `after` may run in parallel). Map **product** phases only — what the project
   builds and ships. One-time meta/tooling work (a mid-project tool adoption, a dependency/CVE sweep, a
   pure refactor) is **not** a phase node: record it in an ADR and/or the Fix log. A meta stub given an
   `after` becomes a permanent dead-end fork in the graph — exactly the noise the map should avoid. Show
   the table draft — **apply only after approval** (§10.36).
2. **Write `PLAN.md`.** Patch the phase table (SOURCE OF TRUTH) and _Current focus_; **regenerate the
   whole diagram block from the table** between the `KEEL_PLAN_DIAGRAM` markers — never hand-edit inside,
   never rewrite the rest of the file (patch, don't clobber). Diagram rules are printed above the block
   in PLAN.md (quoted ASCII labels, no emoji, one node definition per line, fill+color pairs) — one
   syntax slip breaks the whole render on GitHub.
3. **Seed the board.** Refill `TASKS.md ## Now` (3–5 items max) from the wip leaf's gate; reference the
   phase id in each item so the Fix log and HANDOVER one-liners can point back.
4. **Status lifecycle.** `todo → wip → done`, flipped at rituals: `/handover` updates statuses +
   _Current focus_ each session; `/phase-review` is the only gate to `done`. `done` never flips back —
   a bug found later is a **Fix log row** (`date | fix | phase-id`), which keeps the map honest after
   the project completes.
5. **Re-planning (experiments change the plan).** `PLAN.md` always shows ONLY the latest plan: phases
   dropped in a re-plan are **removed entirely** from the table and diagram — no tombstone rows or
   statuses. The failed approach is already recorded in `LESSONS.md [fail]` / HANDOVER block (b), and
   git history keeps every earlier shape of the plan. `done` phases stay; existing ids are never
   renumbered (Fix log / HANDOVER references must keep resolving).
5. **Drift.** The SessionStart hook warns when the table and diagram disagree or when a wip phase has an
   empty `TASKS.md ## Now` — fix by regenerating from the table (this skill), not by editing the diagram.
