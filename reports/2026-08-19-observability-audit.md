# Observability audit — can we tell whether a ritual actually ran?

_2026-08-19 · internal measurement · subject: `.claude/ritual-log`, the four telemetry
registrations, and `/keel-stats`. Prompted by the owner's question: "hook mekanizmasını nasıl
denetliyoruz — keel-compact çalıştı mı, çalışmadı mı?"_

## Headline

| | |
|---|---|
| Answerable today | **yes** — `command keel-compact` (you typed it) and `skill keel-compact` (the body ran) are separate lines |
| Defects found | **4** |
| Of which had been actively misleading | **1**, at every session start for two days |
| A wrong conclusion this audit itself produced first | **1** — see "The instrument again" |

## What the layer looks like

Three layers answer three different questions, and only the third was weak:

| Question | Mechanism | State |
|---|---|---|
| Is the hook registered? | reground's decorative-hook detector · `/hooks` · `test_every_hook_file_is_registered` | sound |
| Does it behave correctly? | `test_keel_hooks.py`, 148 cases | sound (added 2026-08-18) |
| **Did it run?** | `.claude/ritual-log` + `/keel-stats` | **four defects** |

A worked trace from a live project, which is the answer to the owner's question:

```
06:21:13  compact-gate BLOCK: stale manual /compact   ← a plain /compact was STOPPED
06:21:13  compact manual                               ← the PreCompact event itself
06:21:24  command keel-compact                         ← 11s later, the ritual was run
06:28:40  compact manual
06:31:26  session-start compact                        ← compaction actually happened
```

**Reading rule, proven by that trace:** a `compact` line records an *attempt*. It happened only if a
`session-start compact` follows; if a gate BLOCK sits next to it, it did not.

Measured over 713 lines of a live multi-agent project: 497 `session-start` · 88 `compact` (all
`manual`, zero `auto`) · 62 `command` · 41 `skill` · 19 `compact-gate` BLOCK. All four registrations
fire.

## Defect 1 — the measurement contaminated what it measured

`block()` wrote to `${CLAUDE_PROJECT_DIR:-.}/.claude/ritual-log`. Claude Code exports that variable
to every real hook invocation; an ad-hoc probe piping a payload by hand does not, so probe runs
appended to the **live** log.

Consequence, and it was not theoretical: the duplicate-line detector reported

> *"ritual-log has N back-to-back duplicate lines — hooks are double-firing … disable/uninstall that
> plugin"*

at **every session start for two days**, on a machine with no plugin installed. Of the 11 adjacent
duplicates, **10 were test runs** of the hook matrix and 1 was a genuine double session-start from
2026-07-21.

**Fix:** telemetry is written only when `CLAUDE_PROJECT_DIR` is set. The guard itself never depends
on it — losing the log must never lose the wall, and there is a test for exactly that.

## Defect 2 — the detector's signal was the wrong signal

It counted *any* adjacent identical lines. But a repeated BLOCK line is normal: one guard
legitimately stops two commands of the same class in a row. Only **event** lines can prove double
registration, because one session start or one compact boundary must be recorded once.

**Fix:** the detector now looks at `session-start|compact|skill|command` only. Verified both ways —
four identical `session-start` lines still flag; six identical BLOCK lines no longer do.

## Defect 3 — Stop hooks left no trace

`handover-reminder.sh` and `plan-phase-nudge.sh` wrote nothing, so "did the handover reminder ever
appear?" was unanswerable. **Fix:** each records `nudge handover` / `nudge phase-review` *when it
actually fires* — a test asserts the silent path logs nothing, since a log claiming enforcement that
never happened is worse than no log.

## Defect 4 — an agent team wrote one log with no attribution

Seven concurrent sessions of one project all append here, and nothing said which. "Which agent
compacted?" and "whose skill call was that?" became unanswerable exactly when a team makes them
matter.

**Fix:** every line now carries `@agent` when the session adopted one, resolved from
`.claude/agent-team-sessions` — the same `session_id → agent` map the reground hook already reads.
No map or unadopted session means no tag, never a failure. `/keel-stats` lists the agents it saw,
and warns when a roster exists but no line is tagged.

## Also fixed: the same class bug, one hook further

`plan-phase-nudge.sh` counted `## Now` items with `sed -n '/^## Now/,/^## Next/p'` — the section-order
assumption fixed in reground on 2026-08-18. With `## Review` placed between them it counted another
section's checkboxes as the phase's. Now stops at the next `## ` heading, whatever it is.

## The instrument again

This audit's own first conclusion was wrong, in exactly the way the kit keeps writing rules about.
The kit repo's log showed **0 `skill` lines and 1 `command` line**, and that was read as "those two
events don't fire in this environment". The real explanation was mundane: **no skill had ever been
run in that repo.** A live project's log carried 41 and 62. The measurement was correct; the
inference blamed the mechanism instead of checking the obvious cause first (rules §10.37).

`/keel-stats` now refuses to let a reader repeat that: a kind with zero records is reported as a
statement about the *instrument*, not about the project.

## Verification

```
tests/unit/test_keel_telemetry.py — 13 cases, all green
```

Both behavioural fixes were shown revert-sensitive against the previous commit:

| | old code | new code |
|---|---|---|
| probe run with no `CLAUDE_PROJECT_DIR` | wrote into the live log | writes nothing |
| six adjacent BLOCK lines | 1 false "double-firing" warning | silent |
