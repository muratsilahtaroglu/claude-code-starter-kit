# docs/memory-files.md — how the four memory files work (read at bootstrap, not every session)

`HANDOVER.md` · `LESSONS.md` · `TASKS.md` are `@`-imported by `CLAUDE.md` into **every** session and
re-injected after **every** compaction. `PLAN.md` is not imported — it is read when orienting.

This guide holds the detail. The files themselves keep a **short header** — their own contract plus a
pointer here — because a header in an `@`-imported file is paid in every session, forever, and the
same doctrine already lives in `rules.md §9`. Stating it a third time in longer prose is not
belt-and-braces; it is a third thing that can drift out of agreement with the other two.

## The header rule: DOCTRINE, not STATE

> A memory file's header says **how the file works**. It is written once (from the template),
> tailored at bootstrap, and then frozen. Anything that is **true right now** belongs in the body.

Concretely, a header line carrying any of these is in the wrong place:

| In a header | Why it's wrong | Where it belongs |
|---|---|---|
| A date (`2026-08-18: raised 350→500`) | changelog in a live document | git history; the decision itself is the record |
| A measurement (`file is 202 lines — cap ~150`) | a finding, and it rots the moment it's true again | `TASKS.md ## Discovered`, then a `## Next` item with a done-when |
| A pending decision (`owner kararı bekliyor`) | nobody triages a header; it becomes a permanent complaint | `TASKS.md` or `HANDOVER.md` "Open questions" |
| A cap NUMBER | `.claude/keel-caps` is the authority — a copy drifts from it | write "cap: `.claude/keel-caps`" and stop |
| A chat quote (`owner said "TASKS=500 yaptım"`) | provenance for a value that already has a home | the keel-caps comment, or an ADR if it was a real decision |
| Teaching prose restating `rules.md` | paid twice per session, and the two wordings drift apart | this file |

What **does** earn a header line: a non-obvious invariant a reader would otherwise get wrong. Field
example worth keeping — *"this file is `@`-imported IN FULL; a lane heading is a WRITE boundary, not a
context boundary"* — it is timeless, correcting, and one line.

One exception, by construction: `HANDOVER.md`'s `_Last updated: <date>_` freshness stamp sits
OUTSIDE the doctrine blockquote and is meant to change. Both checks below look only at the `>` block,
so it is never flagged.

`/keel-distill` §4 lints headers on this rule; the SessionStart hook flags dated lines and hard-coded
cap numbers inside a header.

## `HANDOVER.md` — what happened, newest first

One dated block per session: **(a)** completed · **(b)** tried and failed, with the reason · **(c)**
latest updates · **(d)** next steps. Block (b) is the highest-value part and the one distillation
never discards — it is what stops the next session re-walking a dead end.

- Written **before** every compact/session end (`/keel-handover`; `/keel-compact` bundles it).
- **English**, on every project (rules §9.31) — machine-read, always imported, so EN is the cheaper
  token per always-on line. Quoted owner wording may stay in its own language.
- Cap: 3 blocks / see `.claude/keel-caps`. On overflow `/keel-distill` moves the oldest block's
  critical facts into `LESSONS.md` and the raw block **verbatim** into `docs/handover-archive.md`.
  The archive is never imported — grep it on demand.
- Strip session narration as you write: "pushed N commits", sha ranges, "ran /keel-distill", "user
  asked if I saved". Keep decisions and their WHY.

**Scaling (optional).** On a large multi-area project each area may get its own
`<area>/HANDOVER.md` with the same block format and cap, wired through a nested `<area>/CLAUDE.md`
`@`-import so it loads only when working there; the root file becomes the program-level index — one
"latest" per area, no duplicated truth. Register the split in `docs/architecture.md`. On human teams
the same valve applies per person (`handovers/HANDOVER-<user>.md`). Start with one file; split only
when it hurts.

## `LESSONS.md` — what we learned, still true

The project's editable knowledge base: rules discovered mid-project, must-run tests, gotchas, failed
approaches. Different from `rules.md`, which is the constitution written at project start.

- **Hot path:** the moment the user corrects you, an approach fails, or a rule/test is agreed — ask
  *"shall I note this?"* and on approval append it **immediately**. Never "at compact time":
  conversation-only agreements are exactly what compaction destroys. Unsure where it belongs? Write
  it here — misfiled beats lost, `/keel-distill` re-files it.
- **English**, same reasoning as HANDOVER. Two exceptions: quoted owner wording, and a
  **language-specific domain fact** (morphology, a locale's casing/collation trap) whose example
  would be destroyed by translation.
- **Format:** atomic **one-line** entries, dated and tagged (`[rule] [test] [fail] [gotcha]`), newest
  first within a tag group. A lesson later proven WRONG is retired: the entry moves verbatim to
  `docs/lessons-retired.md` (never imported) with its refutation, and ONE corrective line stays —
  never silently removed, never a `SUPERSEDED` stub paying rent every session for false knowledge.

### Scope triage — the file holds ALWAYS-relevant lessons only

Every line is paid in every session, and an irrelevant line is not merely token cost: context-rot
measurements show a single distractor degrades retrieval of the lines that DO apply
(`research/web/findings.md`). A field audit of a mature project found only ~26% of accumulated
lessons were always-relevant, ~52% bound specific files, and any one task needed ~15% of the file
(`reports/2026-08-17-lessons-scope-audit.md`). So, per entry:

- **(A) Always-relevant** (verification duty, measurement epistemics, protocol) → stays.
- **(B) File/area-scoped** (matters only when touching X) → a `paths:`-scoped `.claude/rules/<name>.md`
  — or a **`paths:`-scoped SKILL** when the cluster must survive a mid-task compaction (invoked skill
  bodies re-inject; a path rule waits for the next file match).
- **(C) Permanent domain/API fact** → `docs/` (architecture "known limitations", or a guide).
- **(D) Superseded / closed / promoted** → **deleted**. Git is the archive.

**Promotion deletes the entry.** Never leave a "moved to X" stub — a field case left 42 lines of them,
taxing every session. The one surviving pointer is a line in the file's `## Index` router:
*what → where → when it loads*.

**Watch entry BODY, not just line count.** Two audits of the same project found the file shrinking by
entry count while the average entry grew (5.2 → 6.2 lines; 3 of 63 entries were the prescribed
one-liners). A 40-line entry is a report living in an always-loaded file: keep the lesson, move the
case narrative to `reports/`, leave one line and a path.

**Scaling (optional).** Same per-area valve as HANDOVER — `<area>/LESSONS.md` behind a nested
`<area>/CLAUDE.md`. Scope triage is the FIRST valve; splitting is the second.

## `TASKS.md` — what is being worked on

Cross-session tasks. Claude Code's built-in todos are session scratch (ephemeral, machine-local);
this file is the single cross-session source of truth.

- **Work only from `## Now`** (max 3–5 per person). Refill from `## Next` when it empties.
- Every item carries a verifiable **`done-when:`**. Removing or weakening a `done-when:` to make a
  task pass is not acceptable.
- **Delete on done:** `[x]` immediately; at `/keel-handover` the item is deleted as its one-liner
  lands in the new HANDOVER block (a). Git history is the archive.
- `## Discovered` is an **inbox, not storage**: one line the moment something is noticed, then back to
  your task; at handover/distill every line converges OUT (→ `## Next` with a done-when · docs ·
  LESSONS · ADR · deleted if resolved). The SessionStart hook flags lines older than ~a week.
- Inline tags: `blocked-by:` · `discovered-from:` · `due: YYYY-MM-DD` (past dates surface at session
  start) · `@owner`.

### Ids

Per-lane and stable: each lane (agent or person) owns a 2–4 letter lowercase prefix fixed when the
lane is born, and its items run `co1 · co2 · co3 …`. Numbers are allocated by the **orchestrator
only** — two same-machine sessions would otherwise mint the same one. An id is **never renamed and
never reused**: it also names `reports/team/<author>/<id>_*.md` and `scratch/<id>/`, and renaming
dangles permanent artifacts. Reassignment moves the id WITH the work, so the prefix records which
lane a task was *opened for*; per-person throughput is counted from the author folder. One case for
the whole series — a series split across `r1` and `R28` makes every count wrong. Count with
`grep -w`: `co1` is a prefix of `co19`.

### Multi-user and agent lanes

An item may carry `@owner` (the owner's `git config user.name`). Work only unassigned items or your
own; an item tagged for someone else is **surfaced, not done**. On owner-run projects
(`.claude/project-owner` exists) assigning tags is the owner's call.

AI co-agent sessions (rules §10.42) follow the same discipline, with one addition: on same-machine
agent teams the lane is **read-only to the worker**. Progress and findings live on the worker's own
`reports/team/<name>/board.md`; the orchestrator syncs them in. Same-machine sessions have no git
merge layer, so every shared file gets exactly one writer.

### Owner review (four states)

A developer does not delete their finished item — it moves to a `## Review` section and the line
**names its evidence file**:

```
- [x] co7 <what> (@dev) — evidence: reports/team/<@dev>/co7_fix_<date>.md
```

A chat summary is not a delivery; the reground hook flags pathless lines and files missing on disk.
Routing is the owner's/orchestrator's call alone; the mechanical half is delegated to a verifier
whose report appends `— verified ✓ (owner part: <one sentence>)`. The owner performs that named step,
then accepts (delete → HANDOVER (a); index → `closed <date> accepted`) or rejects (back to `## Now`
with one reason line). State chain and index format: `reports/team/README.md`.

## `PLAN.md` — where the whole journey stands

The strategic view: phases, gates, dependency graph. `TASKS.md` is the tactical board and `## Now`
feeds from the wip phase's gate — never duplicate its checkboxes here.

- Updated at **ritual points only**: `/keel-plan` creates or revises the map, `/keel-handover` flips
  statuses and refreshes *Current focus*, `/keel-phase-review` turns a finished phase's gate green.
- The phase table is the source of truth; the diagram is regenerated from it. The SessionStart hook
  cross-checks table ↔ diagram ↔ TASKS and warns on drift.
- **Not `@`-imported** — zero always-on cost, so the pressure here is staleness, not tokens.
- *Current focus* is **one line**: the phase being pushed and its single blocker. It is a pointer, not
  a status report — test counts, evidence lists and audit debts belong in HANDOVER (a) or a report.
  Field case: it grew to 15 lines of session narration that had to be maintained or it lied.
- A fix on a `done` phase goes to the Fix log; never flip `done` back.
