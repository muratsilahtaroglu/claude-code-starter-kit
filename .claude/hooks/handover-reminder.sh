#!/usr/bin/env bash
# Stop hook — gentle, NON-blocking nudge to update HANDOVER.md when the working tree changed
# this session but HANDOVER.md wasn't touched (rules.md §1.4). Always exits 0 (never blocks stopping).

DIR="${CLAUDE_PROJECT_DIR:-.}"
changed="$(git -C "$DIR" status --porcelain 2>/dev/null)"
[ -z "$changed" ] && exit 0                             # clean tree → nothing to hand over
# Ask git about the exact file (an unanchored grep would be fooled by e.g. backend/HANDOVER.md).
[ -n "$(git -C "$DIR" status --porcelain -- HANDOVER.md 2>/dev/null)" ] && exit 0  # already updated → quiet

# Advisory only. `systemMessage` is shown to the user; exit 0 lets the turn end normally.

# Telemetry (rules §9 observability): record that the nudge actually FIRED. Without this line a
# Stop hook is invisible — "did the handover reminder ever appear?" cannot be answered from the
# ritual-log, which is the only durable record of what the enforcement layer did. Guarded on
# CLAUDE_PROJECT_DIR so an ad-hoc probe never writes into the live log.
[ -n "${CLAUDE_PROJECT_DIR:-}" ] && \
  echo "$(date '+%F %T') nudge handover" >> "${CLAUDE_PROJECT_DIR}/.claude/ritual-log" 2>/dev/null || true
printf '{"systemMessage":"Reminder (rules.md §1.4): the working tree changed but HANDOVER.md was not updated this session — consider /keel-handover before ending (about to /compact? run /keel-compact instead: it refreshes the disk first, then hands off)."}\n'
exit 0
