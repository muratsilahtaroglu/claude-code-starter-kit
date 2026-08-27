---
name: keel-autopilot
description: Gated autonomy for one session — advance phases back-to-back with the full /keel-phase-review run at every gate, auto-commit at phase ends, batch pushes for ONE approval. Stops on gate FAIL, UNCERTAIN decisions, architecture surprises, or security-adjacent changes. Push is never automatic. Solo sessions or an agent team's orchestrator ONLY — never a worker/co-agent (it runs phase-review and commits, both forbidden to them by rules §10.42).
---

# /keel-autopilot — phases advance themselves; evidence gates don't move

When: the user explicitly turns it on ("/keel-autopilot", "autopilot", "work through the phases on your
own"). Autonomy is the USER's grant, never self-granted — and it changes WHO presses the button, not
WHAT the gates require.

**Who may run it: a SOLO session, or an agent team's ORCHESTRATOR — never a worker/co-agent.** This
mode runs `/keel-phase-review` (rule 2) and commits (rule 3), and §10.42 forbids a worker BOTH. So
check identity before the first step: the reground hook prints this session's agent from
`.claude/agent-team-sessions`; if it names a worker charter, say so and stop. Do NOT infer the answer
from `git config user.name` — same-machine agent sessions all share ONE git identity, which is exactly
why rule 4's ownership check cannot see this by itself.

Mode contract (4 rules):
1. **In-phase autonomy.** Work the wip phase's `TASKS ## Now` items back-to-back without pausing for
   confirmation; make routine judgment calls yourself (§10.36). Memory discipline stays hot-path:
   LESSONS the moment something is learned, TASKS updated as you go — autopilot without the rituals
   is just drift at higher speed. On a multi-user project, an `@`-assigned item still STARTS with the
   §10.41 spec briefing before the work (task-specific, self-explanatory questions; check the spec's
   Comprehension log first — an already-answered question is never re-asked).
2. **Gates stay evidence-based.** When `## Now` empties, run the FULL `/keel-phase-review` checklist
   yourself. PASS needs real evidence (tests green via `make test`, the gate's done-when observed) —
   never narrate a pass. PASS → flip the phase, seed the next `## Now` from PLAN.md, continue.
   FAIL → stop and report what's missing.
3. **Commit locally, batch the push.** Commit at each phase end (owner identity, §6.16); do NOT push.
   Accumulate the queue and present it at session end (or on request) for ONE approval.
   `settings.json`'s `ask` on push is the enforced backstop — never weaken it for this mode.
4. **Stop-and-ask triggers.** Halt and return to the user when: a gate FAILS · a decision is
   UNCERTAIN (verifier verdict or §10.37 grounding gap) · a scope/architecture surprise would need a
   new ADR · anything security-adjacent (secrets, auth, non-routine dependency changes) · a bulk
   output hits the `/keel-pilot` threshold (its human-routing rules override autopilot) · the same
   test is red twice after fixes · **the next `## Now` item or wip phase belongs to someone else** —
   autopilot NEVER does another's assigned work; stop and surface it (the parallel-work collision the
   ownership tag exists to prevent). Match ownership on the RIGHT key: on a human multi-user project
   that is `@owner` ≠ `git config user.name`; on a same-machine **agent team** every session shares one
   git identity, so compare the item's lane/`@tag` against this session's agent name from
   `.claude/agent-team-sessions` instead — the git check alone is inert there and silently passes.

Boundaries:
- **One session.** Cross-session automation (cron, /loop) is out of scope — re-request the mode each
  session, or make it a standing project agreement via a `LESSONS.md [rule]` line.
- **After any compaction, re-confirm.** The activation may live only in summarized-away conversation;
  ask one line ("autopilot still on?") before continuing autonomously. Note the activation in the next
  HANDOVER block (d) so the grant survives on disk.
- Never bypassed: push approval, `/keel-pilot` human routing, hook blocks, §0 bootstrap approvals,
  `/keel-distill`'s never-lossy-delete. The Stop hooks (`plan-phase-nudge`, handover reminder) keep
  firing — they are the net under the tightrope, not an annoyance to suppress.
