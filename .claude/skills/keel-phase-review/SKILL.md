---
name: keel-phase-review
description: End-of-phase gate — verify working product, tests, docs, ADRs, and handover before committing a phase.
---

# /keel-phase-review — end-of-phase checkpoint

Run at the end of a phase (rules.md §2). Report the checklist with pass/fail; fix gaps before proposing
a commit.

Checklist:
- [ ] **Working product** — the phase's feature runs; include a one-line "how to test this" **for the
  user**. What only a human can verify (browser/UX, prod host, real creds) is handed off as a recipe
  and tracked in HANDOVER (d) — never silently assumed passed.
- [ ] **Tests** — relevant unit/integration (e2e if needed) written and run via `make test` (auto-log →
  `reports/tests/<date>/`); the phase's **committed summary** written to `reports/tests/<date>-phase<N>.md`
  (suites, counts, what was verified, and **measured durations**: suite runtime + the gate's key step
  timings — WHAT to time is project-specific (E2E latency, first token, query ms, batch throughput, …) —
  side-by-side with the previous phase's numbers so slowdowns surface at the gate, not in production);
  new test/fixture files one-lined in their folder README; one-line
  summary in HANDOVER.md (rules.md §2.8); bulk outputs passed the `/keel-pilot` gates where applicable.
  Ad-hoc reports (speed tests, golden proofs) complement `reports/tests/<date>-phase<N>.md` — never replace it.
- [ ] **Architecture** — every structural change recorded in `docs/architecture.md`: new/changed module
  rows AND the component overview resynced with them (the module table is the source of truth — a stale
  top diagram fails this item, same contract as PLAN.md's table → diagram; rules.md §1.6).
- [ ] **PLAN.md (do not skip — this is what marks the phase `done`)** — the finished phase's gate
  flipped to `done` (+ next phase set `wip`, _Current focus_ updated, diagram regenerated from the
  table — see `/keel-plan`). The Stop hook `plan-phase-nudge` reminds you if you end a turn having cleared a
  `wip` phase's `## Now` without flipping it.
- [ ] **ADRs** — any significant decision captured as an ADR in `docs/adr/` (+ index row).
- [ ] **Docs** — CLAUDE.md / docs/user_manual.md updated, **or the review states why nothing user-facing
  changed**. A still-template `user_manual.md` while shipped phases have user-facing behavior = FAIL
  (the SessionStart hook warns on this too — silence is not a pass).
- [ ] **HANDOVER.md** — session block added (run `/keel-handover`); caps respected (else `/keel-distill`).
- [ ] **TASKS.md** — done items deleted (one-liners in HANDOVER (a)); `## Discovered` triaged.
- [ ] **LESSONS.md** — this phase's agreed rules/tests/gotchas written (rules §9.31).
- [ ] **Audit** — `/keel-audit` run over this phase's range **via the skill — it writes `.claude/last-audit`;
  an inline audit that skips the marker leaves the audit-due nudge firing forever** (or consciously
  skipped with a reason); its approved fixes applied (rules.md §4.11).
- [ ] **Code review** — `/code-review` (or the project's review flow) run over this phase's diff;
  each finding triaged **through the `verifier` subagent** (adversarial "try to refute") before any
  fix is applied: CONFIRMED → fix now · REFUTED → record with its counter-evidence · UNCERTAIN → ask
  the user (default: don't fix). Reviewer output is a claim, not a verdict (rules.md §4.11); deferred
  items get one line each in `TASKS.md ## Discovered`. The phase gate is the review boundary —
  cheaper than reviewing every session, earlier than reviewing at release.
- [ ] **Secrets** — `git diff --cached` reviewed; no `.env`/secrets staged (rules.md §6.18).
- [ ] **Deps** — if dependencies changed: lock refreshed + `pip-audit` clean (rules.md §7.23).

Then propose an approved commit + push (rules.md §6.15). Never push without user approval.
