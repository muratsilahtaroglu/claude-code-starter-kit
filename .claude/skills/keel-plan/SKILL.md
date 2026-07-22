---
name: keel-plan
description: Create or revise PLAN.md — propose the phase DAG (phases · gates · dependencies) from the user's goal, get approval, write the table and regenerate the colored Mermaid diagram from it. Statuses flip at rituals (/keel-handover, /keel-phase-review); post-completion fixes land in the Fix log.
---

# /keel-plan — build and maintain the phase map

When: at bootstrap right after the tailoring (rules.md §0), whenever the user asks for a plan or a
re-plan, or when scope changes enough that the DAG no longer matches reality. `PLAN.md` is the strategic
view; `TASKS.md` stays the tactical board — never duplicate checkboxes across them.

1. **Propose.** From the user's goal derive phases + sub-phases, each with: id (`p1`, `p1_2` — lowercase
   `[a-z0-9_]`), a **gate** (verifiable done-when, same spirit as TASKS.md), `after` dependencies
   (siblings with no mutual `after` may run in parallel), and — on a multi-user project — an `owner`
   (the person's `git config user.name`; blank = anyone). Ask who owns what when parallel branches are
   assigned to different people; only the owner advances an owned phase (`/keel-autopilot` stops at a
   foreign one). Single-user projects leave `owner` blank.
   **Multi-user governance:** when the project declares itself multi-user, ASK who the PROJECT owner
   (founder) is — never assume it's whoever is bootstrapping — and write their `git config user.name`
   as the single line of **`.claude/project-owner`**. That file arms the `owner-guard` hook (governance
   files — PLAN/rules/CLAUDE/architecture/ADR/.claude — become owner-only) and the session role line.
   Assignments (`@name` tags in TASKS, the `owner` column here) are then the OWNER's call
   (docs/steering.md "Multi-user"). Single-user: no file, nothing changes. Map **product** phases only — what the project
   builds and ships. One-time meta/tooling work (a mid-project tool adoption, a dependency/CVE sweep, a
   pure refactor) is **not** a phase node: record it in an ADR and/or the Fix log. A meta stub given an
   `after` becomes a permanent dead-end fork in the graph — exactly the noise the map should avoid. Show
   the table draft — **apply only after approval** (§10.36).
2. **Write `PLAN.md`.** Patch the phase table (SOURCE OF TRUTH) and _Current focus_; **regenerate the
   whole diagram block from the table** between the `KEEL_PLAN_DIAGRAM` markers — never hand-edit inside,
   never rewrite the rest of the file (patch, don't clobber). One syntax slip breaks the whole GitHub render.

   **Canonical diagram spec — this skill OWNS it.** (`PLAN.md` is PROTECTED by `/keel-update`, so palette
   fixes reach existing projects only through this skill's regeneration, not by editing their PLAN header.)
   - **Node id = the phase id** (`p1`, `a2`), NOT "Phase 1"; label reads `id short-name` so table, TASKS,
     Fix-log and diagram key on ONE token. **Order is the ARROWS, never the number** — a big id on a
     parallel branch may finish before a small one (that is normal in a DAG, not a mistake to hide).
   - **Status → semantic class** (a plan at rest must not look alarming — reserve red for real trouble):
     ```
     classDef done    fill:#2e7d32,color:#ffffff,stroke:#1b5e20
     classDef wip     fill:#f9a825,color:#000000,stroke:#e65100,stroke-width:3px
     classDef todo    fill:#eceff1,color:#37474f,stroke:#b0bec5,stroke-dasharray:4 3
     classDef blocked fill:#c62828,color:#ffffff,stroke:#8e0000
     ```
     done green · wip amber+**thick** border (the "you are here") · todo neutral grey+**dashed** (not-started
     ≠ broken) · blocked red (reserved). Emit a one-line legend just above the fence:
     `> yeşil done · **amber** wip · gri-kesik todo · kırmızı blocked — sıra OKLARDA, numarada değil.`
   - **Mermaid safety** (GitHub ~v10): ids `[a-z0-9_]`; every node on its own line, edges below; labels
     `"double-quoted"`, ASCII only — no emoji, no unquoted `()`, no lowercase `end`; solid `-->` =
     depends-on, dotted `-.->` = contains; every `classDef` pairs `fill` with `color`; no `%%{init}%%`.
3. **Seed the board.** Refill `TASKS.md ## Now` (3–5 items max) from the wip leaf's gate; reference the
   phase id in each item so the Fix log and HANDOVER one-liners can point back.
4. **Status lifecycle.** `todo → wip → done`, flipped at rituals: `/keel-handover` updates statuses +
   _Current focus_ each session; `/keel-phase-review` is the only gate to `done`. `done` never flips back —
   a bug found later is a **Fix log row** (`date | fix | phase-id`), which keeps the map honest after
   the project completes.
5. **Re-planning (experiments change the plan).** `PLAN.md` always shows ONLY the latest plan: phases
   dropped in a re-plan are **removed entirely** from the table and diagram — no tombstone rows or
   statuses. The failed approach is already recorded in `LESSONS.md [fail]` / HANDOVER block (b), and
   git history keeps every earlier shape of the plan. `done` phases stay; existing ids are never
   renumbered (Fix log / HANDOVER references must keep resolving).
5. **Drift.** The SessionStart hook warns when the table and diagram disagree or when a wip phase has an
   empty `TASKS.md ## Now` — fix by regenerating from the table (this skill), not by editing the diagram.
