# reports/team/ — per-author reports + the ONE index (TEMPLATE)

> Every report lives in its AUTHOR's folder — `reports/team/<@tag>/` for each developer, the owner,
> and every co-agent — task-prefixed names inside: `<task>_spec.md` (owner-approved spec + its
> `## Required reading` — 3–5 targeted artifacts the task needs: relevant ADRs, doc sections,
> scoped rules; the assignee reads THOSE, never the whole tree — + its `## Comprehension log`
> — + its **`## Premise`**: the claim the task rests on, in one line, and how it was MEASURED before
> any code was written; a CLASS-shaped task (a property that must hold everywhere) instead lists the
> SURFACES it covers, found by a search — that list is the done-when, rules §10.39/§10.41),
> `<task>_fix_<date>.md` (solution note: problem → root cause → fix + why →
> changed files → tests), bulky raw evidence as a `<task>_<what>/` subfolder. **Markdown only.**
> Reports are PERMANENT — never deleted: Review evidence, LESSONS, ADRs and path-scoped rules cite
> these paths (rules.md §10.40); findability lives here, in the index. ONE sanctioned move exists:
> when a task reaches `closed`, the `/keel-distill` sweep `git mv`s its files into the author's own
> **`done/`** subfolder and rewrites every citation in the same pass — so the flat folder shows only
> live work. Nothing else ever moves a report.
>
> **This README is the single index AND the team's review todolist** — one line per report,
> `file · task · what · status`, grouped by author (sections mirror the folders; the `/keel-distill`
> lint checks the mirror: every file exactly ONE line, no orphans, no duplicates). **A delivery
> exists only as its file:** a chat summary is not a delivery — the reground hook flags TASKS
> `## Review` lines whose evidence file is missing on disk.
>
> **Controlled status vocabulary (nothing else):**
> - `[ ] wip` — spec exists, work ongoing (a rework after a rejection returns here, dated)
> - `[ ] delivered` — solution note written; the item sits in TASKS `## Review`
> - `[ ] verified — owner part: <one sentence>` — mechanical review done (delegated verifier);
>   ONLY the named human step remains
> - `[x] closed <YYYY-MM-DD> refuted` — the premise did not hold and the measurement says so; the
>   delivery IS the refutation note (zero product lines). A RESULT, not a failure — it closes the
>   task and the assigner's claim is corrected, never quietly re-assigned (rules §10.41).
> - `[x] closed <YYYY-MM-DD> accepted` · `[x] closed <YYYY-MM-DD> rejected` — owner decided; the
>   line stays forever. "What's finished under @X?" = the `[x]` lines in @X's section. At the next
>   `/keel-distill` the files behind a closed line move to `<@tag>/done/` (the line keeps its
>   status; only its path changes).
>
> **Counting throughput** ("how many tasks did @X actually finish?"): the `[x] closed … accepted`
> lines in @X's section — that is the delivery record. The task-id PREFIX (`co3`, `fro7`) says which
> lane the work was OPENED for, which is usually the same person but is not the record: a reassigned
> item keeps its original id (renaming would dangle every citation, §10.40). Count with `grep -w` —
> `co1` is a prefix of `co19`, so a bare grep over-counts.
>
> **Who flips what:** the AUTHOR appends the line and advances it to `delivered`; the ORCHESTRATOR
> (owner's main session / leader agent) flips `verified` and `closed` — one writer per transition.
> Same-machine AGENT teams (rules §10.42 write-surface split): the ORCHESTRATOR writes ALL
> transitions here, syncing from each worker's `board.md` — workers never edit this index
> (humans on their own machines still append their own lines; git merges them).

## @<owner-tag> (one `##` section per author folder — add yours when the folder is born)
- [ ] `<task>_fix_<date>.md` · T7 · <one line: what it delivers> · delivered
