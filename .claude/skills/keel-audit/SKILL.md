---
name: keel-audit
description: Periodic rules-compliance spot-check — spawns the read-only auditor subagent over the commits since the last audit, reports violations with file:line + rule §, fixes only what the user approves. Skips itself on an empty (phase-0) project.
---

# /keel-audit — check the recent work against rules.md

When: the SessionStart hook nudges (default: >25 commits since the last audit), at `/keel-phase-review`, or
on demand. Complements — never replaces — `/keel-distill` (memory lint) and `verifier` (single claims): this
is the "is the project still following its own constitution?" sweep. Post-compact drift gets a free
30-second inline self-check from the re-ground hook; this skill is the deep pass.

1. **Scope.** Phase-0 guard: if the source tree is still empty and the docs are placeholders, report
   "phase 0 — nothing to audit yet" and stop. Otherwise the range is `$(cat .claude/last-audit)..HEAD`
   when the marker exists (else the last ~25 commits).
2. **Run.** Spawn the `auditor` subagent (`.claude/agents/auditor.md`) with the range — don't audit
   inline; the point is fresh eyes in an isolated context. Spot-check its claims before acting (§4.11:
   verify, don't trust).
3. **Report & fix.** Present the severity-ranked table. Apply ONLY user-approved fixes; real-but-deferred
   findings get one line each in `TASKS.md ## Discovered`. Never fix silently (§10.36).
4. **Record.** Write the audited HEAD sha to `.claude/last-audit` (this resets the hook's due-counter);
   add the HANDOVER block (a) one-liner `audit @ <sha>: N findings, M fixed`; commit with approval
   (rules.md §1.3).
