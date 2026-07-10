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
- **Verify what you touch.** The hooks have a runnable test pattern; the `.pth` CI scan must not
  false-fail on legitimate `.pth` files (e.g. `distutils-precedence.pth`, `coloredlogs`). Test before PR.

## How to propose a change
1. Fork + branch.
2. Make the change; keep the diff focused.
3. Fill in the PR checklist (`.github/PULL_REQUEST_TEMPLATE.md`).
4. Open a PR describing *what* and *why* (link an issue if there is one).

## Security posture
The supply-chain rules (`docs/security.md`, `rules.md §7`) are intentionally strict defaults. Proposals to
**relax** them need a rationale; proposals to **strengthen** them are welcome. Never include real secrets
in an example or test — see the secret-hygiene rules in `rules.md §5`.

By contributing, you agree your contributions are licensed under the project's [MIT License](LICENSE).
