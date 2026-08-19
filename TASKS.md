# TASKS.md — cross-session task board (TEMPLATE)

> The single cross-session source of truth (built-in todos are session scratch). `@`-imported IN FULL
> every session — a lane heading is a WRITE boundary, not a context boundary, so every line here is
> paid by every session. Rules: `rules.md §9.32`. Full guide — ids, lanes, review states, ownership:
> **`docs/memory-files.md`**. Cap: `.claude/keel-caps`.
>
> - **Work ONLY from `## Now`** (max 3–5). Refill from `## Next` when it empties.
> - Every item carries a verifiable **`done-when:`** — weakening one to make a task pass is not allowed.
> - **Delete on done:** `[x]` immediately; `/keel-handover` deletes it as its one-liner lands in
>   HANDOVER (a). Git is the archive.
> - `## Discovered` is an INBOX: one line now, converge it OUT at handover/distill.
> - Ids are per-lane and stable (`co1`, `fro2`) — orchestrator-allocated, never renamed, never reused.
>
> This header is DOCTRINE. Anything dated, measured, or awaiting a decision goes in the BODY.

## Now (max 3–5 — the only section to work from)
- [ ] T1: <task> — done-when: <verifiable criterion>

## Next (prioritized backlog, short)
- [ ] T2: <task> — done-when: <criterion> (blocked-by: T1)

## Discovered (append one-liners mid-session; triage at session end)
- <YYYY-MM-DD> — <what was noticed> (discovered-from: T1)
