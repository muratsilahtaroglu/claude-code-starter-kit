# Claude Code Project Template (Starter Kit)

*A discipline + security starter kit that keeps Claude Code (or any LLM) building your project
consistently, traceably, and safely — from the very first session.*

**Requires:** [Claude Code](https://claude.com/claude-code). The `.claude/` layer (permissions, hooks,
skills) is Claude-Code-native; the docs and discipline (`rules.md`, ADRs, `HANDOVER.md`, security guide)
are tool-agnostic and useful with any agent.

## Quick start
```bash
# 1) copy the template (incl. dotfiles) into your new project's root
cp -a _project_template/. my-project/ && cd my-project
# 2) in Claude Code, let it tailor the template to THIS project before coding:
#    "Read CLAUDE.md, then run the bootstrap: prune what this project doesn't need and plan."
```
Then follow **How to use** below. Not every project needs the whole template — the bootstrap prunes it
to fit (with your approval).

> **Purpose:** When starting a new project (you or your teammates), give Claude Code this folder as a
> **template**. The generic "working discipline" files inside help set up the project from day one as
> **professional, traceable, and secure**. No file contains a project name or project-specific detail —
> fill in the placeholders.

## How to use
1. Copy the contents of this folder into the root of the new project.
2. **Bootstrap tailoring (rules.md §0.0):** have the AI first *understand the project*, then propose
   (a) which template parts are unnecessary for this project and should be removed (with reasons), and
   (b) which layout profile from `docs/layouts.md` (ML, service/API, CLI, ...) to instantiate.
   **Nothing is removed or added without user approval.** Not every project needs the whole template.
3. Fill in the `<...>` placeholders in `CLAUDE.md`, `.env.example`, and `docs/architecture.md`.
4. Choose and add a `LICENSE` before the first push (a folder with no license is "all rights reserved").
5. Tell Claude Code: *"First read CLAUDE.md, then plan."* (CLAUDE.md `@`-imports `rules.md` + `HANDOVER.md`.)
6. Follow the discipline in `rules.md` and proceed in phases; update docs + `HANDOVER.md` at the end of
   each phase, then commit + push with approval.

## Contents (all generic / project-agnostic)
```
CLAUDE.md              # project constitution template (@-imports rules.md + HANDOVER.md)
rules.md               # working rules: documentation discipline, testing, scratch layout,
                       #   sub-agent verification, GitHub push, supply-chain security
HANDOVER.md            # cumulative session handover (done/tried-failed/latest/next)
user_manual.md         # end-user guide skeleton
LICENSE                # MIT
CONTRIBUTING.md        # how to contribute to the template itself (vs rules.md = building with it)
.claude/settings.json  # permissions (deny .env/secrets, ask before push) + hook registration
.claude/hooks/         # block-dangerous.sh (rm -rf/force-push/.env/pipe-to-shell) + handover reminder
.claude/skills/        # invokable workflows: /handoff, /phase-review, /research
.gitignore             # secrets + python/node/docker + .claude/settings.local.json
.env.example           # generic example (secrets stay in .env)
.editorconfig          # charset/newline/indent baseline
pyproject.toml         # tool config only: ruff (incl. security lint) + pytest
docs/architecture.md   # live module map template
docs/security.md       # supply-chain security guide (pin/hash/non-root/.pth/CI)
docs/layouts.md        # per-project-type source layout profiles (ML, service/API, CLI)
docs/adr/               # architecture decision records (template + index)
config/                # non-secret parameters per env (local.yaml/prod.yaml; secrets stay in .env)
prompts/ reports/ scratch/ tests/   # organized folder layout + READMEs
research/              # opt-in external research trail (github/articles/linkedin/huggingface/web → findings.md)
Makefile               # runnable setup/test/lint/run targets
.pre-commit-config.yaml # pre-commit secret scan (gitleaks) + .env guard + hygiene hooks
requirements.txt / requirements.lock          # pinned + hash-locked runtime deps skeleton
requirements-dev.txt / requirements-dev.lock  # dev tooling, kept out of the prod image
Dockerfile / .dockerignore / docker-compose.yml  # multi-stage non-root container + compose skeleton
.github/workflows/ci.yml           # hash-verify + pip-audit + .pth scan on every PR/push
.github/PULL_REQUEST_TEMPLATE.md   # Definition-of-Done checklist (mirrors rules.md)
```

## Philosophy (why this discipline?)
- **Fit the project, don't force the template:** the bootstrap step (rules.md §0.0) prunes unneeded
  parts and instantiates the right layout profile — always with user approval.
- **Traceability:** every decision goes into an ADR, every structural change into `architecture.md`,
  every session into the handoff. The project stays stable even after 10+ compactions.
- **Order:** throwaway code stays in `scratch/`, the main tree stays clean.
- **Security from day one:** dependency pinning + hashing + non-root + secret hygiene from the start.
- **Enforced, not just advised:** the discipline is wired into Claude Code's native layer — `.claude/`
  permissions deny reading secrets, hooks block dangerous/secret-leaking commands, and `@`-imports keep
  the rules + handover in context every session. Rules are guidance; hooks/permissions are enforced.
- **Controlled progress:** phases are not skipped; each phase ends with a working product + an
  approved commit/push.
