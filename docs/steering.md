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
  `/keel-pilot` (staged bulk-run gate: declare thresholds → smoke → gold-set validation → ramp → acceptance),
  `/keel-autopilot` (gated autonomy for one session: phases advance back-to-back, every gate still runs the
  full `/keel-phase-review` with real evidence, commits are local, pushes batch for ONE approval).
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

## Headless `claude` calls from inside the repo (trap)
A script or LLM-provider that shells out to the `claude` CLI **with cwd inside the project** (benchmark
runners, LLM judges, batch jobs) starts a FULL Claude Code session per call: SessionStart hooks fire
(`.claude/ritual-log` fills with `session-start startup` lines), and `CLAUDE.md` + its `@`-imports
(~500 lines of constitution) load into EVERY call — per-call token cost, plus the callee model reads
your project rules (judge-bias risk in eval pipelines). Run such calls from a neutral cwd outside the
repo; a burst of same-minute `session-start startup` lines in the ritual-log is the telltale.

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

## Multi-user: owner vs developers (optional — off by default)
Single-user projects: skip this — no file, zero cost. When helpers join, the FOUNDER declares ownership
by writing **`.claude/project-owner`** (one line: the owner's `git config user.name`; a bootstrap run by
someone else ASKS who the owner is, never assumes). Roles from then on:
- **Owner (founder)** — the only one who changes GOVERNANCE: `PLAN.md` (the plan itself + assignments),
  `rules.md`, `CLAUDE.md`, `docs/architecture.md`, ADRs, `.claude/` config. Assigns work by tagging
  TASKS items `(@name)` / the PLAN `owner` column, then pushes.
- **Developers** — pull, work ONLY their `@name` (or unassigned) items, mark them `[x]`, add
  `## Discovered` lines, write their own HANDOVER blocks (headings carry `@<git user.name>`), append
  LESSONS. Their sessions: the re-ground hook prints the role line; `/keel-autopilot` STOPS at
  foreign-owned items; the **`owner-guard` hook BLOCKS governance edits** (exit 2, propose-to-owner
  message). Ritual surfaces stay shared — a session that cannot write HANDOVER/LESSONS/TASKS cannot
  run the discipline at all.
- **Review loop (owner verifies developer work)** — a developer's finished item is MOVED, not deleted,
  to a TASKS `## Review` section at their handover (`- [x] ... (@dev) — evidence: <done-when result>`).
  The owner's next session is nudged by the re-ground hook, verifies the `done-when` (run/observe it;
  verifier agent for adversarial doubt, rules.md §4.11), then **accepts** (delete → owner's HANDOVER (a)
  as "reviewed") or **rejects** (back to `## Now`, one reason line, still @-tagged). Phase grain needs no
  extra machinery: PLAN.md is governance, so a developer cannot flip a phase — the owner flips it after
  reviewing the gate evidence.
Enforcement honesty (layered): the hook stops the AI *drafting* foreign governance edits — the
accidental collision. The wall for intentional human edits is the HOST: branch protection + PRs the
owner reviews (rules.md §6 / CONTRIBUTING) — every developer change lands through the owner anyway.

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

**If a full clone double-fires anyway** (the `session-start-reground` double-fire detector flags it — see
the ritual-log for same-second identical lines): the plugin is enabled at **user scope**
(`~/.claude/settings.json` `enabledPlugins`) and its hooks fire in the clone too. A project-scope
`enabledPlugins:{"keel@keel":false}` *should* override per settings precedence — but a plugin whose hooks
load **before** the enable-filter (notably a stale/`failed to load` cache, e.g. an old 0.8.x pin) fires
its hooks regardless of the flag. Resolution, in order: (1) try `.claude/settings.local.json` (Local
scope, higher precedence, git-ignored) with the same `false`, then start a **fresh session**
(`enabledPlugins` is read at session start, not hot-reloaded); (2) if hooks still fire, the stale plugin
cache is the culprit — update it (`/plugin` → update) or remove the plugin at user scope. **A full clone
and the plugin are mutually exclusive** — pick one per project; the clone is self-contained, the plugin
is for non-clone projects.
