#!/usr/bin/env bash
# claude-launch-wrapper.sh — gives a RESUMED session its agent name back, automatically.
#
# THE GAP IT CLOSES (measured 2026-09-03 on a live 5-agent team, not inferred):
#   `/rename <agent>` writes an `agent-name` record into the session TRANSCRIPT — but the messaging
#   address peers see (`/list-agents`, `SendMessage to:`) is the per-PROCESS record in
#   `~/.claude/sessions/<pid>.json`, and a process started with `--resume <sid>` does NOT copy the
#   transcript's name into it: it comes up `nameSource=derived` as `<repo>-xx`. Every IDE reopen,
#   Remote-SSH reconnect or `--resume` therefore silently un-names the session, and the orchestrator
#   loses the address until a human remembers to type `/rename` again.
#   `claude --name <n>` is the documented flag for setting that name at launch (`claude --help`).
#   VERIFIED END-TO-END 2026-09-03 through the VS Code extension on a live 5-agent team: with this
#   wrapper behind `claudeCode.claudeProcessWrapper`, three reopened tabs came up `nameSource=user`
#   under their own agent names (`review`, `alice_co-agent`, `orchestrator`) while the un-reopened
#   twins stayed `derived`. The IDE resumes with the `--resume=<sid>` form and never renames after
#   launch, which is exactly the gap this closes.
#   PROVING IT REQUIRES THE TRACE BELOW: the `exec` is transparent, so a wrapped launch and a direct
#   one have identical /proc cmdlines — cmdline can NEVER tell you whether the setting took effect.
#
# WHAT IT DOES: sits in front of the real `claude` binary (VS Code setting
# `claudeCode.claudeProcessWrapper`, machine scope) and, when the launch carries `--resume <sid>`
# and no `--name`, prepends `--name <agent>` where <agent> comes from, in order:
#   1. `$PWD/.claude/agent-team-sessions` — the kit's identity map (`<sid> <agent> <date>`), the same
#      file the reground hook re-injects identity from. Stable, kit-owned.
#   2. the transcript's LAST `agent-name` record (what `/rename` and `-n` both write) — restores
#      the user's own rename on any project, kit or not. Best effort: the transcript format is
#      documented as internal, so this is a fallback, never the primary.
# Then it `exec`s the real binary. Nothing else changes; a NEW session (no --resume) passes through
# untouched — `/keel-agent-team-start` names it once, and every later resume keeps the name.
#
# FAIL-OPEN, ALWAYS: any error → exec the real binary with the ORIGINAL args. Never writes to stdout
# (the IDE speaks stream-json over it); never reads secrets; never touches the network.
#
# INSTALL (once per machine, the setting is machine-scoped — see /keel-agent-team-start §2b):
#   cp .claude/claude-launch-wrapper.sh ~/.claude/ && chmod +x ~/.claude/claude-launch-wrapper.sh
#   VS Code (remote) settings → "claudeCode.claudeProcessWrapper": "/home/<you>/.claude/claude-launch-wrapper.sh"
# Override the real binary with KEEL_CLAUDE_BIN=<path> (tests use this).
set -u

args=("$@")

# ---- 1. the real binary -------------------------------------------------------------------------
BIN="${KEEL_CLAUDE_BIN:-}"
if [ -z "$BIN" ] && [ $# -gt 0 ] && [ -x "$1" ] && [ "$(basename -- "$1")" = "claude" ]; then
  BIN="$1"; shift; args=("$@")                     # some launchers pass the executable as $1
fi
if [ -z "$BIN" ]; then
  for root in "$HOME/.vscode-server/extensions" "$HOME/.vscode/extensions" "$HOME/.vscode-insiders/extensions"; do
    cand="$(ls -d "$root"/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | sort -V | tail -1)"
    [ -n "$cand" ] && [ -x "$cand" ] && { BIN="$cand"; break; }
  done
fi
[ -z "$BIN" ] && BIN="$(command -v claude 2>/dev/null || true)"
[ -n "$BIN" ] || { echo "[keel-launch] no claude binary found" >&2; exit 127; }

# ---- opt-in trace: ONLY if the owner created the file (`touch ~/.claude/keel-launch-wrapper.log`).
# The exec is transparent — a wrapped launch and a direct one have identical /proc cmdlines — so this
# is the only way to prove the IDE setting actually took effect. Never created here; never on stdout.
LOG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/keel-launch-wrapper.log"
log() { [ -w "$LOG" ] && printf '%s pid=%s cwd=%s %s\n' "$(date -Is)" "$$" "$PWD" "$1" >> "$LOG" 2>/dev/null; return 0; }

passthrough() { log "passthrough sid=${sid:-none}"; exec "$BIN" "${args[@]}"; }

# ---- 2. already named, or not a resume → nothing to do -------------------------------------------
sid=""; prev=""
for a in "${args[@]}"; do
  case "$a" in
    -n|--name|-n=*|--name=*) passthrough ;;
    --resume=*) sid="${a#--resume=}" ;;
    -r=*) sid="${a#-r=}" ;;
  esac
  case "$prev" in --resume|-r) [ -n "$sid" ] || sid="$a" ;; esac
  prev="$a"
done
[ -n "$sid" ] || passthrough

# ---- 3. resolve the name: identity map first, transcript record second ---------------------------
name=""
map="$PWD/.claude/agent-team-sessions"
if [ -r "$map" ]; then
  name="$(awk -v s="$sid" '$1 == s { print $2; exit }' "$map" 2>/dev/null || true)"
fi
if [ -z "$name" ]; then
  cfg="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
  proj="$(printf '%s' "$PWD" | sed 's/[^A-Za-z0-9]/-/g')"
  tr_="$cfg/projects/$proj/$sid.jsonl"
  if [ -r "$tr_" ]; then
    # compact JSON in real transcripts; tolerate spacing anyway (the format is documented as internal)
    name="$(grep -oE '"type" *: *"agent-name" *, *"agentName" *: *"[^"]*"' "$tr_" 2>/dev/null | tail -1 \
            | sed -E 's/.*"agentName" *: *"//; s/"$//')"
  fi
fi
case "$name" in
  ""|*[!A-Za-z0-9_.-]*) passthrough ;;          # nothing found, or not a safe single token
esac

log "named --name=$name sid=$sid"
exec "$BIN" --name "$name" "${args[@]}"
