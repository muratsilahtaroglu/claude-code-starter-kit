#!/usr/bin/env bash
# PreToolUse(Bash) hook — blocks a few catastrophic / secret-leaking commands (rules.md §5,§6).
# Contract: read the tool call as JSON on stdin; exit 2 = BLOCK the command, exit 0 = allow.
# Deliberately conservative (few, high-signal patterns) so it doesn't nag on normal work. Tune freely.

# Fail-open trade-off (documented): if python3 is missing or stdin isn't JSON, we allow with a stderr
# note rather than blocking every Bash call — this hook is belt-and-suspenders on top of rules.md, and
# a broken guard must not brick the session. The gitleaks pre-commit hook + CI are the backstops.
cmd="$(python3 -c 'import sys, json; print(json.load(sys.stdin).get("tool_input", {}).get("command", ""))' 2>/dev/null)" \
  || echo "block-dangerous.sh: could not parse hook input — allowing (check python3)" >&2
[ -z "$cmd" ] && exit 0

block() {
  # telemetry (best-effort): BLOCK events land in the ritual-log too
  # Telemetry only from a REAL invocation: Claude Code exports CLAUDE_PROJECT_DIR to every hook,
  # an ad-hoc probe does not. Defaulting to "." let probe runs pollute the live log (2026-08-19).
  # The BLOCK itself never depends on this — the guard is below, unconditional.
  [ -n "${CLAUDE_PROJECT_DIR:-}" ] && \
    echo "$(date '+%F %T') block-dangerous BLOCK: $1" >> "${CLAUDE_PROJECT_DIR}/.claude/ritual-log" 2>/dev/null || true
  echo "BLOCKED by .claude/hooks/block-dangerous.sh: $1" >&2; exit 2
}

# 1) Recursive delete of root / home / cwd — including the whole-cwd GLOBS (rm -rf * / .* / .[!.]*).
#    Flags and TARGET are matched INDEPENDENTLY: the old pattern required them adjacent, which is
#    exactly what let `rm -rf -- /` and `rm -rf --no-preserve-root /` through (the separator/long
#    flag sits between them) while `rm -rf *` never matched a target at all — three shipped
#    bypasses, found 2026-08-18 (reports/2026-08-18-hook-audit.md).
#    Scoped per shell SEGMENT (split on |;&) and only to what follows the `rm` token, so a target
#    belonging to a DIFFERENT command is not attributed to rm: `rm -rf ./build && cd /` and
#    `find . -exec rm -rf {} +` stay allowed.
#    A catastrophic target is a STANDALONE token — / // /* ~ ~/ ~/* $HOME . ./ ./* * ** .* .[!.]*
#    — never a scoped path (./build, /srv/app, ~/proj/x) nor a filtered glob (*.log, build/*).
#    (No \b anywhere in this file — it is a GNU extension that silently never matches on
#    BSD/macOS grep, i.e. a guard that quietly stops guarding on someone else's laptop.)
#    Finally, `rm` must sit in COMMAND position — segment start, seeing through a wrapper and its
#    flags (sudo -u root rm … is NOT covered — a wrapper flag that takes a VALUE hides the
#    command; `xargs -0 rm …` and plain `sudo rm …` are). Stated rather than silently assumed.
#    Matching an `rm` token ANYWHERE fires on everyday commands that merely contain one —
#    `docker build --rm -f Dockerfile .` and `git rm -r --cached .` both tripped it during this
#    fix, and a guard that nags on normal work gets disabled, which costs more than it saves.
rm_flag='([[:space:]]-[a-zA-Z]*[rf][a-zA-Z]*([[:space:]]|$)|[[:space:]]--(recursive|force)([[:space:]]|$))'
rm_target='(^|[[:space:]])(/|~|\$HOME|\.|\*|\.\[!\.\]\*)[/*]*([[:space:]]|$)'
while IFS= read -r seg; do
  seg="$(printf '%s' "$seg" | sed -E 's/^[[:space:]]*//; s/^(sudo|command|time|nohup|xargs)([[:space:]]+-[^[:space:]]+)*[[:space:]]+//')"
  printf '%s' "$seg" | grep -Eq '^rm([[:space:]]|$)' || continue
  args="$(printf '%s' "$seg" | sed -E 's/^rm//')"
  printf '%s' "$args" | grep -Eq "$rm_flag" || continue
  if printf '%s' "$args" | grep -Eq "$rm_target"; then
    block "recursive delete of root/home/cwd (or a whole-cwd glob)"
  fi
done <<EOF
$(printf '%s' "$cmd" | tr '|;&' '\n')
EOF

# 2) Force push (allow the safer --force-with-lease). A leading '+' on a refspec (git push
#    origin +main) is git's OWN short form for --force and was slipping past both this rule and
#    owner-guard's main-branch wall — one blind spot in two independent walls (audit 2026-08-18).
#    Checked per SEGMENT like rule 1: scanning the whole command read `echo +done` in an
#    unrelated segment as a force refspec.
push_force='(--force([[:space:]]|=|$)|[[:space:]]-f([[:space:]]|$)|[[:space:]]\+[A-Za-z0-9_/.:^~-]+([[:space:]]|$))'
while IFS= read -r seg; do
  printf '%s' "$seg" | grep -Eq 'git[[:space:]]+push' || continue
  printf '%s' "$seg" | grep -Eq "$push_force" || continue
  printf '%s' "$seg" | grep -q 'force-with-lease' && continue
  block "git push --force — use --force-with-lease and get approval (rules.md §6)"
done <<EOF
$(printf '%s' "$cmd" | tr '|;&' '\n')
EOF

# 3) Staging a real .env — including variants (.env.production/.env.local/...) but not .env.example.
#    The allowed name is STRIPPED first, so `git add .env .env.example` can't ride along on the
#    exclusion, and the variant pattern catches `.env.<anything>`. The check is scoped to the
#    command SEGMENTS (split on |;&) that actually contain `git add` — a `.env` in an unrelated
#    segment (e.g. `git add -A && git diff | grep '\.env'`) is a grep pattern, not a staged file
#    (this false-positive bit two real projects). Trade-off: an exotic `echo .env | xargs git add`
#    now passes — the pre-commit no-tracked-dotenv hook + CI secret-file guard are the backstops.
if printf '%s' "$cmd" | grep -Eq 'git[[:space:]]+add'; then
  stripped="$(printf '%s' "$cmd" | sed 's/\.env\.example//g')"
  if printf '%s\n' "$stripped" | tr '|;&' '\n\n\n' | grep -E 'git[[:space:]]+add' \
     | grep -Eq '(^|[[:space:]"'\''=/])\.env(\.[A-Za-z0-9_-]+)?([[:space:]"'\''*]|$)'; then
    block "staging a .env file — secrets must never be committed (rules.md §5)"
  fi
fi

# 4) Piping remote content straight into a shell.
if printf '%s' "$cmd" | grep -Eq '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba)?sh([[:space:]]|$)'; then
  block "piping remote content into a shell (supply-chain risk, docs/security.md)"
fi

exit 0
