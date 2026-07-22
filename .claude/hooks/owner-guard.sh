#!/usr/bin/env bash
# PreToolUse(Edit|Write|NotebookEdit) hook — GOVERNANCE files are OWNER-ONLY on multi-user projects.
# Armed ONLY when .claude/project-owner exists (one line: the owner's `git config user.name`, written
# at bootstrap / /keel-plan / /keel-adopt when the project declares itself multi-user — the FOUNDER is
# asked, never assumed). Single-user projects have no file and pay nothing.
# Contract: tool call as JSON on stdin; exit 2 = BLOCK the edit, exit 0 = allow.
#
# Guarded (the founder's strategy surfaces): PLAN.md · rules.md · CLAUDE.md · docs/architecture.md ·
# docs/adr/** · .claude/{settings*.json,hooks,skills,agents,rules,project-owner}.
# Shared (every session's ritual surfaces — NEVER guarded): HANDOVER.md · LESSONS.md · TASKS.md ·
# src/ · tests/ · docs/user_manual.md — a developer session must always be able to run the rituals.
#
# Honesty (layered enforcement, docs/steering.md): this stops the AI from *drafting* foreign governance
# edits at the source — the accidental collision. The wall for intentional human edits is the HOST:
# branch protection + owner-reviewed PRs (rules.md §6) — a plain text editor bypasses any hook.
set -u
DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
OWNER_FILE="$DIR/.claude/project-owner"
[ -f "$OWNER_FILE" ] || exit 0
owner="$(head -n1 "$OWNER_FILE" 2>/dev/null | tr -d '\r' | sed 's/^ *//;s/ *$//')"
[ -n "$owner" ] || exit 0
me="$(git -C "$DIR" config user.name 2>/dev/null || true)"
# Fail-open on missing identity (blocking every edit would brick the session) — the SessionStart
# re-ground hook nags "git user.name is UNSET" instead, so the gap is visible, not silent.
[ -n "$me" ] || exit 0
[ "$me" = "$owner" ] && exit 0

fp="$(python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))' 2>/dev/null)" \
  || { echo "owner-guard.sh: could not parse hook input — allowing (check python3)" >&2; exit 0; }
[ -z "$fp" ] && exit 0
rel="${fp#"$DIR"/}"

case "$rel" in
  PLAN.md|rules.md|CLAUDE.md|docs/architecture.md|docs/adr/*|.claude/settings.json|.claude/settings.local.json|.claude/hooks/*|.claude/skills/*|.claude/agents/*|.claude/rules/*|.claude/project-owner)
    echo "$(date '+%F %T') owner-guard BLOCK: $rel by @$me" >> "$DIR/.claude/ritual-log" 2>/dev/null || true
    echo "BLOCKED by .claude/hooks/owner-guard.sh: '$rel' is a GOVERNANCE file — owner-only (owner: @$owner · you: @$me). Developers work their @-assigned TASKS items; plan/architecture/rules/ADR changes are PROPOSED to the owner (or land via a PR the owner reviews). Shared surfaces stay writable: HANDOVER/LESSONS/TASKS, src/, tests/." >&2
    exit 2 ;;
esac
exit 0
