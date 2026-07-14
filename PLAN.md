# PLAN.md — phase map (TEMPLATE)

> The **strategic** view: phases, gates, and the dependency graph — where the whole journey stands.
> The **tactical** board is `TASKS.md` (`## Now` feeds from the wip phase's gate); never duplicate its
> checkboxes here. Updated at **ritual points only**: `/plan` creates/revises the map, `/handover` flips
> statuses + refreshes *Current focus*, `/phase-review` turns a finished phase's gate green. The
> SessionStart hook cross-checks table ↔ diagram ↔ TASKS and warns on drift. **Not `@`-imported**
> (zero always-on context cost) — read it when orienting. **Cap ~150 lines / ~30 nodes** (split
> per-phase diagrams beyond that).

_Current focus: <p1_2 — one line on what is actively being pushed>_

<!-- REPLACE this example at bootstrap (run /plan) -->

## Phase table (SOURCE OF TRUTH — the diagram below is regenerated from this)

Statuses: `todo` → `wip` → `done` (a fix on a done phase goes to the Fix log — never flip done back).
`after` = dependency (comma-separated ids). A phase is `done` only when its gate passed `/phase-review`.
This file holds ONLY the latest plan — phases dropped by a re-plan are removed, not marked (failures
live in `LESSONS.md`; git history keeps every earlier plan).

| id | phase | status | after | gate (done-when) | since |
|---|---|---|---|---|---|
| p0 | Bootstrap | done | - | tailoring applied + recorded | <YYYY-MM-DD> |
| p1 | Data layer | wip | p0 | ingest e2e green | <YYYY-MM-DD> |
| p1_1 | Schema | done | - | migrations apply clean | <YYYY-MM-DD> |
| p1_2 | Ingest worker | wip | p1_1 | e2e ingest test green | <YYYY-MM-DD> |
| p2 | API | todo | p1 | CRUD + auth smoke green | |

## Diagram (regenerated from the table — do NOT hand-edit between the markers)

Conventions (GitHub renders ~Mermaid v10; violating these breaks the WHOLE diagram): ids `[a-z0-9_]`;
every node DEFINED on its own line, edges below; labels always `"double-quoted"`, ASCII only — **no
emoji, no `(`/`)` unquoted, no lowercase `end`**; solid `-->` = depends-on, dotted `-.->` = contains;
every `classDef` pairs `fill` with `color` (dark-mode); never force a theme via `%%{init}%%`.

<!-- KEEL_PLAN_DIAGRAM_BEGIN -->
```mermaid
flowchart TD
  p0["Phase 0 - bootstrap"]:::done
  p1["Phase 1 - data layer"]:::wip
  p1_1["1.1 schema"]:::done
  p1_2["1.2 ingest worker"]:::wip
  p2["Phase 2 - API"]:::todo
  p0 --> p1
  p1 -.-> p1_1
  p1 -.-> p1_2
  p1 --> p2
  classDef done fill:#2e7d32,color:#ffffff,stroke:#1b5e20
  classDef wip fill:#f9a825,color:#000000,stroke:#b28704
  classDef todo fill:#c62828,color:#ffffff,stroke:#8e0000
```
<!-- KEEL_PLAN_DIAGRAM_END -->

## Fix log (after completion too: every update/bugfix maps to the phase it touched)

| date | fix | phase |
|---|---|---|
| <YYYY-MM-DD> | <what was fixed, one line> | <p1_2> |
