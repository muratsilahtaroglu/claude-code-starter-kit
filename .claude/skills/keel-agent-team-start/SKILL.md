---
name: keel-agent-team-start
description: Adopt an agent-team identity for THIS chat (run once per new chat) — load the charter, record the session→agent mapping so the reground hook re-injects the identity from disk after every compaction/--resume, then resume from the agent's lane.
---

# /keel-agent-team-start @<name> — who am I in this chat

When: the FIRST message of a newly-opened session that should act as one of the project's team
agents (`/keel-agent-team-start @mechanic`), or to SWITCH an existing chat's identity. The roster is
`.claude/agents/team-*.md` (created owner-approved by `/keel-agent-team-create`) — if no charters
exist, say so and stop; NEVER invent one (charter creation is the owner's, §10.42).

## 1. Resolve the agent
- Argument given (`@<name>` or `<name>`): match against `team-<name>.md`. No match → list the roster
  once, ask.
- No argument: if the reground hook already injected "this session is @X" into this context, confirm
  and jump to step 3 (idempotent — a known identity is never re-asked); otherwise ask ONCE with the roster.

## 2. Record the mapping — this is what survives compaction
- **Session id:** take it from the reground hook's `Session-id: <id>` line in this context (the hook
  prints it whenever team charters exist). If it is genuinely absent, adopt the identity for this
  context anyway and WARN: "mapping not recorded — identity may need re-adopting after the next compact".
- Append to `.claude/agent-team-sessions` (git-ignored, machine-local):
  `<session_id> <name> <YYYY-MM-DD>`. If THIS session id already has a line, REPLACE that line
  (identity switch). Keep the file ≤ ~50 lines — drop the oldest.
- **Double-claim guard:** if ANOTHER session id maps to the same agent with a recent date (≤ ~2
  days), warn — "@<name> also looks active in another chat: takeover, or a collision about to
  happen?" — and proceed only on the owner's word (two chats writing one lane = the §10.42 clobber).

## 3. Adopt the charter
Read `.claude/agents/team-<name>.md` and take it as this session's standing orders: mission, scope
paths, lane, author folder, review routing, and — for workers — the FORBIDDEN list (no WRITE-rituals,
no commit/push, no touching others' lines; rules §10.42). The `Role: orchestrator` charter instead
assumes the duties: rituals, lane/@tag assignment, review routing (§10.41), memory curation — and no
work items of its own.

## 4. Resume in-lane
Run the `/keel-start` flow scoped to the lane: brief "where the lane left off · in-flight item ·
warnings · next step", then work ONLY lane/@<name> items. Out-of-scope discoveries get one line in
`## Discovered` (or go to the orchestrator) — never fixed by you.

After a compaction/`--resume` the reground hook re-injects the identity from the mapping file —
re-adopt silently; do NOT re-run this skill unless the hook says the session has no identity.
