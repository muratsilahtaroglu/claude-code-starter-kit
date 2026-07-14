# TASKS.md — cross-session task board (TEMPLATE)

> The repo-tracked task board (`@`-imported every session). Claude Code's built-in todos are **session
> scratch only** (ephemeral / machine-local) — this file is the single cross-session source of truth;
> mirror open items here before compaction/session end. Rules: `rules.md §9`.
>
> **Anti-bloat is the whole design (cap ~100 lines):**
> - **Work ONLY from `## Now`** (max 3–5 items). Refill it from `## Next` when it empties.
> - Every item carries a verifiable **`done-when:`** criterion (a test to run, an output to observe) —
>   not a vague description. It is unacceptable to remove or weaken a `done-when:` to make a task pass.
> - **Delete on done:** mark `[x]` the moment a task finishes; at `/keel-handover` the item is DELETED from
>   this file as its one-liner lands in the new `HANDOVER.md` block (a) — git history is the archive.
>   Done items never survive a handover.
> - Mid-session discoveries ("tests are broken", "this module needs a refactor") get ONE line in
>   `## Discovered` immediately — then return to your current task. Triage Discovered at session end.
> - Optional inline tags: `blocked-by: T3` · `discovered-from: T1`.

## Now (max 3–5 — the only section to work from)
- [ ] T1: <task> — done-when: <verifiable criterion>

## Next (prioritized backlog, short)
- [ ] T2: <task> — done-when: <criterion> (blocked-by: T1)

## Discovered (append one-liners mid-session; triage at session end)
- <YYYY-MM-DD> — <what was noticed> (discovered-from: T1)
