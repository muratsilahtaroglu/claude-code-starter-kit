#!/usr/bin/env bash
# Multi-event telemetry hook — appends one line per interesting event to `.claude/ritual-log`
# (git-ignored, machine-local): skills invoked via the Skill tool, compact boundaries (manual/auto),
# session starts. Answers "which skills/hooks ran, how often, in which compact interval" — grep the
# file; compact/session lines are the interval boundaries. The blocking hooks (block-dangerous,
# compact-gate) also append their BLOCK events here. Self-trims to the last 1000 lines once per
# session. Always exits 0 — telemetry must never break work (every write is best-effort).
# One script, three registrations: PreToolUse(matcher Skill) + PreCompact + SessionStart.
#
# TWO CONTRACTS THIS FILE KEEPS (both learned the hard way, 2026-08-19):
#  1. Telemetry is written ONLY when CLAUDE_PROJECT_DIR is set. Claude Code exports it to every
#     hook, so a real invocation always has it; an ad-hoc probe piping a payload by hand does not.
#     Defaulting to $(pwd) let test runs write into the LIVE log — the duplicate-line detector then
#     cried "hooks are double-firing, uninstall your plugin" for two days over a plugin that was
#     not installed. Measurement must never contaminate the thing it measures.
#  2. Every line carries the writing session's @agent when one is adopted, resolved from
#     .claude/agent-team-sessions (session_id -> agent, the same map the reground hook reads).
#     Without it an agent team's sessions all write to one log with no attribution: "which agent
#     compacted?" and "whose skill call was that?" become unanswerable exactly when a team makes
#     them matter. Absent map or unadopted session -> no tag, never a failure.
set -u
DIR="${CLAUDE_PROJECT_DIR:-}"
[ -n "$DIR" ] || exit 0
LOG="$DIR/.claude/ritual-log"
payload="$(cat 2>/dev/null || true)"

agent_tag() { # -> "@name " when this session adopted an agent identity, else ""
  sid="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')"
  [ -n "$sid" ] || return 0
  [ -f "$DIR/.claude/agent-team-sessions" ] || return 0
  ag="$(grep -m1 "^${sid} " "$DIR/.claude/agent-team-sessions" 2>/dev/null | awk '{print $2}')"
  [ -n "$ag" ] && printf '@%s ' "$ag"
  return 0
}
get() { printf '%s' "$payload" | python3 -c "import sys,json;d=json.load(sys.stdin);print($1)" 2>/dev/null || true; }

ev="$(get "d.get('hook_event_name','')")"
case "$ev" in
  PreToolUse)   line="skill $(get "d.get('tool_input',{}).get('skill','?')")" ;;
  UserPromptExpansion)
                # user-TYPED commands, built-ins included (/compact, /code-review, /keel-*) —
                # the gap the Skill-tool matcher can't see (it only fires on agent-side calls)
                line="command $(get "d.get('command_name', d.get('command','?'))")" ;;
  PreCompact)   line="compact $(get "d.get('trigger','?')")" ;;
  SessionStart) line="session-start $(get "d.get('source','?')")"
                # trim once per session — keep the last 1000 lines
                if [ -f "$LOG" ]; then tail -n 1000 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG" 2>/dev/null; fi ;;
  *)            line="event ${ev:-unknown}" ;;
esac

mkdir -p "$DIR/.claude" 2>/dev/null || exit 0
printf '%s %s%s\n' "$(date '+%F %T')" "$(agent_tag)" "$line" >> "$LOG" 2>/dev/null || true
exit 0
