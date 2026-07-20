# <phase/work item>: <short title>

## What & why
<What this change does and the reason. Link the ADR if a decision was made.>

## How to test
<Commands / steps to verify — see rules.md §2.7.>

## Definition of Done (rules.md)
- [ ] Working product; "how to test this" included (§2.7)
- [ ] Relevant tests written & run via `make test` (auto-log → `reports/tests/`); summary in `HANDOVER.md`; new test files one-lined in their folder README (§2.8)
- [ ] `docs/architecture.md` updated for any structural change (§1.6)
- [ ] ADR added in `docs/adr/` if a significant decision was made
- [ ] `CLAUDE.md` / `docs/user_manual.md` updated if behavior/usage changed (§1.3)
- [ ] `HANDOVER.md` session block added (§1.4); done `TASKS.md` items deleted; new lessons in `LESSONS.md` (§9)
- [ ] `git diff --cached` reviewed — no `.env`/secrets staged (§6.18)
- [ ] Deps changed? lock refreshed + `pip-audit` clean (§7.23)
