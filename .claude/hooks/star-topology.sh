#!/usr/bin/env bash
# PreToolUse(SendMessage) hook — keeps an agent team a STAR, not a mesh (rules.md §10.42).
#
# WHY. Everything is coordinated from one centre: the orchestrator assigns, workers deliver back to
# it, and no worker talks to another worker. Left to prose this erodes — two workers "just checking
# something" with each other produces decisions nobody wrote down, in a repo whose whole memory model
# assumes the orchestrator is the single writer of the shared files. This hook makes the topology a
# property of the machine instead of a rule people remember.
#
# WHY A HOOK AND NOT A PERMISSION RULE. Permission rules take the BARE tool name with no specifier,
# so `deny: SendMessage` would also cut the worker→orchestrator path the design depends on. Only a
# hook can decide by TARGET.
#
# ADDRESSING. `to` is the peer's SESSION name (what /list-agents shows), not automatically the keel
# agent name: unnamed sessions are named after the working directory, so a whole team reads as
# `my-app-3f`, `my-app-a1`… indistinguishable. `/keel-agent-team-start` therefore has each session
# run `/rename <agent>` so the session name IS the agent name. Where that has not been done, the
# target simply won't match a roster entry and this hook allows the send — it never guesses.
#
# SCOPE. Blocks exactly one thing: a worker addressing another WORKER on this project's roster.
# Everything else is allowed — the orchestrator to anyone, anyone to the orchestrator, a session
# with no adopted identity (solo projects pay nothing), a target outside the roster (an unrelated
# session), and "main" or a subagent name (a worker's own delegation must keep working).
#
# Contract: tool call as JSON on stdin; exit 2 = BLOCK, exit 0 = allow. Fails OPEN throughout — a
# broken guard must not brick a session (same trade-off the other guards document).
set -u
DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# No roster → no team → nothing to enforce.
ls "$DIR"/.claude/agents/team-*.md >/dev/null 2>&1 || exit 0
[ -f "$DIR/.claude/agent-team-sessions" ] || exit 0

payload="$(cat 2>/dev/null || true)"
field() { printf '%s' "$payload" | python3 -c "import sys, json
print(json.load(sys.stdin)$1)" 2>/dev/null || true; }

[ "$(field '.get("tool_name", "")')" = "SendMessage" ] || exit 0

# WHO AM I — the same session_id → agent map the reground hook re-injects identity from.
sid="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
[ -n "$sid" ] || exit 0
me="$(grep -m1 "^${sid} " "$DIR/.claude/agent-team-sessions" 2>/dev/null | awk '{print $2}')"
[ -n "$me" ] || exit 0                      # unadopted session: not a team member, not our business
[ -f "$DIR/.claude/agents/team-${me}.md" ] || exit 0

# The orchestrator is the hub: it may address anyone.
grep -q '^Role: orchestrator' "$DIR/.claude/agents/team-${me}.md" 2>/dev/null && exit 0

# WHO AM I WRITING TO — strip the optional " [ref]" disambiguator SendMessage accepts.
to="$(field '.get("tool_input", {}).get("to", "")')"
to="$(printf '%s' "$to" | sed -E 's/[[:space:]]*\[[^]]*\][[:space:]]*$//; s/^[[:space:]]+//; s/[[:space:]]+$//')"
[ -n "$to" ] || exit 0

# Not a roster member → not a teammate → allowed (subagents, "main", unrelated sessions).
[ -f "$DIR/.claude/agents/team-${to}.md" ] || exit 0
# Addressing the orchestrator is the one path a worker always has.
grep -q '^Role: orchestrator' "$DIR/.claude/agents/team-${to}.md" 2>/dev/null && exit 0

orch="$(grep -l '^Role: orchestrator' "$DIR"/.claude/agents/team-*.md 2>/dev/null \
        | head -1 | sed 's/.*team-//; s/\.md$//')"
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && \
  echo "$(date '+%F %T') @${me} star-topology BLOCK: -> @${to}" >> "$DIR/.claude/ritual-log" 2>/dev/null || true
echo "BLOCKED by .claude/hooks/star-topology.sh: @${me} may not message @${to} directly — an agent team is a STAR, and every decision goes through the centre (rules.md §10.42). Send it to @${orch:-the orchestrator} instead, which assigns, routes reviews and is the single writer of the shared memory files; a worker-to-worker agreement is a decision no shared file records. If @${to} genuinely needs this, say so in your message to @${orch:-the orchestrator} and let it relay or re-assign." >&2
exit 2
