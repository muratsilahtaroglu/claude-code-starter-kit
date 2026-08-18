# Contributing to this template

Thanks for improving the starter kit! This file is about changing **the template itself** — not about
projects built *with* it (that discipline lives in `rules.md`).

## Ground rules
- **Keep it right-sized.** This template's value is being disciplined *without* bloat. New additions must
  earn their place — prefer sharpening what's here over adding files. Cargo-cult welcome-mat files
  (CODEOWNERS, issue-template suites, etc.) will be declined.
- **Generic, not project-specific.** No project names, private paths, or personal config — everything
  stays a placeholder or a reusable convention.
- **Cross-reference consistently.** If you add / rename / remove a part, update every `.md` that mentions
  it (README contents list, `CLAUDE.md`, `docs/*`, `rules.md`) so nothing dangles.
- **Verify what you touch — in a COMMITTED test, not a session.** Hook changes go in with a row in
  `tests/unit/test_keel_hooks.py` (142 cases; `pytest tests/unit/test_keel_hooks.py -q`, also run by
  CI). This is not ceremony: three security bypasses shipped while commit messages claimed "40-case
  matrix green", because every one of those matrices was run by hand and thrown away
  (`reports/2026-08-18-hook-audit.md`). An ad-hoc probe proves a moment; a committed case protects a
  regression. Add BOTH directions — what must block, and the everyday command that must NOT (the fix
  for those bypasses first blocked `docker build --rm -f Dockerfile .`, and only the matrix caught it).
  The `.pth` CI scan must likewise not false-fail on legitimate `.pth` files (e.g.
  `distutils-precedence.pth`, `coloredlogs`).
  When testing hooks by hand, keep trigger strings OFF the command line — a payload containing e.g. a
  staging-a-dotenv command trips the session's own `block-dangerous` hook (it string-matches your Bash
  call, quotes included; seen in three real projects). Write payloads to files and pipe them:
  `bash hook.sh < payload.json`.

## How to propose a change
1. Fork + branch.
2. Make the change; keep the diff focused.
3. Fill in the PR checklist (`.github/PULL_REQUEST_TEMPLATE.md`).
4. Open a PR describing *what* and *why* (link an issue if there is one).

**`main` is maintainer-only.** Direct pushes are restricted to the repository owner (branch ruleset:
PR required, force-pushes and deletion blocked) — every contribution lands through a reviewed PR.

## Security posture
The supply-chain rules (`docs/security.md`, `rules.md §7`) are intentionally strict defaults. Proposals to
**relax** them need a rationale; proposals to **strengthen** them are welcome. Never include real secrets
in an example or test — see the secret-hygiene rules in `rules.md §5`.

By contributing, you agree your contributions are licensed under the project's [MIT License](LICENSE).
