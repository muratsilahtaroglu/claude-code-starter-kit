# unit/ — why each test exists (one line per file, added with the file)

<!-- `test_<name>.py` — what it guards + origin (phase/bug). Example:
`test_scoring.py` — scoring edge cases: 0-price, missing fields (phase 2; the silent-NaN bug). -->

`test_keel_hooks.py` — the kit's own hook regression matrix (154 cases: block-dangerous ·
owner-guard · reground TASKS parsing + repo invariants · the workspace-trust check that names
allow rules withheld until the trust dialog is accepted, silent when trusted, when there are no
allow rules, or when the config is unreadable · the review-DECAY check: an old delivery is named
with its age, a fresh one is silent, the threshold is keel-caps-tunable, uncommitted evidence has no
age yet · the retirement-candidate signal names the oldest unpromoted LESSONS entries only near the cap
· the ADR orphan check names an uncited Accepted decision, spares a cited or merely Proposed one and
the template's status alternation). Origin: three security bypasses shipped
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

`test_keel_team_addresses.py` — the identity→address resolver (18 cases: healthy lane · closed
window · reverted display name flagged as NAME_MISMATCH not death · one session-id in two windows ·
unregistered live session · per-identity aggregation so a stale dead row beside a live one stays
quiet · the two-machine axis: ATTACHED/DETACHED twins from the VS Code server's client signal, never
guessed when the signal is missing · the SELF check that tells THIS window its address diverged).
Origin: the 2026-08-19 "name unreachable ≠ session dead" incident and the 2026-09-03 two-VS-Code-
builds twin case; resolver backported from alice_v2's `scripts/team_addresses.py`. KIT-OWNED.

`test_keel_launch_wrapper.py` — the resume-keeps-its-name launcher (12 cases: identity map names
a resumed session · separate-arg `--resume` form · transcript `agent-name` record as fallback · map
wins over transcript · new sessions, explicit `--name`, unknown sids pass through untouched ·
unsafe map tokens never injected · fails open when the config dir is missing · never writes stdout · the opt-in trace records both
branches and is never created by the wrapper).
Origin: measured 2026-09-03 — `/rename` lands in the transcript but a `--resume`d process comes up
`nameSource=derived`, so the agent name vanished on every reopen; the fix was then confirmed
through the real IDE (three reopened tabs came up `nameSource=user`). KIT-OWNED.

`test_keel_citation_gate.py` — the provenance gate (9 cases: a committed citation is clean · a
note on disk but not in HEAD is a GHOST and the finding names who cites it · a report swept into
`done/` still resolves · `..` is normalised before git is asked · a gitignored path is a THIRD class,
listed not counted · a foreign path's TAIL never matches as a local path · an unresolvable path is
counted, never dropped · the allowlist silences a deliberate absence · a non-repo is a silent no-op).
Origin: `git commit -- <path>` skips an untracked file WITHOUT erroring, so a record keeps a
reference the artefact never earned; measured on a live project where the class repeated three times
in one day under a written rule, which is why §6.18 became a gate (§10.38). KIT-OWNED.

`test_keel_entry_budget.py` — the per-entry line budget for the always-imported boards (18 cases: oversized new entry
blocked · the fold-in blind spot closed (an Edit with no dated line that grows an entry past budget)
· shrinking always passes · pre-existing backlog never blocks unrelated edits · per-file caps tunable via
keel-caps · --check baseline auto-lowers and never auto-raises · the same gate over TASKS.md board
items, whose lane `### ` headings end an entry and whose doctrine-header bullets are not entries · a fenced code block is neither an entry nor
padding for the one before it).
Origin: a live project measured 450→1039 LESSONS lines in five days from entries GROWING, not
multiplying — raising the file cap "was never enough"; the same disease then showed on its board
(12 `## Review` items in 211 lines), so one hook guards both files. KIT-OWNED.

`test_keel_agent_identity.py` — agent-team identity resolution in the reground hook (5 cases: the
resolved session's mapping date touches to TODAY on every SessionStart · other lanes' dates are
left alone · an unmapped session id never fabricates a row · the Session-id line still prints ·
solo projects with no team are a silent no-op). Origin: a VS Code restart left the session id and
mapping intact but reset `/list-agents`' display name, and the orchestrator misread "name
unreachable" as "session dead" (`docs/steering.md` "Addressing: the session name IS the address").
KIT-OWNED.
