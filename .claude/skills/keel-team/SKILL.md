---
name: keel-team
description: OWNER-only setup wizard for a REAL human team (different people, different machines) — declare the owner (arm owner-guard), register members (@tags), seed lanes + author folders + the comprehension protocol, size the caps, pick the §6 contribution model + host wall. Packages the existing Multi-user playbook into one approved run; invents no new rules.
---

# /keel-team — set up the human team (owner-only)

When: helpers are joining a solo project — different PEOPLE on different MACHINES sharing a
repo/host. This wizard INSTALLS the existing Multi-user discipline (docs/steering.md "Multi-user",
rules §10.40–41, review-v2) in one approved pass — it invents nothing new. Same-machine AGENT
sessions are `/keel-agent-team-create`'s job; the two coexist: human lanes and agent lanes share one
TASKS board, and setup authority is the owner's in both.

## 0. Owner gate
- `.claude/project-owner` exists and `git config user.name` ≠ its content → **STOP** ("team setup is
  the owner's — ask @<owner>").
- Missing → this run DECLARES ownership: ask the owner's exact `git config user.name`, write the
  file (one line). State the **identity invariant** for everyone: repo-local
  `git config user.name "<tag>"`, single token, byte-for-byte the repo's `@tag` spelling — a
  mismatch silently unarms every ownership mechanism (the reground hook nags when unset).

## 1. Interview the owner
1. **Members** — each person's `@tag` (= their git user.name) + a one-line area/responsibility.
2. **Contribution model (§6.17 — host reality decides the wall):** same-repo branch→PR ·
   fork→PR (developers Read-only) · no-remote/local-only. Walk the HOST-wall table (steering
   "Multi-user") and say which wall actually ENFORCES here — on a free private PERSONAL repo there
   is NO real wall: either move to a free org (Read + fork PRs) or accept discipline-only and write
   that into the team doc.
3. **Caps** — propose `.claude/keel-caps` sized to headcount (5 people ≈ `HANDOVER=200` ·
   `HANDOVER_BLOCKS=4` · `LESSONS=400` · `TASKS=250` — field-tested values; the owner tunes). Pinned
   only on approval, never silently (§10.40).
4. **CI shape** (when PRs gate merges): §7.24 secret-less gating — a fork PR receives NO repo
   secrets, so live-cred/network tests must SKIP, never fail. If bootstrap pruned `.github/`, team
   scale-up is the moment the prune reverses — as a recorded ADR addendum.

## 2. Apply — each piece shown, approved, nothing silent
- `.claude/project-owner` (if new) — arms owner-guard: governance files + non-owner `main` pushes
  are blocked from then on.
- **TASKS:** `## Now` goes per-person (~2–3 items each), items carry `@owner` (+ `due:` for sprint
  targets); `## Review` is born at the first developer handover and follows review-v2 (file-first,
  four states, routing = orchestrator/owner).
- **`reports/team/<@tag>/`** folder per member + their `##` section in `reports/team/README.md`
  (the index-as-todolist; controlled status vocabulary per that template).
- **`.claude/keel-caps`** with the approved numbers.
- **Comprehension protocol:** the §10.41 gate already binds via rules; if the team wants the
  standalone one-pager (field pattern: a protocol sheet under `reports/team/`), seed it —
  task-specific self-explanatory questions, idempotent `## Comprehension log`, personally-run
  manual checks.
- **`docs/team.md`** (project-owned — the kit deliberately ships no template): roles table ·
  fork/clone + `git config` onboarding steps · secret handoff via a safe channel · ritual etiquette ·
  dev-local run knobs (own `.env` from `.env.example`, `make run PORT=…` overrides — "runs only on
  the owner's machine" is a bootstrap bug, §10.40).
- **rules.md §6** rewritten to the chosen contribution model, recorded as an ADR — with the §0a
  cascade: every doc that described the old flow gets updated in the same pass.
- **`docs/architecture.md`** (§1.6): register the team structure.

## 3. Hand off
Give the owner a per-member onboarding message to send: clone/fork → repo-local
`git config user.name "<tag>"` → `.env` from `.env.example` → `make test` green locally → work ONLY
your `@`-items → deliver per review-v2 (evidence FILE + `delivered` index line; a chat summary is
not a delivery). Remind the owner what stays theirs: assignment (TASKS `@tags`), review routing
(§10.41), governance edits — and the scaling valves when it hurts: per-user handovers at ≥~4
concurrent writers; LESSONS is never split per user (sign lines instead).
