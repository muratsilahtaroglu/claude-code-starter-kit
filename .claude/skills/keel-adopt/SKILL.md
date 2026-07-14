---
name: keel-adopt
description: Adopt Keel's discipline into an EXISTING project (brownfield) — inventory, non-destructive merge, back-fill docs from real code, migrate security. Never overwrites.
---

# /keel-adopt — bring an existing project under Keel discipline (brownfield)

Use when the project **already has code + history** (rules.md §0, Mode B). Goal: overlay the template's
discipline **without clobbering anything**. Non-destructive is the hard rule — propose the full plan, get
approval, then act. Nothing is overwritten without a shown diff + an explicit yes.

## 1. Inventory & classify
Bucket every template path against the repo and report the three lists **before touching anything**:
- **missing** → safe to add as-is.
- **present** (project already has its own: `README.md`, `.gitignore`, `pyproject.toml`, `Makefile`,
  `CLAUDE.md`, `Dockerfile`, ...) → **merge**, never replace.
- **conflicting** (same path, different intent) → show a diff, ask.

Safe bulk-add of only-missing files (never `cp -r` over the top; never `rm -rf .git`):
```bash
rsync -av --ignore-existing <keel>/ ./ --exclude .git
```

## 2. Back-fill the living docs from real code
- `docs/architecture.md` ← reverse-engineer the **current** module map (what each real dir/file does; status ✅).
- `HANDOVER.md` ← write the FIRST session block: (a) what already exists / works **today** (not blank
  placeholders); seed `LESSONS.md` with known gotchas and `TASKS.md ## Now` with the actual next work.
- Capture the adoption itself as an ADR in `docs/adr/` (what was added / merged / deferred and why).

## 3. Reconcile discipline
- **Merge, don't replace** an existing `CLAUDE.md` and `.claude/settings.json` (union the permissions; keep the project's).
- Map the existing source layout to the nearest `docs/layouts.md` profile — don't create parallel folders beside it.
- Prune template parts the project won't use, cascading reference cleanup (rules.md §0a).

## 4. Security migration (rules.md §7 — as a migration, not a rewrite)
- Freeze **currently-installed** versions into `==` in `requirements/base.txt`; `pip-compile --generate-hashes`.
- `pip-audit`; fix criticals first. **Don't break a working build** chasing the ideal — stage it over phases.

## 5. Approve → commit
Present the plan as three columns — **add · merge · defer** — with reasons. On approval, apply, then propose
an approved commit (rules.md §6). Update `HANDOVER.md` before ending the session (rules.md §1.4).
