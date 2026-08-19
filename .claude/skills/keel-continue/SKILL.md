---
name: keel-continue
description: Work out what this session should do NEXT and continue from it — resume half-done work, or pick up the lane's newly assigned task, or report that there is nothing to do and go idle. Cross-checks the auto-loaded memory against PLAN.md + git. Role-aware (worker vs orchestrator) and read-only, so any session type may run it.
---

# /keel-continue — decide what this session does next, then do it

When: at session start, after a compaction, after `--resume`, when a message from another session
wakes this one, or any time "what should I be doing?" needs an ACTIVE answer. The SessionStart hook
only REMINDS you what to re-read; this skill does the reading, cross-checks it against reality (git),
and ends in exactly one of three verdicts.

(Renamed from `/keel-start` in v0.8.28: it answers more than "how do I start" — resuming, taking new
work, and going idle are the same decision, taken from the same evidence.)

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
- Agent-team session (the reground hook injected "this session is @<agent>"): scope the brief to
  that agent's `### <agent>` lane and charter paths; re-adopt the identity silently
  (see `/keel-agent-team-start` — do not re-run it when the hook already named you).

## 2. Cross-check — the 60-second drift pass
- HANDOVER top block vs `git log`: do its (c)/(d) lines still describe HEAD? A block that predates
  the last ~10 commits is suspect — flag it as stale in the brief instead of trusting it (§1.4).
- TASKS `## Now` vs `git status`: which open item owns the uncommitted files? That item is the
  resume point — name its next micro-step from the actual diff, not from memory.
- Fold in whatever the SessionStart hook already flagged (caps, overdue `due:`, Review queue,
  missing evidence files, stale Discovered) — don't re-derive it, don't drop it.

## 3. Decide — exactly one of three verdicts

Take them in order; the FIRST that matches wins.

1. **RESUME** — uncommitted work, or an open `## Now` item that is yours and already started.
   Continue it. Name the next micro-step from the actual diff, not from memory.
2. **TAKE** — nothing in flight, but your lane has an assigned, unblocked item. Do NOT open the
   editor: go to the §10.41 **comprehension gate** first — read the spec's `## Comprehension log`
   (an answered question is never re-asked), then brief the task and answer 2–3 questions that are
   specific to THIS task's done-when. Work starts after that, not before.
3. **IDLE** — nothing in flight and nothing assigned. Say so plainly and STOP. Do not invent work,
   do not poll in a loop, do not sleep: on an agent team the orchestrator wakes this session with a
   message when there is something to do, and that wake re-runs SessionStart, so the identity and
   memory come back from disk on their own (measured 2026-08-19 —
   docs/steering.md "Agent teams: how a waiting agent gets woken"). Idle is a legitimate end state.

### If this session is the ORCHESTRATOR
The verdicts differ, because the orchestrator takes no work items of its own (§10.42):
1. **SYNC** — any `reports/team/*/board.md` newer than `TASKS.md` (the reground hook counts them):
   read the boards, then write the shared files — statuses and `## Review` moves into TASKS,
   findings into LESSONS with `@<name>` attribution, index lines into `reports/team/README.md`.
2. **ROUTE** — anything sitting in `## Review`: routing is yours alone (a deliverer never picks its
   own reviewer). Delegate the mechanical half to the `verifier` subagent; keep the owner's list to
   what only a human can do.
3. **ASSIGN** — a lane is free and `## Next` has work for it: allocate the next id in that lane's
   series (§9.32) and tell the worker.
   **Before calling a lane "free", check the MAPPING, not `/list-agents` names** (field case
   2026-08-19): `.claude/agent-team-sessions`' date column is a last-seen heartbeat, touched by the
   reground hook on every resolve — grep the lane's agent there. A line dated within ~2 days means
   a session is quietly alive; `/list-agents` failing to show a reachable name for it is an
   ADDRESSING problem (the client-side display name reset — e.g. a VS Code restart — while the
   session and its identity mapping stayed intact), not proof the worker died. Message the lane's
   last-known name first; only treat the lane as truly free once the heartbeat itself has gone
   stale. Never assign the SAME lane to a second freshly-adopted session while its heartbeat is
   recent — that is the double-ownership risk the start skill's double-claim guard exists for.
4. **IDLE** — none of the above. Report the board state in one line and stop; a worker's delivery
   message will wake this session.

## 4. Brief, then act
Reply with a four-part brief, one screen max:
1. **Where you left off** — wip phase + one-line status.
2. **In-flight** — the half-done `## Now` item: what's already done on it, the next micro-step.
3. **Warnings** — only what changes today's plan (test status, overdue items, Review queue waiting,
   cap overflows, stale handover). Nothing to warn = say "none".
4. **Next step** — the verdict from §3 and ONE concrete action; then start it. On IDLE,
   the next step is "waiting for an assignment" — that is a complete answer, not a failure.

Resuming a half-done item continues directly; STARTING NEW work first verifies tests pass
(CLAUDE.md session protocol). If the memory files contradict each other or git, surface the
conflict in the brief and ask which wins (§10.36) — never silently pick a side.

Boundaries: writes nothing (blocks/board/lessons are `/keel-handover`'s and `/keel-distill`'s job) ·
never auto-picks a foreign-owned item · never flips PLAN statuses (that's `/keel-phase-review`).
