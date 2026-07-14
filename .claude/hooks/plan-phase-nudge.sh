#!/usr/bin/env bash
# Stop hook — gentle, NON-blocking nudge fired the MOMENT a turn ends: a PLAN.md phase is
# still `wip` yet every TASKS.md `## Now` item is checked off, i.e. the phase looks finished
# but its status was never flipped (rules.md §2.7). This is the enforcement backstop that the
# four ritual update-points lacked — statuses lived only in guidance, so a skipped /keel-phase-review
# left PLAN lagging reality. Surfacing here (systemMessage) is also seen by the user, so the
# phase map can be watched from outside without waiting a whole session. Always exits 0.

DIR="${CLAUDE_PROJECT_DIR:-.}"

# Only meaningful once PLAN.md exists and is a real plan (not the bootstrap template).
[ -f "$DIR/PLAN.md" ] || exit 0
grep -q 'REPLACE this example at bootstrap' "$DIR/PLAN.md" && exit 0

# PLAN.md dirty in the working tree → it's being updated right now; stay quiet (mirrors handover-reminder).
[ -n "$(git -C "$DIR" status --porcelain -- PLAN.md 2>/dev/null)" ] && exit 0

# Which phases are `wip` in the source-of-truth table? (same table parse as session-start-reground.sh)
wip=$(awk -F'|' '$2 ~ /^ *[a-z][a-z0-9_]* *$/ && $4 ~ /^ *wip *$/ {gsub(/ /,"",$2); print $2}' "$DIR/PLAN.md" 2>/dev/null | paste -sd, -)
[ -z "$wip" ] && exit 0                                   # no wip phase → nothing to flip

# Fire only when the current batch is FINISHED: zero open `[ ]` items AND at least one checked
# `[x]` item (evidence work just completed — not merely an empty section between refills).
[ -f "$DIR/TASKS.md" ] || exit 0
now=$(sed -n '/^## Now/,/^## Next/p' "$DIR/TASKS.md" 2>/dev/null)
nowopen=$(printf '%s\n' "$now" | grep -c '^- \[ \]')
nowdone=$(printf '%s\n' "$now" | grep -cE '^- \[[xX]\]')
if [ "${nowopen:-0}" -eq 0 ] && [ "${nowdone:-0}" -ge 1 ]; then
  printf '{"systemMessage":"[keel] Phase %s is still wip but every TASKS.md ## Now item is checked off — if the gate is met, run /keel-phase-review to flip it to done in PLAN.md (rules.md §2.7); otherwise refill ## Now from the gate."}\n' "$wip"
fi
exit 0
