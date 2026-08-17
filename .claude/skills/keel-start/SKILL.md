---
name: keel-start
description: Actively resume after a compact, --resume, or cold start — cross-check the auto-loaded memory against PLAN.md + git, deliver a "where you left off · in-flight · warnings · next step" brief, then continue from it. Read-only, so any session type may run it.
---

# /keel-start — pick up exactly where the project left off

When: at session start, after a compaction, or after `--resume` — whenever "what was I doing?" needs
an ACTIVE answer. The SessionStart hook only REMINDS you what to re-read; this skill actually does
the reading, cross-checks it against reality (git), and hands back a resume brief before work continues.

**Read-only by design** — it writes no file, so EVERY session type may run it: owner, developer,
co-agent (rules §10.42 walls co-agents off the WRITE rituals; this isn't one).

## 1. Gather — cheap, no double-reads
`CLAUDE.md` `@`-imports HANDOVER.md · LESSONS.md · TASKS.md · rules.md, re-injected from disk after
every compaction — they are ALREADY in context: do not re-Read them wholesale. Exception: if
`git status` shows one of them MODIFIED (this session's earlier writes, or a parallel co-agent's —
§10.42), re-Read that file: the imported copy predates the edit. Then read only what is NOT auto-loaded:
- `PLAN.md` — the wip phase, its gate, _Current focus_ (skip if the project doesn't use PLAN).
- `git log --oneline -10` + `git status` — what actually landed vs. what is in flight; uncommitted
  edits are the surest marker of a half-finished item.
- Multi-user (`.claude/project-owner` exists): note `git config user.name` — the brief scopes to
  YOUR `@tag` items; foreign-owned work is surfaced, never picked up (TASKS ownership).

## 2. Cross-check — the 60-second drift pass
- HANDOVER top block vs `git log`: do its (c)/(d) lines still describe HEAD? A block that predates
  the last ~10 commits is suspect — flag it as stale in the brief instead of trusting it (§1.4).
- TASKS `## Now` vs `git status`: which open item owns the uncommitted files? That item is the
  resume point — name its next micro-step from the actual diff, not from memory.
- Fold in whatever the SessionStart hook already flagged (caps, overdue `due:`, Review queue,
  missing evidence files, stale Discovered) — don't re-derive it, don't drop it.

## 3. Brief, then continue
Reply with a four-part brief, one screen max:
1. **Where you left off** — wip phase + one-line status.
2. **In-flight** — the half-done `## Now` item: what's already done on it, the next micro-step.
3. **Warnings** — only what changes today's plan (test status, overdue items, Review queue waiting,
   cap overflows, stale handover). Nothing to warn = say "none".
4. **Next step** — ONE concrete action; then start it.

Resuming a half-done item continues directly; STARTING NEW work first verifies tests pass
(CLAUDE.md session protocol). If the memory files contradict each other or git, surface the
conflict in the brief and ask which wins (§10.36) — never silently pick a side.

Boundaries: writes nothing (blocks/board/lessons are `/keel-handover`'s and `/keel-distill`'s job) ·
never auto-picks a foreign-owned item · never flips PLAN statuses (that's `/keel-phase-review`).
