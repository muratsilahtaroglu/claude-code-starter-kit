# CLAUDE.md — <PROJECT NAME> project constitution (TEMPLATE)

> Claude Code reads this first every session. The four `@`-imports below auto-load the working rules,
> the running handover, the lessons database, and the task board — always in context, re-injected from
> disk after every compaction. Keep this file lean (< ~200 lines); push sometimes-relevant knowledge
> into `.claude/skills/` and deterministic checks into `.claude/hooks/`. Fill in the `<...>` blanks.

@rules.md
@HANDOVER.md
@LESSONS.md
@TASKS.md

## Session protocol (rules.md §9)
- **Start:** read the TOP block of `HANDOVER.md` + `LESSONS.md` + `TASKS.md ## Now` + recent `git log`;
  pick ONE `## Now` item; verify tests pass before new work.
- **During:** the moment a rule / must-run test / gotcha / failed approach is agreed or discovered — ask
  "shall I note this?" and append it to `LESSONS.md` immediately (don't wait for compaction).
- **End (or before compact):** `/keel-handover` (new HANDOVER block) · delete done TASKS items · commit with
  approval. If any memory file exceeds its cap → `/keel-distill`. About to compact manually? Run
  `/keel-compact` — it bundles all of the above, verifies freshness, then hands off to `/compact`.
- **When compacting, always preserve:** the list of modified files, open `TASKS.md ## Now` items, test
  commands, and any agreement not yet written to `LESSONS.md` (write it there first).

## What we're building
<Purpose of the project in 2-3 sentences. What problem it solves, who uses it.>

## Architecture (summary)
<Components and how they talk to each other. E.g.: API (FastAPI) + Worker + DB + Vector DB + LLM. A text diagram.>

## Key decisions (ADRs in `docs/adr/`)
- <ADR-0001: ...>
- <ADR-0002: ...>
(Every significant technical decision becomes an ADR; copy `docs/adr/0000-adr-template.md`.)

## Stack & versions
<Languages, frameworks, libraries — with exact versions (rules.md §7: pinning).>

## Configuration
NO hard-coding. Secrets + machine-local values come from `.env` (key list: `.env.example`); non-secret
parameters from `config/<env>.yaml` selected by `ENV` (see `config/README.md`).

## Commands
```bash
<setup / run / test / migration commands — also wired into the Makefile>
```

## Conventions
- **All application code lives under the source tree** (`src/<app|package>/` per `docs/layouts.md`) —
  never loose at the repo root; the root holds only the discipline/config scaffold. New modules → `src/`.
- Runtime LLM prompts (LLM apps only) live in versioned files under `src/` and are read from disk —
  code never embeds prompt strings. (Prompts that steer *Claude Code* go in `.claude/skills/` or `.claude/agents/`, not here.)
- Reusable Claude Code workflows live in `.claude/skills/<name>/SKILL.md` (e.g. `/keel-handover`, `/keel-phase-review`).
- Side tasks that would clutter the thread run as subagents in `.claude/agents/` (e.g. `researcher`,
  `verifier`). Which mechanism for what (skill vs subagent vs rule vs hook) → `docs/steering.md`.
- Throwaway/experimental code only in `scratch/<subfolder>/`, with a 1-line purpose comment at the top.
- Every structural change → `docs/architecture.md`. Every phase end → docs + HANDOVER.md (approved commit+push).
- Tests live in `tests/{unit,integration,e2e,fixtures}/`. Detailed rules: `rules.md`.
- Enforcement lives in `.claude/`: `settings.json` permissions + `hooks/` (block dangerous/secret commands,
  handover reminder, pre-compact snapshot, session-start re-ground). Rules are guidance; hooks/permissions
  are enforced.

## Directory map
See `docs/architecture.md` (live module map).
