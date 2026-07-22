# docs/architecture.md — Live Architecture Map (TEMPLATE)

> Updated on every structural change. What each significant file/module does. Status: ✅ exists · 🟡 skeleton · ⬜ planned.
> The **module map table is the source of truth** — when its rows change, resync the component overview
> diagram in the same edit (same contract as PLAN.md's table → diagram; appending rows while the top
> diagram rots is the documented failure mode — the SessionStart hook warns when the whole file lags the code).

## Component overview
```
<text diagram: client → API → service/worker → database/external services>
```

## Module map
| Module / file | Status | Purpose |
|---|---|---|
| `<path>` | 🟡 | <what it does> |

## Reused patterns
- <which off-the-shelf pattern/from where> → <how it's used here>

## Runtime prompts (LLM apps only — omit for non-LLM projects)
Prompts the app sends at runtime, kept as versioned files under `src/` and read from disk (never
embedded as strings): <list>.
