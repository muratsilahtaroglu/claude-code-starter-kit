# TASKS.md — cross-session task board (TEMPLATE)

> The repo-tracked task board (`@`-imported every session). Claude Code's built-in todos are **session
> scratch only** (ephemeral / machine-local) — this file is the single cross-session source of truth;
> mirror open items here before compaction/session end. Rules: `rules.md §9`.
>
> **Anti-bloat is the whole design (cap ~100 lines — team override via `.claude/keel-caps`, rules §10.40):**
> - **Work ONLY from `## Now`** (max 3–5 items). Refill it from `## Next` when it empties.
> - Every item carries a verifiable **`done-when:`** criterion (a test to run, an output to observe) —
>   not a vague description. It is unacceptable to remove or weaken a `done-when:` to make a task pass.
> - **Delete on done:** mark `[x]` the moment a task finishes; at `/keel-handover` the item is DELETED from
>   this file as its one-liner lands in the new `HANDOVER.md` block (a) — git history is the archive.
>   Done items never survive a handover.
> - Mid-session discoveries ("tests are broken", "this module needs a refactor") get ONE line in
>   `## Discovered` immediately — then return to your current task. Discovered is an INBOX, not
>   storage: at `/keel-handover` every line converges OUT (→ `## Next` with a done-when · docs ·
>   LESSONS · ADR · delete if resolved); the SessionStart hook flags lines older than ~a week.
> - Optional inline tags: `blocked-by: T3` · `discovered-from: T1` · `due: YYYY-MM-DD` (sprint
>   target — the SessionStart hook surfaces past-due dates) · `@owner` (see below).
> - **Ownership (multi-user projects).** An item may carry `@owner` (the owner's `git config user.name`).
>   Work ONLY unassigned items or ones owned by the CURRENT git user; an item tagged for someone else is
>   **surfaced, not done** — doing another person's assigned work is how parallel work collides. Single-user
>   projects leave the tag off and ignore this. Enforced where it bites most: `/keel-autopilot` STOPS at a
>   foreign-owned item, and the SessionStart hook warns when `## Now` is entirely someone else's.
>   On owner-run projects (`.claude/project-owner` exists) ASSIGNING the tags is the project owner's call;
>   developers complete + `[x]` their items and add `## Discovered` lines (docs/steering.md "Multi-user").
>   **AI co-agent sessions** (rules §10.42) follow the same discipline as teammates: their own
>   `### <name>` lane, edits only INSIDE their own items (no rituals/git/curation), delivery via `## Review`.
>   Structured roster: `/keel-agent-team-create` (owner-only charters) + `/keel-agent-team-start`
>   (per-chat identity, survives compaction via the session map).
>   **Owner review (file-first, four states — rules §10.40/41):** a developer does NOT delete their
>   finished item — at their handover it MOVES to a `## Review` section (created on first use), and the
>   line NAMES its evidence FILE: `- [x] T7 <what> (@dev) — evidence: reports/team/<@dev>/<task>_fix_<date>.md`.
>   A chat summary is not a delivery — the reground hook flags pathless lines and files missing on disk.
>   Review ROUTING is the owner/orchestrator's call alone; the mechanical half is delegated (verifier
>   subagent) and appends `— verified ✓ (owner part: <one sentence>)` to the line; the owner performs that
>   named step, then accepts (delete → owner's HANDOVER (a); index line → `closed <date> accepted`) or
>   rejects (back to `## Now` + one reason line; index back to `wip`). State chain + index format:
>   `reports/team/README.md`. Single-user projects: no such section, delete-on-done as above.

## Now (max 3–5 — the only section to work from)
- [ ] T1: <task> — done-when: <verifiable criterion>

## Next (prioritized backlog, short)
- [ ] T2: <task> — done-when: <criterion> (blocked-by: T1)

## Discovered (append one-liners mid-session; triage at session end)
- <YYYY-MM-DD> — <what was noticed> (discovered-from: T1)
