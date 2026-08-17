# reports/ — generated reports (dated)

Phase acceptance reports + generated output reports are archived here. Naming: `YYYY-MM-DD-<topic>.md`.

`tests/` — test-run traces: raw per-run logs in `tests/<YYYY-MM-DD>/` (auto-written by `make test`,
git-ignored — local history) + **committed** phase summaries `tests/<YYYY-MM-DD>-phase<N>.md` (written
at `/keel-phase-review`). Convention: root `tests/README.md`.

`team/` — per-author task reports (spec + solution notes + evidence), ONE index: `team/README.md` —
which is also the team's review TODOLIST (state chain `wip → delivered → verified → closed`;
rules.md §10.40).
