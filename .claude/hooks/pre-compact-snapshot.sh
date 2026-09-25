#!/usr/bin/env bash
# PreCompact hook (manual + auto) — side-effect only: PreCompact stdout CANNOT inject instructions
# into the compaction summary (that's SessionStart's job — see session-start-reground.sh); the
# manual-compact BLOCKING gate lives in compact-gate.sh (matcher "manual"). What this one CAN do is
# make compaction safe: snapshot the memory files so nothing is lost if the summary goes wrong, and
# warn (systemMessage) if the handover looks stale. Always exits 0 — never blocks auto-compact.
set -u
DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
payload="$(cat 2>/dev/null || true)"   # carries "trigger": manual|auto
SNAP="$DIR/.claude/snapshots"

# If the snapshot dir can't be created, say so loudly — a silent no-op would defeat the safety net —
# but still fall through to the staleness warning below.
if mkdir -p "$SNAP" 2>/dev/null; then
  ts=$(date +%Y%m%d-%H%M%S)
  for f in HANDOVER.md LESSONS.md TASKS.md; do
    [ -f "$DIR/$f" ] && cp "$DIR/$f" "$SNAP/${ts}-${f}" 2>/dev/null
  done
  # Prune: keep the 30 most recent SELF-GENERATED snapshots only (never touch user-dropped files).
  ls -1t "$SNAP" 2>/dev/null | tail -n +31 | while IFS= read -r old; do
    case "$old" in
      [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-*-*.md) rm -f "$SNAP/$old" ;;
    esac
  done
else
  printf '{"systemMessage":"[keel] pre-compact snapshot FAILED: cannot create .claude/snapshots/ — memory files are NOT backed up for this compaction."}\n'
fi

# Stale-handover warning: tree changed but HANDOVER.md untouched → the summary may be the only record.
# Ask git about the exact file (an unanchored grep would be fooled by e.g. backend/HANDOVER.md).
if git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  changed=$(git -C "$DIR" status --porcelain 2>/dev/null)
  if [ -n "$changed" ] && [ -z "$(git -C "$DIR" status --porcelain -- HANDOVER.md 2>/dev/null)" ]; then
    # DURABLE marker first: the systemMessage below dies with the context it warns, so an AUTO
    # compaction would otherwise leave NO record that this boundary was crossed without a handover
    # block (field case: a fix committed at 07:41, auto-compact at 07:43, its WHY reached disk at
    # 07:53 only because a ritual happened to run). The SessionStart hook reads this line back.
    trig=$(printf '%s' "$payload" | grep -o '"trigger"[[:space:]]*:[[:space:]]*"[a-z]*"' | grep -o '[a-z]*"$' | tr -d '"')
    echo "$(date '+%F %T') compact ${trig:-?} STALE-DISK: tree dirty, HANDOVER.md untouched" >> "$DIR/.claude/ritual-log" 2>/dev/null || true
    printf '{"systemMessage":"[keel] Compacting with a dirty tree but HANDOVER.md not updated — the WHY of this work may now exist only in the summary. A STALE-DISK line was written to .claude/ritual-log; the next session start asks you to settle it first. Next time run /keel-compact (snapshot saved to .claude/snapshots/)."}\n'
  fi
fi
exit 0
