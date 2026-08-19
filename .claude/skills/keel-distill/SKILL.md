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

## 2. Consolidate LESSONS.md (write-policy: add / update / supersede / promote-and-delete — never LOSSY delete)
- **Scope-triage every entry first (A/B/C/D — the LESSONS header defines the tiers):** always-relevant
  stays; file-scoped graduates (below); a permanent domain fact → docs; superseded/closed/already-
  promoted → DELETE. Field measurement behind the triage: in a mature file ~52% of entries were
  file-scoped and any one task needed ~15% of the file — the always-on core is the minority
  (`reports/2026-08-17-lessons-scope-audit.md`).
- Merge duplicates and near-duplicates into the stronger phrasing (keep the earliest date).
- A contradicted-but-instructive entry is marked `SUPERSEDED by <entry/date>` — visible, dated.
- **Promote what has graduated:** a lesson applied 3+ times is no longer a lesson — move it into
  `rules.md` (conduct), a `.claude/skills/` skill (procedure), an ADR (decision), or — for a permanent
  DOMAIN fact (a data quirk, an API contract) — the relevant **docs** (`docs/architecture.md` "known
  limitations" / a guide). A lesson CLUSTER that binds only SPECIFIC files (a must-run
  test after touching X, an append-only dir, a never-hand-edit generated file) becomes a
  **path-scoped rule** — `.claude/rules/<name>.md` with `paths:` frontmatter: it loads ONLY when a
  matching file is touched, so it is cheaper than both `rules.md` and this file — **or a
  `paths:`-scoped SKILL** (`.claude/skills/<name>/SKILL.md`, same `paths:` format) when the cluster
  must SURVIVE a mid-task compaction: invoked skill bodies are the one scoped mechanism re-injected
  after compaction (≈5k tokens/skill, 25k total, truncation keeps the TOP — put the load-bearing
  lines first), while a path rule waits for the next file match. Never put
  must-always-hold discipline in either (that stays in LESSONS tier A / rules.md).
  The new rule/skill is shown as its FULL text in the distill plan and lands owner-approved, written
  self-contained — constraint + why + check inline, evidence pointing only to permanent artifacts,
  never to TASKS/PLAN live state (`.claude/rules/README.md` "Writing discipline").
- **Promotion DELETES the LESSONS entry** — lossless: the content lives in its target and git keeps
  the history. Never leave a "moved to X" stub (field case: 10 promoted entries left 42 lines of
  stubs, taxing every session). The ONE surviving pointer is a line in LESSONS `## Index`
  (what → where → when it loads) — add or refresh it in the same pass. This is the main pressure
  valve on a long project's `[gotcha]` list: reference facts belong in docs, file-scoped stock
  behind its trigger — not in the always-loaded core.

## 3. Prune TASKS.md
- Verify done items were deleted (their one-liner lives in HANDOVER (a)); delete any stragglers.
- **Drain `## Discovered` to convergence** (incl. project variants like `## Discovered-team`) — it is
  an INBOX, not storage: each line → `## Next` (real task, with done-when) · `docs/` known-limitations
  / R-request doc (domain/provider fact) · `LESSONS.md` (lesson) · an ADR (design decision) · DELETE
  (resolved/superseded — git keeps it). One line per entry; longer → a report/ADR + pointer here. A
  line surviving TWO distills is in the wrong file — after this step the section holds only the
  current week's untriaged finds. Refill `## Now` (max 3–5, per person on teams).

## 4. Sweep closed team reports to done/ (folder hygiene — orchestrator/owner only)
A long-running author folder drowns its open work: dozens of spec/fix files, no visual way to tell
finished from in-flight. The valve: a report whose task reached **`closed <date> accepted|rejected`**
in the index moves to its author's **`reports/team/<@tag>/done/`** — the flat folder then holds only
live work, and "what is @X still carrying?" becomes a directory listing again.

- **Only `closed` moves.** `wip · delivered · verified` are in flight — on the board, cited from
  `## Review` (the reground hook checks those paths against disk), never swept.
- **A move is `git mv` + citation rewrite, one pass.** Before moving, grep the repo for BOTH the full
  path and the bare filename; rewrite every hit (index line, LESSONS, ADRs, other reports) to the
  `done/` path in the same commit. A move that breaks one citation is worse than the clutter —
  this sweep is the ONE sanctioned exception to §10.40's "never moved", and the rewrite is what
  keeps the exception honest. Evidence subfolders (`<task>_<what>/`) move with their report.
- **Stays in the index, same section.** The `[x] closed` line keeps its status and history; only its
  file path gains `done/`. Throughput counting is untouched — done/ is INSIDE the author's folder.
- Same write authority as every shared-file transition: the ORCHESTRATOR/owner sweeps; workers never
  move files out of their own delivered set (§10.42).

## 5. Lint the memory set (drift check)
- **Strip noise:** delete VCS/ritual bookkeeping ("pushed N commits", sha ranges, "ran /keel-distill")
  and conversational meta ("user asked if I saved", "don't rush") from HANDOVER — it's git-log /
  ritual-log-derivable, and it's usually what pushed the file over cap (keep decisions + their WHY).
- **Header hygiene (every memory file, not just HANDOVER).** A header is DOCTRINE — how the file
  works, written once, frozen. Move OUT anything that is state: a date or changelog line, a
  measurement ("file is 202 lines"), a debt or pending decision (nobody triages a header, so it
  becomes a permanent complaint — send it to `## Discovered`, then a `## Next` item with a
  done-when), a cap NUMBER (write "cap: `.claude/keel-caps`" — a copy drifts from the file that sets
  it, which is why the stale-cap-header lint below exists), a chat quote. Also collapse teaching
  prose that merely restates `rules.md`: it is paid in every session by an `@`-imported file and the
  two wordings drift — the detail lives in `docs/memory-files.md`. What EARNS a header line is a
  timeless, non-obvious invariant (field example: *"this file is `@`-imported IN FULL — a lane
  heading is a WRITE boundary, not a context boundary"*). Measured on the template itself: the three
  imported files carried 110 header lines, 55 after this rule. (The SessionStart hook flags dated
  lines and hard-coded caps in a header.)
- Contradictions between `rules.md` / `LESSONS.md` / `CLAUDE.md` — flag, ask the user which wins.
- **Decision/constraint drift (`docs/adr/` + `.claude/rules/`):** an *Accepted* ADR contradicted by a
  newer decision, a measurement, or the code as it now stands → PROPOSE `Superseded (by ...)` — the
  OWNER flips the status, never this ritual; a path-scoped rule whose constraint has been overtaken
  → propose rewrite or retirement the same way. Also verify each rule's/skill's `paths:` globs still
  match existing files (a glob matching nothing = the rule silently never loads — a dead rule; brace
  expansions past the documented 1,000-pattern budget and malformed `[` brackets ALSO match nothing,
  silently), and the ADR README index still mirrors the folder.
- **LESSONS `## Index` router mirror:** every Index line's target file exists, and every
  graduated-lesson rule/skill/doc has its ONE Index line — an orphan cluster is invisible to
  sessions whose trigger hasn't fired; a dead line hides lessons that still exist. (The reground
  hook flags dead targets at session start; the missing-line direction is checked here.) Same mirror check for `reports/team/README.md`: every
  report file has exactly ONE index line (an orphan = unfindable evidence; a duplicate diverges —
  field case: the same report indexed twice with two different status texts), statuses use only
  the controlled vocabulary (`wip · delivered · verified — owner part: <…> · closed <date>
  accepted|rejected`, `[x]` only at closed), and the mirror counts `done/` files too — a `closed`
  line whose path lacks `done/` is a §4 sweep candidate, a non-closed line pointing INTO `done/`
  is a bug.
- Stale claims (files/commands/paths that no longer exist) — fix or mark superseded. Resolve bare
  BASENAMES against the tree before flagging: field measurement found ~54% of citations are
  basename-only and DO resolve — a naive path check reports them as false staleness.
- **Language drift (rules §9.31):** HANDOVER/LESSONS/worker boards are ENGLISH on every project.
  Convert only the lines this run already rewrites/merges/rotates (gradual, no bulk-translation pass:
  a mass rewrite risks meaning loss and buries the real diff) — quoted user wording stays as-is.
- Stale cap HEADERS in the memory files themselves (e.g. a LESSONS.md header still quoting an old
  "~100"): correct to the current thresholds below — headers are prose, the SessionStart hook is the
  authority; they drift in adopted projects because `/keel-update` never touches PROTECTED memory files.
- Cap check (solo defaults — the project's `.claude/keel-caps` overrides them, rules §10.40):
  `HANDOVER.md` ≤ ~150 lines, `LESSONS.md` ≤ ~250, `TASKS.md` ≤ ~100, `CLAUDE.md` ≤ ~200,
  `rules.md` ≤ ~400 — of which the stock template is ~290, so the project's own rules get ~110
  (rule budget §10.38 — merge/retire/promote to a hook, don't just append).

## 6. Report → approve → commit
Summarize: N blocks archived, M lessons added/merged/superseded/promoted, lint findings. On approval,
apply + propose a commit (rules.md §6.15). Never push without user approval.
