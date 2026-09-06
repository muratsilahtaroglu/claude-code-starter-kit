# .claude/agents/ — reusable subagents

Subagents are isolated assistants for side tasks (deep research, audits, verification) that would
clutter the main thread with intermediate results you won't reference again. Each runs in its **own
context window** and returns only its final message to the parent — so the raw exploration never enters
your main context. Called via the Agent tool (by name); defined here as a markdown file with `name` /
`description` / optional `tools` / `model` frontmatter + a system-prompt body.

Shipped with the kit:
- **`researcher`** — cited prior-art scout (web + local repo); backs rules.md §8 and `/keel-research`.
- **`verifier`** — adversarial fact-checker (CONFIRMED / REFUTED / UNCERTAIN); backs rules.md §4.
- **`auditor`** — read-only rules-compliance spot-check over a commit range; backs `/keel-audit` (the
  SessionStart hook nudges when one is due).
- **`observer`** — OWNER-triggered outside eye, never spawned by the orchestrator: critiques the process
  and the rules themselves (compliance is the auditor's axis, critique is this one's), writes only under
  `reports/team/<owner-tag>/observer/`, and opens every round with what became of the LAST round's
  findings plus its own refuted/total ratio. Field-earned on a 5-agent team (2026-09-05/06): 30
  recommendations were evaluated and none tracked until the follow-up duty existed.

**Add project-specific subagents here as the project needs them** — e.g. a `regression-runner`, a
`migration-reviewer`, a `log-analyst`. The set is meant to **grow per project**, not stay fixed. Keep
each agent's body focused; put "when to use it" in the `description` (that's what drives auto-selection).
Mechanism trade-offs (skill vs subagent vs rule vs hook): `docs/steering.md`.
