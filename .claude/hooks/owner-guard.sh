#!/usr/bin/env bash
# PreToolUse(Edit|Write|NotebookEdit + Bash) hook — OWNER-ONLY walls on multi-user projects.
# Armed ONLY when .claude/project-owner exists (one line: the owner's `git config user.name`, written
# at bootstrap / /keel-plan / /keel-adopt when the project declares itself multi-user — the FOUNDER is
# asked, never assumed). Single-user projects have no file and pay nothing.
# Contract: tool call as JSON on stdin; exit 2 = BLOCK the call, exit 0 = allow.
#
# Two walls, one owner check:
#  - Edit|Write|NotebookEdit → GOVERNANCE files (the founder's strategy surfaces): PLAN.md · rules.md ·
#    CLAUDE.md · docs/architecture.md · docs/adr/** · .claude/{settings*.json,hooks,skills,agents,
#    rules,project-owner}. Shared ritual surfaces (HANDOVER/LESSONS/TASKS, src/, tests/) are NEVER
#    guarded — a developer session must always be able to run the rituals.
#  - Bash → `git push` targeting main/master (explicit refspec, or a bare push while checked out on
#    it): main is OWNER-merged (rules.md §6) — developers push topic branches (on their fork when
#    upstream is read-only) and open a PR. Keeps even a fork's own main clean = a clean PR base.
#
# Honesty (layered enforcement, docs/steering.md "Multi-user"): this stops the AI from *drafting* the
# foreign edit / push — the accidental collision. The wall for intentional human action is the HOST
# (org Read role + fork PRs, or an enforced branch ruleset) — a plain terminal bypasses any hook.
set -u
DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
OWNER_FILE="$DIR/.claude/project-owner"
[ -f "$OWNER_FILE" ] || exit 0
owner="$(head -n1 "$OWNER_FILE" 2>/dev/null | tr -d '\r' | sed 's/^ *//;s/ *$//')"
[ -n "$owner" ] || exit 0
me="$(git -C "$DIR" config user.name 2>/dev/null || true)"
# Fail-open on missing identity (blocking every call would brick the session) — the SessionStart
# re-ground hook nags "git user.name is UNSET" instead, so the gap is visible, not silent.
[ -n "$me" ] || exit 0
[ "$me" = "$owner" ] && exit 0

payload="$(cat 2>/dev/null || true)"
field() { # best-effort JSON field via python3 ($1 = accessor suffix); empty on any failure (fail-open)
  printf '%s' "$payload" | python3 -c "import sys, json
print(json.load(sys.stdin)$1)" 2>/dev/null || true
}
tool="$(field '.get("tool_name", "")')"

deny() { # $1 = short reason (telemetry) · $2 = full message
  echo "$(date '+%F %T') owner-guard BLOCK: $1 by @$me" >> "$DIR/.claude/ritual-log" 2>/dev/null || true
  echo "$2" >&2
  exit 2
}

if [ "$tool" = "Bash" ]; then
  cmd="$(field '.get("tool_input", {}).get("command", "")')"
  [ -z "$cmd" ] && exit 0
  hit=""
  # Examine each shell segment (split on |;&) that is a `git … push …` invocation.
  while IFS= read -r seg; do
    printf '%s' "$seg" | grep -Eq '(^|[^[:alnum:]_.])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+push([^[:alnum:]_-]|$)' || continue
    # (a) explicit main/master anywhere in the remote/refspec part (origin main · HEAD:main · :main)
    if printf '%s' "$seg" | grep -Eq '[[:space:]:/](main|master)([[:space:]:]|$)'; then
      hit="explicit main refspec"; break
    fi
    # (b) bare push (≤1 non-flag token after `push` = remote only, no refspec) while checked out on it
    rest="$(printf '%s' "$seg" | sed -E 's/.*[^[:alnum:]_-]push//')"
    nonflags=0
    for w in $rest; do case "$w" in -*) ;; *) nonflags=$((nonflags+1)) ;; esac; done
    if [ "$nonflags" -le 1 ]; then
      br="$(git -C "$DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
      case "$br" in main|master) hit="bare push on $br"; break ;; esac
    fi
  done <<EOF
$(printf '%s' "$cmd" | tr '|;&' '\n')
EOF
  if [ -n "$hit" ]; then
    deny "git push main ($hit)" "BLOCKED by .claude/hooks/owner-guard.sh: pushing to main/master is OWNER-only on this multi-user project (owner: @$owner · you: @$me). Push a topic branch instead — git push origin <branch> (on your FORK when upstream is read-only) — and open a PR the owner merges (rules.md §6 · docs/steering.md 'Multi-user' · the project's team doc if present)."
  fi
  exit 0
fi

# Edit|Write|NotebookEdit (any call carrying a file_path): the governance wall.
fp="$(field '.get("tool_input", {}).get("file_path", "")')"
[ -z "$fp" ] && exit 0
rel="${fp#"$DIR"/}"

case "$rel" in
  PLAN.md|rules.md|CLAUDE.md|docs/architecture.md|docs/adr/*|.claude/settings.json|.claude/settings.local.json|.claude/hooks/*|.claude/skills/*|.claude/agents/*|.claude/rules/*|.claude/project-owner|.claude/keel-caps)
    deny "$rel" "BLOCKED by .claude/hooks/owner-guard.sh: '$rel' is a GOVERNANCE file — owner-only (owner: @$owner · you: @$me). Developers work their @-assigned TASKS items; plan/architecture/rules/ADR changes are PROPOSED to the owner (or land via a PR the owner reviews). Shared surfaces stay writable: HANDOVER/LESSONS/TASKS, src/, tests/." ;;
esac
exit 0
