# Agent teams — how a waiting agent gets woken, measured

_2026-08-19 · live experiment on this machine + the vendor documentation it was checked against.
Question behind it: an agent blocked on another should park, not die — and the owner asked whether
that is a "waiting mode", a "manual mode", or an "auto mode" in the literature._

## Headline

| | |
|---|---|
| Proposed mechanism (sleep + poll) | **rejected** — it is the pattern the field moved away from, and Claude Code already ships the event-driven version |
| Mechanism adopted | message wakes an idle peer session |
| Wake latency, measured | **seconds** (sent 10:18:5x, received 10:19:13) |
| Does a wake restore identity? | **yes** — it fires `SessionStart`, so the reground hook re-injects from disk |
| Star topology enforceable? | **yes, by hook** — not by permission rule |
| Claude Code's own agent teams | present in the product, **not usable here**: v2.1.87 installed vs v2.1.178+ documented, flag unset |

## The names the field already has

- **attended / unattended / hybrid** — RPA's terms for the mode axis the owner described as "manual
  control mode vs auto mode". Attended means a human starts it; unattended means a schedule or event
  does; hybrid runs unattended and escalates on anything outside the rules. Agent frameworks call the
  same axis human-in-the-loop vs autonomous.
- **idle** — the state of a session with nothing to do.
- **supervisor pattern** — one lead delegating to specialised workers that report only to the lead.

The 2026 consensus in multi-agent orchestration is explicit that idle workers should be **activated
by events, not poll**, because polling burns compute for nothing. Claude Code's design agrees: its
teammates emit an idle notification and the lead "doesn't need to poll for updates".

## The experiment

A message was sent from this session to `claude-code-starter-kit-a3`, a peer session that had been
idle for a day. Its reply, verbatim:

> "State on arrival: **IDLE** — no user turn in progress, no tool running. Your message is what woke
> this session; it arrived as the first turn of a fresh context (SessionStart hook fired in the same
> turn). Received at 2026-08-19T10:19:13+00:00."

Three things follow, and all three matter more than the wake itself:

1. **An idle session is reachable.** It does not have to be watching anything.
2. **The wake fires `SessionStart`.** So the reground hook re-injects the agent identity from
   `.claude/agent-team-sessions`, and CLAUDE.md's `@`-imports reload from disk. A woken worker
   rebuilds itself before it acts — no sleep loop needs to preserve anything.
3. **The wake is not free.** The peer noted it triggered a full session start, and the vendor docs
   confirm a message to an idle session re-sends that session's whole context. Hence the deliberately
   terse message protocol: a message is a pointer, not a payload.

## What could not be tested, and what that changed

```
claude --version                    2.1.87
cross-session messaging             docs say v2.1.224+ … but WORKS here (tested above)
agent teams / TeammateIdle          docs say v2.1.178+
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS unset
~/.claude/teams · ~/.claude/tasks   absent
```

An earlier draft of this design put Claude Code's `TeammateIdle` hook at the centre — "exit 2 to keep
the teammate working" is a precise fit for the requirement. **It was withdrawn**: it cannot be
exercised on this machine, and building a mechanism on an unverified one is the failure mode rules
§10.37 exists to prevent. The base is the channel that was actually measured; the built-in feature is
documented as an optional accelerator.

Keel is not made redundant by the built-in feature either. Its documented limitation —
*"`/resume` and `/rewind` do not restore in-process teammates"* — is exactly what Keel's session map
plus reground hook solve, and its shared task list lives in `~/.claude/tasks/`, local and never
uploaded, where the owner's review chain cannot see it. Runtime coordination and durable governance
are different jobs.

## The star, and why a permission rule cannot express it

Requirement: workers never talk to each other; everything goes through the orchestrator. Not for
tidiness — the shared memory files have exactly one writer, so a decision two workers reach between
themselves is a decision no shared file records.

Permission rules take the **bare tool name with no specifier**, so `deny: SendMessage` would also cut
the worker→orchestrator path the design depends on. A `PreToolUse` hook can decide by target, so the
wall is `.claude/hooks/star-topology.sh`.

Verified live, both directions, with a temporary roster in this repo:

```
@tmpworker → @tmppeer   BLOCKED by star-topology.sh  (with the message naming @tmporch instead)
@tmpworker → @tmporch   allowed by the hook; delivery then failed only because no session
                        answers to that name — the wall let it through
```

The block was recorded as `2026-08-19 12:27:34 @tmpworker star-topology BLOCK: -> @tmppeer`, which
also confirmed the same day's ritual-log attribution work on a real invocation.

## Addressing — the detail that makes or breaks it

`SendMessage`'s `to:` is the peer's **session name** from `/list-agents`, not the keel agent name. An
unnamed session is named after its working directory: a live seven-session team in one repo listed as
`alice-v2-01`, `alice-v2-91`, `alice-v2-7a`… mutually indistinguishable. The orchestrator could not
address a worker, and the star wall could not recognise a target as a teammate.

So `/keel-agent-team-start` now has each chat run `/rename <agent>`. After that the agent name is the
address, the wall recognises the roster, and the `@<agent>` tag on every ritual-log line matches the
name people actually type.

## Consequences accepted

- **A closed chat cannot be woken** — `/list-agents` lists live sessions only. Keeping the team's
  chats open is an operating requirement.
- **No polling anywhere.** `/keel-continue` ends in IDLE and stops; the next assignment wakes it.
- **Message loops are already bounded** by the platform (repeat throttling, identical-repeat drops,
  a 50-message cap per session), and the star wall removes worker↔worker loops by construction.
