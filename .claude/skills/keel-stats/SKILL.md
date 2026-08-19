---
name: keel-stats
description: Render the ritual telemetry visually — turns .claude/ritual-log into reports/ritual-stats.md with PLAN.md-style colored Mermaid interval boxes (session/compact boundaries) + a counts table. Answers "which skills/commands/hooks ran, how often, in which interval".
---

# /keel-stats — see what ran, when, how often

The `ritual-log` hook records every Skill-tool call, user-typed command (custom = `command …`
via UserPromptExpansion; built-ins like `/compact` = `typed /…` via UserPromptSubmit — first
token only, user prose never logged), compact boundary, session start and hook BLOCK into
`.claude/ritual-log` (machine-local, git-ignored, self-trimmed). This skill renders it for humans.

1. Run the deterministic generator — never parse the log by hand:
   ```bash
   python3 .claude/ritual-report.py
   ```
2. Open / point the user at **`reports/ritual-stats.md`** — the Mermaid timeline renders on
   GitHub and in the VSCode markdown preview: one colored box per interval (green = session
   start, amber = manual compact, red = auto compact; PLAN.md's palette), event counts inside,
   full detail in the table below it.
3. Quote the headline numbers (totals line) back to the user in one sentence.
4. Scope honesty: the log is machine-local and trimmed to ~1000 lines — long-horizon history
   lives in git/HANDOVER, not here. Do not commit the report unless the user asks (it is a
   regenerable artifact; the compact-gate ignores it either way).
