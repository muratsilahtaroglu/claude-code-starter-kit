---
name: keel-audit
description: Periodic rules-compliance spot-check — spawns the read-only auditor subagent over the commits since the last audit, reports violations with file:line + rule §, fixes only what the user approves. Skips itself on an empty (phase-0) project.
---

# /keel-audit — check the recent work against rules.md

When: the SessionStart hook nudges (default: >25 commits since the last audit), at `/keel-phase-review`, or
on demand. Complements — never replaces — `/keel-distill` (memory lint) and `verifier` (single claims): this
is the "is the project still following its own constitution?" sweep. Post-compact drift gets a free
30-second inline self-check from the re-ground hook; this skill is the deep pass.

0. **Follow-up FIRST — what became of the LAST audit's findings.** Open the previous report
   (`reports/<date>-audit.md`, newest) and, before any new finding, write one line per earlier
   finding: `id · decision (fixed / deferred / rejected) · landed? (sha or "not landed") ·
   measurement then → now`. Count the fourth outcome separately — *silently dropped* (evaluated, never
   tracked) — and re-measure every rejection's stated reason: is it still true today? A landed fix
   whose number did not move is itself a finding. First audit: write "first round, no follow-up" —
   the section is never skipped. Field: an audit's 30 recommendations were all evaluated and none
   tracked until this table existed; a finding-producing audit that never measures change is noise.
1. **Scope.** Phase-0 guard: if the source tree is still empty and the docs are placeholders, report
   "phase 0 — nothing to audit yet" and stop. Otherwise the range is `$(cat .claude/last-audit)..HEAD`
   when the marker exists (else the last ~25 commits).
2. **Run.** Spawn the `auditor` subagent (`.claude/agents/auditor.md`) with the range — don't audit
   inline; the point is fresh eyes in an isolated context. Spot-check its claims before acting (§4.11:
   verify, don't trust).
3. **Report & fix.** Present the severity-ranked table. Apply ONLY user-approved fixes; real-but-deferred
   findings get one line each in `TASKS.md ## Discovered`. Never fix silently (§10.36).
4. **Record.** Write the findings table + the follow-up table + the auditor's own hit rate
   (`refuted claims / total claims`, from your spot-check in step 2 — a critic whose accuracy is never
   measured becomes a voice nobody can challenge) to `reports/<date>-audit.md` — that file is what
   the NEXT audit's step 0 reads. Write the audited HEAD sha to `.claude/last-audit` (resets the
   hook's due-counter); add the HANDOVER block (a) one-liner `audit @ <sha>: N findings, M fixed,
   hit rate K/N`; commit with approval (rules.md §1.3).
5. **Not this skill's job:** critiquing whether a RULE is right or the process is healthy. That is the
   owner-triggered `observer` agent (`.claude/agents/observer.md`) — compliance here, critique there;
   neither output stands in for the other's.
