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
| **`.mcp.json`** (repo root) | **External tool bridges** (MCP servers: DB, browser, internal APIs) — project-level, git-tracked | approved servers at session start | ✅ config on disk | tool access |

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
  `/keel-plan` (phase map: status table + regenerated Mermaid DAG in `PLAN.md`), `/keel-compact`
  (pre-compact bundle: refresh the disk via `/keel-handover`, verify freshness, hand off to `/compact`),
  `/keel-pilot` (staged bulk-run gate: declare thresholds → smoke → gold-set validation → ramp → acceptance).
- **Side tasks** → subagents: `researcher`, `verifier`, `auditor` (`.claude/agents/`).
- **Guarantees** → hooks (`block-dangerous`, `compact-gate` (blocks a stale manual `/compact`),
  `pre-compact-snapshot`, `session-start-reground`, handover reminder, `plan-phase-nudge`) +
  `settings.json` permissions. Plus `ritual-log` telemetry: every Skill-tool invocation, every
  user-typed command (built-ins included, via `UserPromptExpansion`), compact boundary
  (manual/auto), session start and hook BLOCK is appended to `.claude/ritual-log` (git-ignored,
  self-trimmed). **`/keel-stats`** renders it into `reports/ritual-stats.md` — PLAN.md-style
  colored Mermaid interval boxes + a counts table.
- **File-local constraints** → optional `.claude/rules/` (see the example there).

## Auto memory vs Keel memory
Claude Code also keeps an **auto memory** per project (`~/.claude/projects/<project>/memory/` —
`MEMORY.md` index + topic files, on by default): the assistant's own private notes. It is
**machine-local** — it never enters git, so teammates and CI never see it. Division of labor:
auto memory = one person's scratch recall; **anything the team must know goes to `LESSONS.md` /
`HANDOVER.md`** (git-shared, `@`-imported, cap-controlled). A team-relevant lesson that lives only
in one machine's auto memory is a lesson the team does not have.

## MCP (external tool servers)
The kit ships **no MCP servers** — the discipline layer needs none (files + bash + hooks cover it).
MCP itself is often essential (semantic search, vLLM endpoints, DB bridges…); what Keel standardizes
is **where each server lives**, by who needs it:

| Who needs the server | Where it goes | Why |
|---|---|---|
| **Only this project** (its own DB/API) | **root `.mcp.json`** (rules.md §5.13) | git-tracked, reviewed like config, teammates get it with the repo |
| **You, in every project** (your personal toolbelt) | `claude mcp add --scope user` | written ONCE into your user config, available machine-wide — never re-written per project |
| **A team / several machines**, versioned | a small personal **MCP plugin** in your own marketplace (same pattern as keel's) | one `/plugin install` (or the auto-install keys below) distributes + updates the whole set centrally |

So "rewriting the same MCP config in every project" is the one option that should never happen.
The plugin-bundled variant (an `.mcp.json` at a plugin's root, as drawn in ecosystem diagrams) is that
third row — *distribution*, not project config. Agent Teams and observer agents remain experimental:
watch, don't build on them.

## Team auto-install of the keel plugin
On a **plugin-only** team project (tooling via plugin, no full clone), commit these two keys to the
project's `.claude/settings.json` so everyone who opens the repo gets the tooling registered and
enabled automatically — no per-person `/plugin marketplace add` + `/plugin install`:
```json
{
  "extraKnownMarketplaces": {
    "keel": { "source": { "source": "github", "repo": "muratsilahtaroglu/claude-code-starter-kit" } }
  },
  "enabledPlugins": { "keel@keel": true }
}
```
Never add this to a **full clone** of the kit: the clone already registers the same hooks via
`.claude/settings.json`, and plugin + settings registration together fire each hook **twice**
(the dual-registration trap above).
