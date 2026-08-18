# unit/ — why each test exists (one line per file, added with the file)

<!-- `test_<name>.py` — what it guards + origin (phase/bug). Example:
`test_scoring.py` — scoring edge cases: 0-price, missing fields (phase 2; the silent-NaN bug). -->

`test_keel_hooks.py` — the kit's own hook regression matrix (141 cases: block-dangerous ·
owner-guard · reground TASKS parsing + repo invariants). Origin: three security bypasses shipped
while eleven commit messages claimed a verified matrix — every one had been run in a session and
thrown away (`reports/2026-08-18-hook-audit.md`). KIT-OWNED: `/keel-update` replaces
`test_keel_*.py`, so never put your project's tests in that name.
