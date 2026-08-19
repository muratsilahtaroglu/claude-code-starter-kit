# scratch/ — exploration code (rules.md §3.10)

Never spread into the main source tree. **Every scratch file starts with a 1-line purpose comment** —
at the end of a session, no file is left unanswered for "what is this?".

## Two shapes, pick per project

**By kind** (default for un-tasked exploration): `experiments/` · `probes/` · `one_off/` · `archive/`.

**By work item** (task-driven projects): `scratch/<task-id>/` — `co43/`, `denetim_co58/`, `r25/`.
This is the same addressing `reports/team/<author>/<task>_*.md` and `TASKS.md` item ids already use,
so "where is the evidence for co56?" has one answer. Measured on a mature project: 56 scratch folders,
39 of them task-addressed, and it is the task-addressed ones the reports actually cite.

Both may coexist. What matters is not the taxonomy — it is the distinction below.

## Disposable scratch vs. CITED EVIDENCE

A probe stops being throwaway the moment a permanent artifact names it. `reports/` notes, ADRs and
`docs/` are permanent by rules §10.40 — never deleted; the only sanctioned move is the
`/keel-distill` sweep of a *closed* task's reports into `done/`, citations rewritten — so a
`reports/` note whose measurement says "probe: `scratch/co56/premise_check.py`" has made that probe
part of a permanent claim. Archiving or deleting it dangles the citation.

**Rule:** a scratch folder is archived/deleted **only if nothing cites it**:

```bash
n=co56   # the folder name
grep -rl "scratch/$n" reports/ docs/ *.md          # cited by PATH
grep -rl "$n" reports/ | head                       # …or by report FILENAME (r25 → r25_go_smoke_*.md)
```

Both directions matter: on the same project, one folder read as uncited by a path-only grep and was in
fact cited by a report whose *filename* carried its id. **Age is not evidence of deadness** — a probe
untouched for 18 days was the independent measurement behind a decision taken that week.

Uncited *is* the signal, though: the folders nothing referenced were the stock `experiments/` and
`one_off/`, not the task ones.

## Lifecycle

| State | Where it goes |
|---|---|
| Proved useful, belongs in the product | a module under `src/` + a `docs/architecture.md` row |
| Cited by a report / ADR / doc | **stays put** — it is that claim's evidence (§10.40) |
| Nothing cites it, no longer needed | `scratch/archive/<topic>/` (git-ignored) or deleted — git is the archive |
| Unclear what it even is | it violated the 1-line purpose rule; answer it or delete it |

`/keel-tidy` sweeps this folder by **citation, not by date**.

## What is committed

Most scratch content is git-ignored (`.md`, `.html`, `archive/`, `__pycache__/`, `*.out` — see
`.gitignore`); READMEs are kept. So a folder can be locally rich and nearly empty in the repo — that
is expected, and one more reason not to judge a probe by what git shows.
