#!/usr/bin/env bash
# SessionStart hook (sources: startup|resume|clear|compact). stdout IS added to Claude's context
# (unlike PreCompact, which cannot inject). On a context RESET (compact|resume|clear) it emits a
# re-read directive to recover lost state; on a cold startup it emits a lighter orientation nudge
# (nothing was lost — no need to command "work only on ## Now"). Always emits memory-file cap
# warnings. Always exits 0 — never blocks a session.
set -u
DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Claude Code pipes a JSON payload with the trigger "source" on stdin; read it (non-fatal if absent).
payload="$(cat 2>/dev/null || true)"
source="$(printf '%s' "$payload" | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-zA-Z]*\)".*/\1/p')"

case "$source" in
  compact|resume|clear)
    echo "[keel] Context was reset ($source) — re-read HANDOVER.md (TOP block = current state), LESSONS.md, TASKS.md '## Now', and PLAN.md (current focus) to recover state before continuing; resume from a '## Now' item."
    echo "[keel] Post-reset self-check (30s, inline — no sub-agent): does the in-flight work still respect rules.md §3 layout / §5 security / §2 tests? Catch drift at the reset point; /keel-audit is the deep pass when due." ;;
  *)
    echo "[keel] Keel project — skim HANDOVER.md (top block) · LESSONS.md · TASKS.md '## Now' · PLAN.md (current focus) to get oriented (rules.md §1)." ;;
esac

# Cap checks (rules.md §9.33): warn when a memory file needs /keel-distill. Thresholds mirror rules.md §1.4
# / §9.33 and HANDOVER.md's header — keep the three in sync if you change a cap.
warn_cap() { # $1=file $2=max_lines
  [ -f "$DIR/$1" ] || return 0
  lines=$(wc -l < "$DIR/$1" 2>/dev/null || true)
  lines=${lines:-0}
  if [ "$lines" -gt "$2" ]; then
    echo "[keel] $1 is ${lines} lines (cap ~$2) — run /keel-distill before adding more."
  fi
}
warn_cap "HANDOVER.md" 200
warn_cap "LESSONS.md" 100
warn_cap "TASKS.md" 100

# Rule-budget check (rules.md §10.38): the constitution is capped like the memory files — a rules.md
# nobody can hold in attention stops steering anything.
if [ -f "$DIR/rules.md" ]; then
  rlines=$(wc -l < "$DIR/rules.md" 2>/dev/null || true)
  rlines=${rlines:-0}
  if [ "$rlines" -gt 200 ]; then
    echo "[keel] rules.md is ${rlines} lines (budget ~200 lines / ~40 rules — rules.md §10.38): merge/retire a rule or promote it to a hook instead of appending."
  fi
fi

# Block-count check: >5 SESSION blocks in HANDOVER.md → rotation due.
# Count only dated block headings (### YYYY-MM-DD ...) — other ### headings (e.g. the area-handover
# index) and the unfilled <YYYY-MM-DD> placeholder must not inflate the count.
if [ -f "$DIR/HANDOVER.md" ]; then
  blocks=$(grep -cE '^### [0-9]{4}-[0-9]{2}-[0-9]{2}' "$DIR/HANDOVER.md" 2>/dev/null || true)
  blocks=${blocks:-0}
  if [ "$blocks" -gt 5 ]; then
    echo "[keel] HANDOVER.md has ${blocks} session blocks (max 5) — run /keel-distill to rotate the oldest to docs/handover-archive.md."
  fi
fi

# Handover-staleness check (rules.md §1.4): commits kept landing but HANDOVER.md didn't move — the top
# block may no longer describe reality (ritual decay, caught early). Threshold: 10 commits (~2 sessions
# at normal commit cadence); tune freely. Skips quietly when HANDOVER.md has no commit history yet.
if git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  last=$(git -C "$DIR" log -1 --format=%H -- HANDOVER.md 2>/dev/null)
  if [ -n "$last" ]; then
    behind=$(git -C "$DIR" rev-list --count "${last}..HEAD" 2>/dev/null || true)
    behind=${behind:-0}
    if [ "$behind" -gt 10 ]; then
      echo "[keel] HANDOVER.md last changed ${behind} commits ago — its top block may be stale; run /keel-handover (or verify it still matches reality) before relying on it."
    fi
  fi
fi

# Audit-due nudge (/keel-audit): deterministic detection ONLY — the hook never spawns the auditor itself.
# Marker: .claude/last-audit (the audited HEAD sha, written by /keel-audit; committed, so the whole team
# shares one clock). Threshold: 25 commits (~5 sessions); tune freely. A missing/invalid marker counts
# from the beginning of history — right for brownfield adopts, quiet on young repos.
if git -C "$DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  base=""
  [ -f "$DIR/.claude/last-audit" ] && base="$(tr -cd '0-9a-fA-F' < "$DIR/.claude/last-audit" | head -c 40)"
  if [ -n "$base" ] && git -C "$DIR" cat-file -e "${base}^{commit}" 2>/dev/null; then
    n=$(git -C "$DIR" rev-list --count "${base}..HEAD" 2>/dev/null || true)
  else
    n=$(git -C "$DIR" rev-list --count HEAD 2>/dev/null || true)
  fi
  n=${n:-0}
  if [ "$n" -gt 25 ]; then
    echo "[keel] ${n} commits since the last rules audit — run /keel-audit at the next natural boundary (it skips itself on a phase-0 project)."
  fi
fi

# PLAN drift check (warn-only): PLAN.md's phase table is the source of truth; the mermaid block between
# the KEEL_PLAN_DIAGRAM markers is REGENERATED from it, and TASKS '## Now' carries the wip work.
# Deterministic detection only — regenerating is /keel-plan | /keel-handover's job. Skips the untouched template.
if [ -f "$DIR/PLAN.md" ] && ! grep -q 'REPLACE this example at bootstrap' "$DIR/PLAN.md"; then
  tbl=$(awk -F'|' '$2 ~ /^ *[a-z][a-z0-9_]* *$/ && $4 ~ /^ *(todo|wip|done) *$/ {gsub(/ /,"",$2); gsub(/ /,"",$4); print $2":"$4}' "$DIR/PLAN.md" 2>/dev/null | sort)
  dgm=$(sed -n '/KEEL_PLAN_DIAGRAM_BEGIN/,/KEEL_PLAN_DIAGRAM_END/p' "$DIR/PLAN.md" 2>/dev/null \
        | grep -oE '^ *[a-z][a-z0-9_]*\["[^"]*"\]:::(todo|wip|done)' \
        | sed -E 's/^ *([a-z][a-z0-9_]*)\["[^"]*"\]:::/\1:/' | sort)
  if [ -n "$tbl" ] && [ "$tbl" != "$dgm" ]; then
    echo "[keel] PLAN.md drift: the phase table and the diagram block disagree — regenerate the diagram from the table (/keel-plan step 2)."
  fi
  if printf '%s\n' "$tbl" | grep -q ':wip$' && [ -f "$DIR/TASKS.md" ]; then
    nowopen=$(sed -n '/^## Now/,/^## Next/p' "$DIR/TASKS.md" 2>/dev/null | grep -c '^- \[ \]')
    if [ "${nowopen:-0}" -eq 0 ]; then
      echo "[keel] PLAN.md has a wip phase but TASKS.md '## Now' is empty — refill Now from the wip gate (or flip the phase)."
    fi
  fi
fi
exit 0
