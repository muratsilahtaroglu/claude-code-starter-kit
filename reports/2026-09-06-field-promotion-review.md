# 2026-09-06 — the field project → kit promotion review (v0.8.36)

**Source:** The field project's observer brief of 2026-09-06 (25 candidates,
written by @observer against the field project's copy of kit v0.8.34). **Method (rules §10.37):** every candidate was
measured on BOTH sides before a verdict — the field project's commit/file/test opened, the kit's current file diffed —
not taken from the brief's sentence. The field project was not touched (kit-first; the field project pulls via `/keel-update`).

Verdict vocabulary: **ENTERS** · **NARROWER form enters** · **ALREADY in kit** · **DOES NOT ENTER**.

| # | Candidate | Field-project evidence (measured) | Verdict | Reason (one line) | Landed in kit |
|---|---|---|---|---|---|
| A1 | Twin resolver: live = NEWEST pid per session-id, not `attached` | `c1366ff` · `.claude/team-addresses.py` · 21-cell test matrix passes | **ENTERS** | Kit's 09-03 axis (`attached`) measured blind: per VS Code BUILD, 11/11 read attached; the field project's version is a strict superset of the kit's own file | `.claude/team-addresses.py` · `tests/unit/test_keel_team_addresses.py` (21 cells) · `docs/steering.md` twin paragraph rewritten |
| A2 | `make team-clean` — table, never `kill` | `bd58af3`+`c1366ff` Makefile target | **ENTERS** (English, 4-line comment) | Frozen `kill <pid>` is a security error (pid recycling); kit Makefile had no team target | `Makefile` `team-clean` |
| A3 | Item CHARACTER budget ≤400, monotone descent, axes separate | `b9bee55` · `entry-budget.py` · 19-cell test matrix passes; 0/27 items complied, median 1287 | **ENTERS** | Kit counted LINES only — 4 lines × 180 chars was a solution note with hard wraps; per-axis tracking pinned by a mutation cell | `.claude/hooks/entry-budget.py` · `tests/unit/test_keel_entry_budget.py` · `TASKS_ENTRY_CHARS` cap · rules §10.40 · hooks README |
| A4 | Commit-time fast test subset | idea approved  — **no target in the field project's Makefile, not measured** | **NARROWER** (opt-in) | Unproven mechanism; a mandatory commit-time suite would block docs-only commits. Shipped as a `test-fast` target + a commented pre-commit hook | `Makefile` `test-fast` · `.pre-commit-config.yaml` (commented block) |
| A5 | Citation gate: absence marker · `done/` · `.claude` axis · self-scope | `scripts/citation_head_check.py` (749 lines) | **NARROWER** | Kit already had `done/`, the `.claude` tree (via `repo_roots`), the positive control and BY-DESIGN class. Missing: the absence marker and the live-anchor class — both ported, generic names | `citation-gate.py`: `(RECORDED-ABSENT)` + `board.md:N`/TASKS/HANDOVER/LESSONS/PLAN anchor WARNING (exit 0) · 2 new test cells |
| A6 | compact-gate checks "approved suggestion has a governance diff" | idea only, no hook in the field project | **DOES NOT ENTER** | "Was an approval landed" is not machine-decidable at PreCompact; covered as a RECORD by E1's follow-up table instead | — (see E1) |
| B1 | `/keel-continue` orchestrator: queue ≥2 deep, delivery names next item | audit §12; lanes idled a weekend | **ENTERS** | Kit's IDLE was written as legitimate for workers — right — but nothing made the orchestrator pre-queue | `keel-continue` §3 ASSIGN · charter "reporting done → … · next:" form |
| B2 | Epic sub-item step-over in the skill | ADR-0013 countermeasure existed only as text | **ENTERS** | ADR named the step; no skill carried it | `keel-continue` §3 ROUTE "EPIC step-over" |
| B3 | Owner-absence protocol | `rules.md §10.42`; ran live 09-05/06: 4 lanes, 0 owner questions, Review 17→6 | **ENTERS** | Measured to work; kit had nothing for "owner away" | rules §10.42 "Owner absence" |
| B4 | LESSONS cold layer (`docs/retro/`) | `rules §9.33` · `docs/retro/README.md`; LESSONS stuck 1000/1000, 82/132 single-copy | **ENTERS** | Kit had retire (wrong) and promote (3+ uses) — no exit for true-but-uncited; the proxy criterion is labelled as a proxy | `docs/retro/README.md` · `keel-distill` §2 COOL · rules §9.33 · LESSONS header · `docs/memory-files.md` (E) |
| B5 | Owner round SLICED by observation | RV121: 17 items → 6 questions + 3 desk lines, partition sums | **ENTERS** | Kit's ROUTE handed the owner a list; the splitting axis is the QUESTION, not the item | `keel-continue` §3 ROUTE |
| B6 | `/keel-stats` process metrics | audit §0 table, derived by hand; **no script in the field project** | **ENTERS** (built here first) | Numbers nobody sees until someone counts; generator is deterministic git+tree, classifier written down | `.claude/ritual-report.py` `process_metrics()` · `keel-stats` SKILL |
| C1 | Tiers T0/T1/T2 decide `## Review` | ADR-0012 + `§10.41`; Review 17→15, Now 11→7 on first pass; 45 items/37 no owner part before | **ENTERS** | Kit routed everything with "owner may waive trivia" — ceremony was habit, not risk | rules §10.41 TIER · `keel-continue` ROUTE · orchestrator charter text |
| C2 | Premise measured first; assigner not the authority | `rules §10.41` (09-03) | **ALREADY in kit** (v0.8.34) | rules §10.41 already carries "The assigner is not the authority on the premise; the measurement is" + the 26-delivery field line | — |
| C3 | Class-shaped item names surfaces by SEARCH | `rules §10.39` | **ALREADY in kit** (v0.8.34) | rules §10.39 "A CLASS-shaped task names its SURFACES first" + 28/4/20 field line | — |
| C4 | Lane `status` file + live table | `scripts/serit_durumu.py` · 4 lanes write `durum` | **NARROWER** | Mechanism yes (one line, one writer); the python table is replaced by a 1-line `make team-status` — no new script surface | rules §10.42 "Status is the lane's" · charter Status bullet · `Makefile` `team-status` |
| C5 | Board rotation precondition; anchor = item id | HANDOVER 09-06 (j): 3 of 4 `board.md:NNN` anchors off-surface; RV30 `:1589`→`:1594` drifted | **ENTERS** (rule + lint) | A lane can never clear its own rotation → orchestrator-only freeze, and the gate warns on the anchor class | rules §10.42 "Anchors, not line numbers" · charter bullet · `citation-gate.py` LIVE_ANCHOR |
| C6 | Index GENERATED, `done/` retired | its rules §10.40 — **generator not written in the field project** | **DOES NOT ENTER (deferred)** | Unmeasured mechanism that changes who writes status; §10.37 ground-before-build. Revisit when the field project's generator exists and has run | — |
| C7 | Epic layer (rule) | ADR-0013 · `rules §10.40`; E- items on board today: 0 (opening condition unmet) | **ENTERS** | Generic ("work that does not finish in one round"); the ADR's 5th clause (class-shaped = epic) folded in | rules §10.40 EPIC · charter EPIC PROPOSAL |
| D1 | `observer` agent template | `.claude/agents/observer.md` (`77e7907`, `8e8854f`) — the field project already split KIT CORE / field block | **ENTERS** | Compliance (auditor) ≠ critique (observer); the follow-up duty is what turned 30 evaluated-and-untracked recommendations into change | `.claude/agents/observer.md` · agents README · `docs/steering.md` section · `keel-audit` step 5 · team-create §1 note |
| D2 | `H:` premise label + EPIC PROPOSAL in charters | `b9bee55` team-*.md (`H:` landed; epic proposal relayed 09-06) | **ENTERS** | Two bullets in the skeleton; `H:` also in the orchestrator's ASSIGN text | `keel-agent-team-create` skeleton |
| D3 | `verifier` requirement vs sub-agent policy | `rules §10.41` | **ENTERS** (merged into C1) | Kit §4.11 said "an INDEPENDENT sub-agent" — unreachable where workers are denied sub-agents; routed review named as the alternative, sub-agent stays mandatory for the orchestrator's own changes | rules §10.41 TIER paragraph |
| D4 | Review charter: slice the owner round | B5 | **ENTERS** (merged into B5) | Kit has no review charter; the duty lives in the orchestrator's ROUTE step | `keel-continue` §3 ROUTE |
| E1 | Audit follow-up table | observer's second duty; 30 dispositions never tracked | **ENTERS** | An audit that produces findings but never measures change is noise | `keel-audit` step 0 + step 4 (`reports/<date>-audit.md`) · `auditor.md` check 7 |
| E2 | Auditor's own hit rate | observer: 2 refutations (2065→551 · `stats`) | **ENTERS** | A critic whose accuracy is never measured cannot be challenged | `keel-audit` step 4 · `auditor.md` check 7 |

## Not entering, and why (brief §3 agreed)
Tool catalogue/contract · ClickHouse guide · TR morphology rules · `honesty_guard` · `verified_answers` ·
counting discipline · the field project's teardown cases — all specific to the field project. The teardown PROCEDURE itself was already
in the kit (rules §10.39 revert-sensitivity order).

## Kit-side measurements this review rests on
- Kit test suite: 258 passed before → 265 passed after (`pytest tests/unit`; +3 team-addresses cells, +3 entry-budget cells, +3 citation-gate cells, −2 replaced attached-axis cells).
- `rules.md` 342 → 381 lines (cap 400, `.claude/keel-caps`); §10.38 re-quotes the measured count.
- Pre-delivery review (rules §4.11, `verifier` sub-agent): 3 refutations, all fixed before commit — the absence marker could hide a ghost still on disk (guard + test cell added) · §10.40's state chain and the charter skeleton said every delivery enters `## Review`, contradicting the tiers (qualified) · `test-fast` doubled pytest's `-q` and hid the pass count (dropped). Two minor wording gaps fixed in the same pass (ASSIGN trigger, `TASKS_ENTRY_CHARS` in the caps key list).
- Kit `Bash(*)` control: this session ran the whole review without one permission prompt.

## What the field project should do next (its own decision, via `/keel-update`)
Pull v0.8.36. Expected REVIEW hunks: `rules.md` (the field project's §10.40–42 already carry the Turkish originals of
these paragraphs — keep the field project's wording, take the kit's structure), `Makefile` (`team-clean` comment text
differs), `.pre-commit-config.yaml`. TOOLING lands whole: the two ported hooks are byte-identical to
The field project's except for corrected header docstrings; `observer.md`'s kit core is what the field project already has above
its marker line.
