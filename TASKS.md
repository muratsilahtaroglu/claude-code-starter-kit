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
> - Optional inline tags: `blocked-by: T3` · `discovered-from: T1` · `@owner` (see below).
> - **Ownership (multi-user projects).** An item may carry `@owner` (the owner's `git config user.name`).
>   Work ONLY unassigned items or ones owned by the CURRENT git user; an item tagged for someone else is
>   **surfaced, not done** — doing another person's assigned work is how parallel work collides. Single-user
>   projects leave the tag off and ignore this. Enforced where it bites most: `/keel-autopilot` STOPS at a
>   foreign-owned item, and the SessionStart hook warns when `## Now` is entirely someone else's.
>   On owner-run projects (`.claude/project-owner` exists) ASSIGNING the tags is the project owner's call;
>   developers complete + `[x]` their items and add `## Discovered` lines (docs/steering.md "Multi-user").
>   **Owner review:** a developer does NOT delete their finished item — at their handover it MOVES to a
>   `## Review` section (created on first use; `- [x] T7 ... (@dev) — evidence: <done-when result>`).
>   The OWNER verifies the done-when, then accepts (delete → owner's HANDOVER (a) as "reviewed") or
>   rejects (back to `## Now` with one reason line). Single-user projects: no such section, delete-on-done as above.

## Now (max 3–5 — the only section to work from)
- [ ] T1: <task> — done-when: <verifiable criterion>

## Next (prioritized backlog, short)
- [ ] T2: <task> — done-when: <criterion> (blocked-by: T1)

## Discovered (append one-liners mid-session; triage at session end)
- <YYYY-MM-DD> — <what was noticed> (discovered-from: T1)
