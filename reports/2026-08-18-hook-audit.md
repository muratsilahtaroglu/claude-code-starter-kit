# Hook security audit — three shipped bypasses and the missing regression floor

_2026-08-18 · external audit (independent session) + verification and extension in this session ·
subject: `.claude/hooks/block-dangerous.sh`, `owner-guard.sh`, `session-start-reground.sh`._

## Headline

| | |
|---|---|
| Findings raised by the audit | 10 |
| Confirmed by re-running them here | 9 |
| Corrected (mechanism right, numbers wrong) | 1 |
| Rejected outright | 0 (one re-argued — see "dev.txt") |
| Additional bypasses found in the same classes | **3** |
| Committed hook tests before this audit | **0** |
| Committed hook tests after | **141** |

The root cause is a single sentence: **every hook matrix was run in a session and thrown away.**
`git log --diff-filter=A -- 'tests/**'` returned only READMEs across 77+ commits, while eleven
commit messages claim a verified matrix ("40-case matrix green", "22-case matrix (9 gate + 13
block-dangerous incl. regressions) all green", "16-case tested"). The verifications were real —
they were re-run and reproduced here — but volatile. A moment was proven; nothing was protected.
The three bypasses below are precisely what a committed matrix would have caught and kept caught.

## 1. `block-dangerous.sh` — recursive-delete guard (rule 1)

The guard required the recursive FLAG and the catastrophic TARGET to be adjacent:

```
[[:space:]]-[a-zA-Z]*[rf][a-zA-Z]*[[:space:]]+(/|~|\$HOME|\.)[/*]*([[:space:]]|$)
```

Two independent consequences, six commands through the wall:

| Command | Why it passed | Effect |
|---|---|---|
| `rm -rf *` | `*` was not in the target alternation at all | wipes cwd |
| `rm -rf ./*` | same | wipes cwd |
| `rm -rf **` | same | wipes cwd |
| `rm -rf .*` | same | wipes dotfiles, `.git` included |
| `rm -rf .[!.]*` | same — and this is the idiom people reach for *because* it looks careful | same |
| `rm -rf -- /` | `--` sits between flag and target, breaking adjacency | root |
| `rm -rf --no-preserve-root /` | same, and it disarms `rm`'s own last-resort guard | root |
| `rm --recursive --force /` | long-form flags never matched the flag pattern | root |

The hook's own comment claimed coverage of "root / home / cwd" — the cwd half was aspirational.

**Fix.** Flag and target are matched independently, per shell segment, over the argument list only.
A catastrophic target is a standalone token (`/ // /* ~ ~/ ~/* $HOME . ./ ./* * ** .* .[!.]*`),
never a scoped path (`./build`, `/srv/app`, `~/proj/x`) nor a filtered glob (`*.log`, `build/*`).

**The fix's own first attempt was wrong** and the matrix caught it: matching an `rm` token anywhere
blocked `docker build --rm -f Dockerfile .` and `git rm -r --cached .` — both everyday commands. A
guard that nags on normal work gets switched off, which costs more than the bypass it closed. `rm`
is now required in COMMAND position (segment start, optionally behind `sudo`/`command`/`time`).
Both cases are permanent ALLOW rows in the matrix.

## 2. Force push — one blind spot in two independent walls

`git push origin +main` passed **both** `block-dangerous.sh` rule 2 (which exists to stop force
pushes) and `owner-guard.sh` (which exists to stop non-owner pushes to main). A leading `+` on a
refspec is git's own short form for `--force`; neither wall knew it.

Refinement of the audit's claim: `+refs/heads/main` was already blocked by owner-guard (its
`/main` matched the branch pattern) and passed only in `block-dangerous`. The shared blind spot is
the short `+main` form.

**Fix.** `block-dangerous` treats `[[:space:]]\+<ref>` as force (so `+topic` is caught too);
owner-guard adds `+` to the character class preceding `main|master`.

## 3. `owner-guard.sh` — the governance wall was a string comparison

`case "$rel"` over a prefix-stripped string is not a path comparison. Through the wall:
`./rules.md`, `docs/../rules.md`, `./docs/adr/0001-x.md`, `src/../PLAN.md`, and any absolute form
carrying a `..`. `.claude/hooks/../rules.md` *was* blocked — by accident, matching the
`.claude/hooks/*` glob rather than the file it names.

**Fix.** The path is normalised textually (`os.path.normpath` + `relpath`, no symlink resolution)
before the match, so a file that does not exist yet — a `Write` creating a new ADR — is still
caught. Fails open to the raw form if `python3` is unavailable, matching the JSON reader above it.

This wall remains AI-side only, as the file has always stated: a plain terminal bypasses any hook.

## 4. `session-start-reground.sh` — `## Review` section parsing

Two ranges read the same section with different terminators: `/^## Review/,/^## /` for the queue
counter and `/^## Review/,/^## Next/` for the evidence checks. TASKS.md section order is not fixed
(`## Review` is documented as "created on first use", with no stated position), so the second form
runs to EOF whenever Review sits after Next and swallows every later section.

Measured over all 24 orderings: **12 mis-parse**, producing up to 3 phantom "carries NO evidence"
warnings. Correction to the audit: the **queue counter is not affected** — it already used the
robust form. Only the evidence checks break.

The same class was present in two more places the audit did not name: the ownership warning and
the due-date nudge both used `/^## Now/,/^## Next/`, so a board without a `## Next` section, or
with one placed first, scanned unrelated sections.

**Fix.** One `section()` helper — "stop at the next `## ` heading, whatever it is" — used by every
section read (Now · Review · Index · Now|Review). `### <lane>` subheadings are preserved.

## 5. Everything else

| Finding | Status | Action |
|---|---|---|
| `.claude/hooks/hooks.json` is a dead plugin-era registry | confirmed (12 `${CLAUDE_PLUGIN_ROOT}` entries; plugin retired in v0.8.23) | deleted; matrix asserts it stays gone |
| The kit records its own 8 hooks / 17 skills nowhere: `docs/architecture.md` is the stock TEMPLATE and the doc-drift detector skips `(TEMPLATE)` files | confirmed, with a correction | the template STAYS blank — it belongs to the downstream project, and the detector skipping it is right. The kit's own inventory belongs in per-folder READMEs, which did not exist: `.claude/hooks/README.md` and `.claude/skills/README.md` written, and the repo-map footer that already promised them corrected |
| Cap comment documents `TASKS=300`; code uses `cap_T=100` | confirmed | comment corrected; matrix asserts comment ↔ code |
| `rules.md` at 298/300 — §10.38 promises a template keeps headroom | confirmed | no rule text was added by this batch |
| `reports/ritual-stats.md` regenerable but untracked and un-ignored | confirmed | gitignored |
| `requirements/dev.txt` is all comments → `make test` fails on a fresh clone | mechanism confirmed, **reasoning corrected** | the placeholders are deliberate template design (§7.20 teaching `==` pinning); the real defect is that the kit now ships a test suite, so `pytest` is pinned for real. `dev.lock` still needs a `pip-compile` run — CI installs the pin inline instead, matching the existing `pip-audit==2.7.3` step |

## Verification

```
before fixes:  30 failed, 103 passed
after fixes:   141 passed
```

Every bypass row in `tests/unit/test_keel_hooks.py` is marked `AUDIT-2026-08-18` and failed before
its fix. The suite also asserts the properties that let these ship: every hook file is registered
in `settings.json`, every hook is executable and parses, no plugin-era registry exists, and the
documented cap defaults equal the coded ones.

## What this changes about how the kit works

Ad-hoc verification and committed verification are not the same claim, and the kit's own §2.8 says
so. A commit message asserting "40-case matrix green" is a report about a session; a test file is
a property of the repository. The kit had been writing the first and calling it the second.
