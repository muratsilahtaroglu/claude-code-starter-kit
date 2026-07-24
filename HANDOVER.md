# HANDOVER.md — Session handover, block-rotated (TEMPLATE)

> Updated BEFORE every compact/session end. The repo is durable disk; the context window is volatile
> RAM — anything not written here is assumed lost. This file is `@`-imported into EVERY session, so it
> has a **hard cap: max 3 session blocks / ~150 lines.** When a 4th block would be added (or the cap is
> hit), run **`/keel-distill`** first: the oldest block's critical facts go to `LESSONS.md` (tagged, distilled)
> and the raw block moves verbatim to `docs/handover-archive.md` (never imported — costs no context,
> grep-able forever). Compaction is a curation step, not an information-loss event.

_Last updated: <YYYY-MM-DD> — <short status>._

---

## Session blocks (newest first — a fresh session reads the TOP block first)
<!-- Insert each new session block HERE, directly below this comment (newest first; older blocks get
     pushed down). ONE BLOCK PER SESSION, not per day: the heading carries HH:MM, so several same-day
     sessions stay separate; a /keel-handover re-run in the SAME session updates its own block (keeping
     its original time). Max 3 blocks — then run /keel-distill. On the FIRST real session, REPLACE the
     placeholder block below (don't stack a real block on top of it, or the phantom placeholder lingers
     forever). -->

### <YYYY-MM-DD HH:MM> — <one-line status>   <!-- ← REPLACE this whole placeholder block on the first session -->
- **(a) Completed:** <what was done, briefly>. (Details/decisions → ADR / docs; done TASKS.md items land here as one-liners.)
- **(b) Tried, didn't work (don't retry):** <approach> — FAILED, reason: <...>. (Highest-value lines — never lost: `/keel-distill` moves them to `LESSONS.md [fail]`, not to the trash.)
- **(c) Latest updates:** <most recent changes>
- **(d) Next steps:** <what to do next session, in priority order>

---

## Open questions / pending user decisions
<!-- GLOBAL section — survives rotation untouched until each item is resolved (then delete it). -->
- <topics awaiting a decision>

---

## Scaling: per-area handovers (optional)
**Default: this single root file.** On a **large, multi-area** project (e.g. backend + frontend +
agent/LLM) it can grow noisy — then, when an area is developed in its own sessions, give it a
**per-area handover** next to its code (`backend/HANDOVER.md`, `frontend/HANDOVER.md`,
`agents/HANDOVER.md`), each with its own session blocks + the same 3-block cap. In that setup:
- this **root** file becomes the **program-level index**: milestones, cross-area/integration decisions,
  and the links below. **One "latest" per area — no duplicated truth.**
- pair each with a nested **`<area>/CLAUDE.md`** that `@`-imports its `<area>/HANDOVER.md`; Claude Code
  auto-loads a subtree's `CLAUDE.md` when working there, so the right memory comes in automatically.
- **the AI creates a per-area handover when an area starts needing its own**, and **MUST register the
  structure in `docs/architecture.md`** (+ wire the nested `CLAUDE.md` `@`-import). Start with one file;
  split only when it hurts.

**Per-USER variant (teams):** when ≥~4 people write concurrently, the same valve applies per user —
`handovers/HANDOVER-<user>.md` (same block format + 3-block cap), this root file as the index (one
"latest" per person, no duplicated truth). Never split LESSONS per user — sign lines with your `@tag`
instead (docs/steering.md "Multi-user").

### Area handovers (index)
- <area> → `<area>/HANDOVER.md` — <one-line status>  <!-- add rows only when you actually split -->
