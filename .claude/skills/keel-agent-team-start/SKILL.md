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

## 2b. Name the session after the agent — this is the messaging ADDRESS

Ask the owner to run **`/rename <name>`** in this chat (or relaunch it with `claude --name <name>`).

This is not cosmetic. The orchestrator wakes a worker with `SendMessage`, and its `to:` is the
SESSION name that `/list-agents` shows — not the keel agent name. A session nobody renamed is named
after the working directory, so a five-agent team reads as `my-app-3f`, `my-app-a1`, `my-app-7c`…
mutually indistinguishable: the orchestrator cannot address a worker, and the star-topology wall
cannot recognise a target as a teammate (it allows what it cannot identify, by design).

With the rename done, `to: "<name>"` reaches this session, the wall recognises the roster, and the
`@<name>` tag on every `.claude/ritual-log` line lines up with the address people actually use.

**Re-run this after every client restart, even when the identity re-adopted silently.** Field case
2026-08-19: a VS Code restart left the session id AND `.claude/agent-team-sessions` mapping exactly
intact — the reground hook re-injected "@frontend" correctly — but `/list-agents` started showing
this window under its directory-derived name again. The orchestrator read "name unreachable" as
"session dead" and broadcast a needless re-identify. The mapping (identity) and the display name
(addressing) are two different layers, and only one of them survives a client restart. `/rename
<name>` is idempotent and cheap — run it any time addressing might have reset, not only once.

**Make it automatic — install the launch wrapper once per machine (recommended).** Measured
2026-09-03: `/rename` IS written to the session transcript (an `agent-name` record), but a process
started with `--resume` does not copy it into the messaging record — it comes up
`nameSource=derived`. So "I forgot to rename" is structural, not a lapse. `claude --name <agent>`
at launch is the documented flag for that record, and the VS Code extension lets a script front the binary:

    cp .claude/claude-launch-wrapper.sh ~/.claude/ && chmod +x ~/.claude/claude-launch-wrapper.sh
    # VS Code settings on the machine that RUNS claude (remote host, if Remote-SSH):
    #   "claudeCode.claudeProcessWrapper": "/home/<you>/.claude/claude-launch-wrapper.sh"

From then on every `--resume` launch is named from `.claude/agent-team-sessions` (this step's
mapping) — or, on any project without a map, from the transcript's own last rename. **Verify
once after installing** — and do it with the trace, because the `exec` is transparent and the process
cmdline looks identical either way: `touch ~/.claude/keel-launch-wrapper.log`, reload the IDE window
(the setting is read when the extension host starts), reopen one agent tab, then read the log — a
`named --name=<agent>` line means it fired. `python3 .claude/team-addresses.py` should then show that
lane OK. Delete the log file to disarm; the wrapper never creates it. New sessions
pass through untouched; the wrapper never writes to stdout and fails open to the original launch.
The `team-addresses.py --hook` SessionStart line stays as the safety net: it tells THIS window,
by name, when its address and identity have diverged.

**Two machines, two VS Code builds = twins.** If the owner works one remote host from two clients
on DIFFERENT VS Code versions, two VS Code servers stay alive and each resumes the same session
ids — every identity shows 2–3 live windows. The SessionStart line marks which twin is ATTACHED
(its server has a client) and which is DETACHED, with the `kill` command for the detached pids;
the durable fix is version parity between the two clients (see steering "Addressing").

## 3. Adopt the charter
Read `.claude/agents/team-<name>.md` and take it as this session's standing orders: mission, scope
paths, lane, author folder, review routing, and — for workers — the FORBIDDEN list (no WRITE-rituals,
no commit/push, no touching others' lines; rules §10.42). The `Role: orchestrator` charter instead
assumes the duties: rituals, lane/@tag assignment, review routing (§10.41), memory curation — and no
work items of its own.

## 4. Resume in-lane (write-surface split, §10.42)
Refresh your board's lane MIRROR from TASKS.md (read-only), then run the `/keel-continue` flow scoped
to it: brief "where the lane left off · in-flight item · warnings · next step", then work ONLY your
items. Everything you write mid-work goes to YOUR surfaces — `reports/team/<name>/board.md`
(progress · findings inbox the moment something is learned · requests) and your spec/fix files —
NEVER to TASKS/LESSONS/HANDOVER/the index: the orchestrator syncs your board into them.
Out-of-scope discoveries: one line in your board's requests section — never fixed by you.

After a compaction/`--resume` the reground hook re-injects the identity from the mapping file —
re-adopt silently; do NOT re-run this skill unless the hook says the session has no identity.
