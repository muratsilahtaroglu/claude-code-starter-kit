# unit/ — why each test exists (one line per file, added with the file)

<!-- `test_<name>.py` — what it guards + origin (phase/bug). Example:
`test_scoring.py` — scoring edge cases: 0-price, missing fields (phase 2; the silent-NaN bug). -->

`test_keel_hooks.py` — the kit's own hook regression matrix (141 cases: block-dangerous ·
owner-guard · reground TASKS parsing + repo invariants). Origin: three security bypasses shipped
while eleven commit messages claimed a verified matrix — every one had been run in a session and
thrown away (`reports/2026-08-18-hook-audit.md`). KIT-OWNED: `/keel-update` replaces
`test_keel_*.py`, so never put your project's tests in that name.

`test_keel_telemetry.py` — the kit's observability layer (13 cases: ritual-log agent tagging ·
probe isolation · Stop-hook traces · the duplicate detector's signal · /keel-stats reporting a
silent event kind as an INSTRUMENT gap). Origin: a false "hooks are double-firing" warning that
ran at every session start for two days, caused by test runs writing into the live telemetry
(`reports/2026-08-19-observability-audit.md`). KIT-OWNED — `/keel-update` replaces `test_keel_*.py`.

`test_keel_star_topology.py` — the star wall for agent teams (12 cases: worker→worker blocked
incl. the `[ref]` disambiguator · worker→orchestrator and every off-roster target allowed · solo
projects untouched · fails open · the block is logged with @attribution). Origin: the message-driven
team design of 2026-08-19 — a permission rule cannot express "by target", so the topology had to
become a hook (`reports/2026-08-19-agent-team-messaging.md`). KIT-OWNED.

`test_keel_agent_identity.py` — agent-team identity resolution in the reground hook (5 cases: the
resolved session's mapping date touches to TODAY on every SessionStart · other lanes' dates are
left alone · an unmapped session id never fabricates a row · the Session-id line still prints ·
solo projects with no team are a silent no-op). Origin: a VS Code restart left the session id and
mapping intact but reset `/list-agents`' display name, and the orchestrator misread "name
unreachable" as "session dead" (`docs/steering.md` "Addressing: the session name IS the address").
KIT-OWNED.
