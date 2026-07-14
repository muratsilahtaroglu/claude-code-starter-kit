---
name: keel-phase-review
description: End-of-phase gate — verify working product, tests, docs, ADRs, and handover before committing a phase.
---

# /keel-phase-review — end-of-phase checkpoint

Run at the end of a phase (rules.md §2). Report the checklist with pass/fail; fix gaps before proposing
a commit.

Checklist:
- [ ] **Working product** — the phase's feature runs; include a one-line "how to test this".
- [ ] **Tests** — relevant unit/integration (e2e if needed) written and run; results summarized under
  `tests/` + in HANDOVER.md (rules.md §2.8).
- [ ] **Architecture** — every structural change recorded in `docs/architecture.md` (rules.md §1.6).
- [ ] **PLAN.md (do not skip — this is what marks the phase `done`)** — the finished phase's gate
  flipped to `done` (+ next phase set `wip`, _Current focus_ updated, diagram regenerated from the
  table — see `/keel-plan`). The Stop hook `plan-phase-nudge` reminds you if you end a turn having cleared a
  `wip` phase's `## Now` without flipping it.
- [ ] **ADRs** — any significant decision captured as an ADR in `docs/adr/` (+ index row).
- [ ] **Docs** — CLAUDE.md / docs/user_manual.md updated if behavior/usage changed.
- [ ] **HANDOVER.md** — session block added (run `/keel-handover`); caps respected (else `/keel-distill`).
- [ ] **TASKS.md** — done items deleted (one-liners in HANDOVER (a)); `## Discovered` triaged.
- [ ] **LESSONS.md** — this phase's agreed rules/tests/gotchas written (rules §9.31).
- [ ] **Audit** — `/keel-audit` run over this phase's range (or consciously skipped with a reason); its
  approved fixes applied (rules.md §4.11).
- [ ] **Secrets** — `git diff --cached` reviewed; no `.env`/secrets staged (rules.md §6.18).
- [ ] **Deps** — if dependencies changed: lock refreshed + `pip-audit` clean (rules.md §7.23).

Then propose an approved commit + push (rules.md §6.15). Never push without user approval.
