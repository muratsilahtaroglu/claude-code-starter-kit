# scratch/ layout audit — why a mature project leaves the template's taxonomy

_2026-08-18 · internal measurement · corpus: `alice_v2/scratch/`, a live multi-agent project.
The kit was NOT applied to that project from here — it is read-only evidence; the fixes land in the
template and reach it through `/keel-update`._

## Headline

| Metric | Value |
|---|---|
| `scratch/` subfolders | **56** (the template prescribes 4) |
| Cited by a permanent artifact | **54** — `reports/` notes, ADRs, docs, memory files |
| Files doing the citing | **83** |
| Uncited | **2 — `experiments/` and `one_off/`**, i.e. the template's own folders |
| Task-addressed folders (`co<n>/`, `denetim_*/`) | **39 of 56** |
| Scratch `.py` files carrying the §3.10 purpose comment | **211 / 211** |
| Most-cited | `kw_integrity` (10 files) · `co4` (10) · `co56` (7) · `ke1` (6) · `co_review` (6) |

## What the drift actually is

The template classifies scratch by **kind of activity** — `experiments/`, `probes/`, `one_off/`,
`archive/`. The project classifies by **work item** — `co43/`, `denetim_co58/`, `ke1/`. That is the
addressing `reports/team/<author>/<task>_*.md` and `TASKS.md` ids already use, so the tree answers the
question people actually ask ("where is the evidence for co56?") instead of one nobody asks ("which of
these was an experiment rather than a probe?").

The file-level discipline was never abandoned: **211 of 211** scratch scripts carry their §3.10
one-line purpose header. The drift is entirely in the folder layer — and it drifted *toward* the
kit's own addressing scheme, not away from it.

## The real defect: two kit rules that never met

- **§3.10** treats `scratch/` as disposable: at session end each file is module-ized, archived, or deleted.
- **§10.40** treats `reports/` as permanent: *"never deleted or moved — they are the artifacts other
  files cite."*

A report that records a measurement names the probe that produced it. At that moment the probe stops
being throwaway and becomes the evidence behind a permanent claim. **54 of 56 folders are in that
state.** Applying §3.10 literally would dangle citations in 83 permanent files — so the project had to
write a local rule to protect its scratch tree *from the kit's own `/keel-tidy`*, whose criterion was
file AGE (`git log -1 --format=%cs`).

Age is the wrong axis, and the project's own counter-example proves it: `r25/apostrof_probe.py`,
untouched for 18 days, was the independent measurement behind that week's apostrophe decision.

## Two measurement traps found while checking this

Both are recorded because the fix ships the grep commands:

1. **`\b` inside `grep -E` silently matches nothing.** The first citation sweep,
   `grep -rlE "scratch/$n(/|\b)"`, returned **0 of 56** — a clean, plausible, entirely false answer.
   This is the exact portability trap the kit's own `block-dangerous.sh` comment warns about; it still
   caught this measurement. (rules §10.37: a surprising measurement indicts the instrument first —
   0/56 was surprising enough to check, and the instrument was the culprit.)
2. **Path-only citation checks under-report.** With the regex fixed, `r25` still read as uncited:
   its citation is `reports/team/alice_co-agent/r25_go_smoke_2026-08-12.md` — the id is in the report's
   FILENAME, not in a `scratch/r25` path string. A dead-folder verdict needs both directions. Same
   shape as the ~54% basename false-staleness measured for LESSONS citations
   (`reports/2026-08-17-lessons-scope-audit.md`).

## What changed in the template

- `scratch/README.md` — rewritten around the disposable-vs-cited distinction; task-addressed folders
  documented as a first-class shape; both citation checks given as runnable commands.
- `rules.md §3.10` — the session-end sweep now exempts anything a permanent artifact cites, and states
  that `/keel-tidy` sweeps by citation, never by date.
- `/keel-tidy` — criterion changed from age to citation, with the filename fallback.

**Not changed:** the four stock subfolders stay. An earlier draft proposed dropping `experiments/` and
`one_off/` as dead weight, but the kit's own `one_off/` holds real content (the handbook build source,
git-ignored by design) — the evidence for that half of the proposal was one project deep, and it was
withdrawn.
