---
name: keel-tidy
description: Layout-hygiene ritual — sweep stray/obsolete files (loose root scripts, dead code, logs, stale scratch), attach EVIDENCE to each (git age, references, test collection), then triage with approval — module-ize · delete (git is the archive) · scratch/archive/ · gitignore the class. Never touches memory files or the reports/ evidence trail.
---

# /keel-tidy — the §3.10 sweep: no file left unanswered

When: layout drift is felt (loose files at the repo root, stray one-off scripts, logs/caches in the
tree, `scratch/` overflowing), at a phase boundary, or every ~5 sessions as hygiene. This is the
ritual arm of rules.md §3.10 — "no file of unclear purpose is left in the main source tree". It is
NOT `/keel-distill`'s job: distill curates the MEMORY files (§9 caps), tidy curates the FILE TREE
(§3 layout) — different axis, different risk, and a file sweep bolted onto a cap rotation would
derail both.

## 1. Sweep — collect candidates deterministically
- **Repo-root files outside the discipline scaffold** (CLAUDE.md · rules.md · HANDOVER/LESSONS/TASKS/
  PLAN · README/LICENSE/CONTRIBUTING · Makefile/pyproject/lockfiles · dotfiles) — §3.10: the root
  holds scaffold only; application code lives under `src/`.
- **Runtime junk anywhere:** `*.log` · `*.tmp` · `__pycache__/` · `.pytest_cache/` · editor swap
  files · stray outputs sitting outside `reports/`.
- **`scratch/` items** untouched for weeks (`git log -1 --format=%cs -- <f>`) or missing their 1-line
  purpose comment.
- **Source files nothing references:** not imported (grep the module name across `src/` + `tests/`),
  absent from Makefile/CI, not collected by the test runner, no `docs/architecture.md` row.

**Off-limits (other jurisdictions):** memory files + `docs/adr/` (distill / the owner) · `reports/`
(the §2.8 evidence trail — prune only on an explicit ask) · `research/` findings (§8.30) ·
`tests/fixtures/` golden sets (§10.39) · paths already git-ignored.

## 2. Evidence per candidate — never vibes
One line each: last git touch · referenced-by (imports / Makefile / CI / docs) · test-collected? ·
tracked or untracked. A test that LOOKS dead may be a regression fixture guarding a fixed bug —
check `tests/fixtures/` and the tests-folder README why-lines before calling anything obsolete.

## 3. Triage table → user approval (nothing moves without it)
- **Belongs in the tree** → move under `src/`/`tests/` + an `architecture.md` row (§1.6).
- **Obsolete + TRACKED** → **DELETE** — git history IS the archive; moving a dead tracked file into an
  "archive" folder relocates clutter instead of removing it.
- **Unsure / maybe-later / UNTRACKED experiment** → `scratch/archive/<topic>/` with a 1-line purpose
  header (the §3.10 triad's middle door).
- **Runtime junk** → delete AND add the PATTERN to `.gitignore` so the class never returns (§10.39:
  fix the class, not the instance).
Present ONE table — file · evidence · verdict · action — apply only approved rows, never silently.

## 4. Cascade + verify + record
- Cascade every move/delete: grep the old path across `*.md` (README, docs/, folder READMEs),
  Makefile, CI — update or remove every reference (§0a cascade discipline).
- `make test` after moves (imports break silently); hooks/CI still green.
- Record: HANDOVER (a) one-liner (`keel-tidy: N moved · M deleted · K ignored`), `architecture.md`
  rows for moves, and a LESSONS `[rule]`/`[gotcha]` line when a junk class earned a `.gitignore`
  pattern. Commit with approval (§1.3).
