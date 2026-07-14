# docs/steering.md — which Claude Code mechanism for what

Claude Code offers several ways to steer an agent; each has a different context cost, authority, and
compaction behavior. Put each instruction in the RIGHT one instead of piling everything into `CLAUDE.md`.
(Reference: Anthropic, ["Steering Claude Code"](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more).)

| Mechanism | What it's for | Loads | Survives compaction? | Authority |
|---|---|---|---|---|
| **`CLAUDE.md`** (root) | **Facts**: build commands, layout, conventions, the always-true rules (via `@`-imports) | every session, in full | ✅ re-injected from disk | guidance |
| **`.claude/rules/`** | Constraints; **path-scoped** ones (with `paths:`) load only for matching files | unscoped: always · scoped: on match | unscoped ✅ · scoped ❌ (until a match is re-read) | guidance |
| **`.claude/skills/`** | **Procedures** you want to watch/steer in the main thread (deploy, handover, review) | name+desc always · body when invoked | ✅ invoked bodies re-injected (to a budget) | guidance |
| **`.claude/agents/`** | **Side tasks** whose intermediate output would clutter the thread (deep research, audits, verification) | name+desc always · body only when called | isolated context — bypasses main compaction | guidance |
| **`.claude/hooks/`** | Things that must happen **deterministically** (block a command, snapshot, re-ground) | on lifecycle events | ✅ runs outside the context window | **enforced** |
| **`.claude/settings.json` permissions** | Hard **allow/deny/ask** on tools (deny reading secrets, ask before push) | always | ✅ | **enforced** |

## Rules of thumb (from the Anthropic guidance)
- **"Every time X, always do Y"** or **"never do X"** → a **hook** or a **permission**, not a `CLAUDE.md`
  line. Instructions are probabilistic; only hooks/permissions are guarantees.
- **A 30-line procedure** → a **skill**, not `CLAUDE.md`. Facts go in `CLAUDE.md`; procedures go in skills.
- **A file-specific constraint** ("migrations are append-only") → a **path-scoped rule** so it stays out
  of context during unrelated work.
- **A read-heavy side investigation** whose details you won't reference again → a **subagent** (it returns
  only a distilled summary; the raw exploration never enters your main context).
- **Keep `CLAUDE.md` under ~200 lines** and treat it as an index pointing to the above, not a manual.
  An unscoped rule is mechanically identical to `CLAUDE.md` content: always loaded, always costing tokens.

## How Keel maps onto this
- **Always-on discipline** (`rules.md`, `HANDOVER.md`, `LESSONS.md`, `TASKS.md`) → `@`-imported by `CLAUDE.md`.
- **Procedures** → skills: `/keel-handover`, `/keel-phase-review`, `/keel-research`, `/keel-adopt`, `/keel-distill`, `/keel-update`
  (pull the latest template with per-file approval), `/keel-audit` (rules-compliance spot-check when due),
  `/keel-plan` (phase map: status table + regenerated Mermaid DAG in `PLAN.md`).
- **Side tasks** → subagents: `researcher`, `verifier`, `auditor` (`.claude/agents/`).
- **Guarantees** → hooks (`block-dangerous`, `pre-compact-snapshot`, `session-start-reground`, handover
  reminder, `plan-phase-nudge`) + `settings.json` permissions.
- **File-local constraints** → optional `.claude/rules/` (see the example there).
