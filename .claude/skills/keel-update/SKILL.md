---
name: keel-update
description: Pull the latest Keel template improvements into THIS project — kit tooling in one reviewed batch, likely-tailored files hunk-by-hunk; only approved hunks are applied. Never touches project memory (HANDOVER/LESSONS/TASKS) or project-owned files (src/, CLAUDE.md, ADRs).
---

# /keel-update — sync this project with the latest Keel template

Use when the kit was **cloned** a while ago and the template has since improved (hardened hooks, doc
fixes, workflow updates). Pull model: run it IN the project, review diffs, approve. Non-destructive is
the hard rule (same spirit as `/keel-adopt`): nothing is applied without a shown diff + an explicit yes.

**Plugin half first:** if the `keel` plugin is installed (skills show up as `/keel:keel-*`), the *live*
tooling (skills · agents · hooks) updates centrally — run `/plugin marketplace update keel` for that
half. The buckets below still apply in full: a plugin never writes repo files, so the committed
`.claude/**` copies (what standalone / no-plugin sessions run), `.claude-plugin/**`, and the template
docs are synced here.

## 1. Fetch the latest template (never inside the project)
```bash
rm -rf /tmp/keel-latest   # idempotent — clear the stale clone a previous /keel-update run left behind
git clone --depth 1 https://github.com/muratsilahtaroglu/claude-code-starter-kit /tmp/keel-latest
git -C /tmp/keel-latest rev-parse --short HEAD   # record for the handover line
```

## 2. Classify every template path into three buckets
- **PROTECTED — never touched (project-owned):** `HANDOVER.md` · `LESSONS.md` · `TASKS.md` · `PLAN.md` ·
  `docs/handover-archive.md` · `docs/architecture.md` · `docs/adr/*` (except the kit-owned `0000`
  template and the folder `README.md` — those are TOOLING) · `CLAUDE.md` · `README.md` · `LICENSE` ·
  `config/` · `requirements/*.{txt,lock}` contents · `.env.example` values · `src/` · `tests/` ·
  `scratch/` · `research/` findings · `reports/` · `.claude/last-audit` · `.claude/project-owner`
  (project state: audit clock + governance owner).
- **REVIEW — likely tailored; full diff, apply hunk-by-hunk with approval:** `rules.md` ·
  `.claude/settings.json` (permissions merge = union, keep the project's) · `.gitignore` ·
  `.pre-commit-config.yaml` · `pyproject.toml` · `Makefile` · `Dockerfile*` · `.dockerignore` ·
  `docker-compose.yml` · `.editorconfig` · `.github/*` (workflows + PR template) ·
  `docs/layouts.md` · `docs/user_manual.md`.
- **TOOLING — template-owned; summarize changes, one approval for the batch:** `.claude/skills/**` ·
  `.claude/hooks/**` · `.claude/agents/{researcher,verifier,auditor,README}.md` · `.claude/rules/README.md`
  (+ example) · `.claude-plugin/**` · `docs/security.md` · `docs/steering.md` ·
  `docs/adr/0000-adr-template.md` · `docs/adr/README.md` · `docs/assets/` · `CONTRIBUTING.md`
  (kit-meta by its own first line) · folder `README.md`s.

**If a path matches two buckets, the more protective one wins: PROTECTED > REVIEW > TOOLING**
(e.g. `config/README.md` is a folder README, but `config/` is PROTECTED → protected).

**Respect the bootstrap prune (rules.md §0e):** files the tailoring removed on purpose (recorded in the
first HANDOVER block / tailoring ADR) are **not re-added** — list them as "pruned, skipped" unless the
user explicitly asks for them back.

## 3. Present the plan, then apply approved-only
**Enumerate changes MECHANICALLY — do not eyeball.** For EVERY path in the TOOLING + REVIEW buckets,
`diff -q <template-copy> <project-copy>`; every differing file MUST appear in the plan. Hand-picking "the
files that obviously changed" is how a hook lands while the skill it references does not — a half-applied
update leaves the hooks ahead of the skills (e.g. an owner-review nudge with no `## Review` write logic).
Then one table — **new · changed · pruned-skipped · protected** — one line per file with what/why, and the
diffs per §2 buckets. Apply only what was approved; never resolve a conflict silently.

## 4. Verify + record
- **Consistency re-diff:** after applying, `diff -q` the TOOLING paths against the template again — none
  should still differ except the ones consciously skipped. A leftover diff means a skill/hook pair is
  half-updated (the §3 failure mode) — finish it before committing.
- Hooks stay executable: `chmod +x .claude/hooks/*.sh`. If `.claude-plugin/` changed:
  `claude plugin validate <project-root>`.
- Quick smoke: the project's tests still pass (rules.md §2.8).
- `HANDOVER.md` block (a) one-liner: `keel /keel-update applied @ <template-sha>: <files>`; structural
  changes also land in `docs/architecture.md` (rules.md §1.6). Commit with approval (rules.md §1.3);
  push only with approval (§6).
