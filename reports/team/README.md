# reports/team/ — per-author reports + the ONE index (TEMPLATE)

> Every report lives in its AUTHOR's folder — `reports/team/<@tag>/` for each developer, the owner,
> and every co-agent — task-prefixed names inside: `<task>_spec.md` (owner-approved spec + its
> `## Comprehension log`), `<task>_fix_<date>.md` (solution note: problem → root cause → fix + why →
> changed files → tests), bulky raw evidence as a `<task>_<what>/` subfolder. **Markdown only.**
> Reports are PERMANENT — never deleted, never moved: Review evidence, LESSONS, ADRs and path-scoped
> rules cite these paths (rules.md §10.40); findability lives here, in the index.
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
> - `[x] closed <YYYY-MM-DD> accepted` · `[x] closed <YYYY-MM-DD> rejected` — owner decided; the
>   line stays forever. "What's finished under @X?" = the `[x]` lines in @X's section.
>
> **Who flips what:** the AUTHOR appends the line and advances it to `delivered`; the ORCHESTRATOR
> (owner's main session / leader agent) flips `verified` and `closed` — one writer per transition.

## @<owner-tag> (one `##` section per author folder — add yours when the folder is born)
- [ ] `<task>_fix_<date>.md` · T7 · <one line: what it delivers> · delivered
