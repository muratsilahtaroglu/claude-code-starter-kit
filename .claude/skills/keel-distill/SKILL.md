---
name: keel-distill
description: Consolidate project memory — rotate old HANDOVER blocks to the archive, promote critical facts to LESSONS.md, dedup/merge, and lint for contradictions. Run when caps are exceeded.
---

# /keel-distill — the memory consolidation ritual ("sleep" for the project)

Run when `HANDOVER.md` exceeds **3 session blocks / ~150 lines**, when `LESSONS.md` exceeds **~250** or
`TASKS.md` **~100 lines** (the SessionStart hook warns on all of these), or every ~5 sessions as hygiene —
that cadence is yours to keep, the hook only detects cap overflows. Memory that is written but never
reviewed degrades the project — consolidation is what keeps it useful (rules.md §9).

Propose the full plan, get user approval, then apply. Never lossy-delete.
(File-TREE clutter — stray scripts, logs, dead code — is not this ritual's job: that is `/keel-tidy`, §3.10.)

## 1. Rotate HANDOVER blocks (oldest first, until ≤2 blocks AND under ~150 lines)
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
  `rules.md` (conduct), a `.claude/skills/` skill (procedure), an ADR (decision), or — for a permanent
  DOMAIN fact (a data quirk, an API contract) — the relevant **docs** (`docs/architecture.md` "known
  limitations" / a guide), then drop it here. A lesson that binds only SPECIFIC files (a must-run
  test after touching X, an append-only dir, a never-hand-edit generated file) becomes a
  **path-scoped rule** — `.claude/rules/<name>.md` with `paths:` frontmatter: it loads ONLY when a
  matching file is touched, so it is cheaper than both `rules.md` and this file. Never put
  must-always-hold discipline there (a path rule stays unloaded after compaction until a match).
  The new rule is shown as its FULL text in the distill plan and lands owner-approved, written
  self-contained — constraint + why + check inline, evidence pointing only to permanent artifacts,
  never to TASKS/PLAN live state (`.claude/rules/README.md` "Writing discipline"). This is the main pressure valve on a long project's
  `[gotcha]` list: reference facts belong in docs, not the always-loaded `LESSONS.md`.

## 3. Prune TASKS.md
- Verify done items were deleted (their one-liner lives in HANDOVER (a)); delete any stragglers.
- **Drain `## Discovered` to convergence** (incl. project variants like `## Discovered-team`) — it is
  an INBOX, not storage: each line → `## Next` (real task, with done-when) · `docs/` known-limitations
  / R-request doc (domain/provider fact) · `LESSONS.md` (lesson) · an ADR (design decision) · DELETE
  (resolved/superseded — git keeps it). One line per entry; longer → a report/ADR + pointer here. A
  line surviving TWO distills is in the wrong file — after this step the section holds only the
  current week's untriaged finds. Refill `## Now` (max 3–5, per person on teams).

## 4. Lint the memory set (drift check)
- **Strip noise:** delete VCS/ritual bookkeeping ("pushed N commits", sha ranges, "ran /keel-distill")
  and conversational meta ("user asked if I saved", "don't rush") from HANDOVER — it's git-log /
  ritual-log-derivable, and it's usually what pushed the file over cap (keep decisions + their WHY).
- Contradictions between `rules.md` / `LESSONS.md` / `CLAUDE.md` — flag, ask the user which wins.
- **Decision/constraint drift (`docs/adr/` + `.claude/rules/`):** an *Accepted* ADR contradicted by a
  newer decision, a measurement, or the code as it now stands → PROPOSE `Superseded (by ...)` — the
  OWNER flips the status, never this ritual; a path-scoped rule whose constraint has been overtaken
  → propose rewrite or retirement the same way. Also verify each rule's `paths:` globs still match
  existing files (a glob matching nothing = the rule silently never loads — a dead rule), and the
  ADR README index still mirrors the folder. Same mirror check for `reports/team/README.md`: every
  report file has exactly ONE index line (an orphan = unfindable evidence; a duplicate diverges —
  field case: the same report indexed twice with two different status texts), and statuses use only
  the controlled vocabulary (`wip · delivered · verified — owner part: <…> · closed <date>
  accepted|rejected`, `[x]` only at closed).
- Stale claims (files/commands/paths that no longer exist) — fix or mark superseded.
- Stale cap HEADERS in the memory files themselves (e.g. a LESSONS.md header still quoting an old
  "~100"): correct to the current thresholds below — headers are prose, the SessionStart hook is the
  authority; they drift in adopted projects because `/keel-update` never touches PROTECTED memory files.
- Cap check (solo defaults — the project's `.claude/keel-caps` overrides them, rules §10.40):
  `HANDOVER.md` ≤ ~150 lines, `LESSONS.md` ≤ ~250, `TASKS.md` ≤ ~100, `CLAUDE.md` ≤ ~200,
  `rules.md` ≤ ~300 (rule budget §10.38 — merge/retire/promote to a hook, don't just append).

## 5. Report → approve → commit
Summarize: N blocks archived, M lessons added/merged/superseded/promoted, lint findings. On approval,
apply + propose a commit (rules.md §6.15). Never push without user approval.
