# 2026-09-25 — alice_v2 second promotion round (v0.8.37)

**Source:** alice_v2 measured read-only over 2026-09-06 → 2026-09-25 (783 commits). alice had not pulled
v0.8.36; nothing in alice was changed (kit-first — alice pulls via `/keel-update`). Previous round:
`reports/2026-09-06-alice-promotion-review.md`.

## What the project showed (measured)
| Signal | Value |
|---|---|
| commits touching product code | 118 of 783 (15%) — process-only 636 (81%), up from 70% on 09-05 |
| reports lines / product lines | 199k / 47k (4.2×), 1230 reports |
| longest fix loops | two items at r11 and r9, hand-written grammar rules, every round correct |
| HANDOVER | 146/150 lines (green) at **244 KB** — one line held 135 KB; auto-compact 3× in 5 min |
| one `/keel-compact` run | up to 59 tool turns at ~626k context ≈ 37M cache reads |
| LESSONS | 67 entries cooled to `docs/retro/`, but by BLANKING 508 lines in place to keep 55 line anchors |

## Decisions
| alice mechanism / defect | Verdict | Landed in kit |
|---|---|---|
| Per-LINE token caps (the 244 KB HANDOVER) | **ENTERS, narrower** — characters enforced (stdlib), tokens optional when `tiktoken` is installed | `entry-budget.py` per-line gate on CLAUDE/rules/HANDOVER/LESSONS/TASKS · reground KB caps + longest line · rules §1.4 |
| `keel_compact_gate.py` (ritual cost) | **ENTERS**, rewritten generic | `.claude/keel-compact-check.py` · `/keel-compact` step 2 |
| STALE-DISK marker on auto-compact + handover rhythm per work block | **ENTERS** | `pre-compact-snapshot.sh` · reground debt check · `/keel-handover` · HANDOVER header · rules §1.4 |
| Item approval fields (surface count, owner step that can FAIL) | **ENTERS**; the owner-approval step itself stays a project choice | `/keel-continue` ASSIGN · rules §10.41 |
| Rehearsal of live steps (2 variant inputs, never the owner's own) | **ENTERS**; port/model/account are alice's | `/keel-continue` ROUTE · rules §10.41 |
| Boundary sweep on T2 | **ENTERS** | `/keel-continue` ROUTE · `verifier.md` check 6 |
| Mechanism sentence is a separate claim | **ENTERS** | rules §10.37 · `verifier.md` check 5 |
| Index scope: live or cited reports only (608/1094 had no line) | **ENTERS** | `reports/team/README.md` · rules §10.40 · `/keel-distill` lint · steering |
| Owner asked desk decisions by the orchestrator only | **ENTERS** | rules §10.42 · charter skeleton · `/keel-continue` |
| Owner messages short, files complete | **ENTERS** (charter line) | charter skeleton |
| Window-name date suffix | **OPTION** only (a daily rename is a real cost) | `docs/steering.md` |
| r9/r11 patch loops (defect) | **FIXED IN KIT** — the third FAIL stops the loop and reopens the approach | rules §10.39 · `/keel-continue` ROUTE · orchestrator text |
| Blanking lines to keep anchors (defect) | **FIXED IN KIT** — documented as forbidden; anchors are the defect | `docs/memory-files.md` |
| `observer.md` missing from `/keel-update` TOOLING (kit's own v0.8.36 defect) | **FIXED** | `keel-update` SKILL bucket |
| `anchor-gate.py`, `owner_step_freshness.py`, `gate_corpus_diff.py` | **DOES NOT ENTER** — tied to alice's test style / id formats; concepts covered above | — |

## Verification
- Suite: 265 → 290 passed (`pytest tests/unit`); every new gate has cells for its RED and its pass.
- Pre-delivery review (rules §4.11, `verifier`): core claims confirmed (old entry-gate logic copied
  line for line; shell hooks always exit 0); 7 refutations, all fixed and pinned by a test — a
  new over-token line hid behind an old over-character one · the hook could traceback on odd input ·
  a relative path read `before` from the cwd · one existing path vouched for a missing Review note ·
  an unreadable STALE-DISK marker read as settled · the new KB default became a hidden second limit
  on a project that had raised its line cap (now scales in proportion, in both readers) · new cap keys
  were undocumented in §10.40.
- Run read-only against alice_v2, `keel-compact-check.py` reports what the project must fix on pull:
  one rules.md line of 401 characters, 9 ghost citations, and (on the old defaults) nothing else.

## Addendum 2026-09-26 — v0.8.38 (post-release audit of v0.8.37)
An auditor pass and a second independent review found defects in v0.8.37 before alice_v2 pulled it.
Every fix has a test that fails on the old code (checked by swapping the old files back in).
- **STALE-DISK was role-blind** (alice_v2 carries 163 markers): a worker was told to write HANDOVER,
  which §10.42 forbids. Markers are now tagged `@agent`, and a worker's marker is written and settled
  against its own `reports/team/<name>/board.md`. The compaction message no longer tells a worker to
  run a ritual. Agent names are matched literally, not as a regex.
- **compact-check faulted on a project-owned `entry-budget.py`** (alice's has no `read_caps`). The
  script now parses the caps file itself. A missing citation gate reads "NOT measured"; one that
  crashes or `sys.exit`s on import is rc 2, never a silent rc 0. Long lines are info, not RED.
- **Caps readers disagreed:** `KEY=10  # comment` read as 1020260925 in bash; one undecodable byte
  silenced `--check`; `KEY = 20` gave the entry gate its default while the line gate read 20. There is
  now one parser rule (leading digits, comments stripped, bytes replaced) in all three readers.
- **The window-name date suffix bypassed star-topology.** `<agent>_MM_DD` now resolves to the agent,
  but only when the name as written is not itself on the roster.
- **Silent off-switches are now said out loud:** a special token in a line (`encode` raises) now
  uses `encode_ordinary`; SessionStart names a `*_LINE_TOKENS` cap with no importable tiktoken, and a
  caps key one typo away from a known one. `.claude/keel-caps.example` lists every key and default.
- **Delivery gaps:** `/keel-update` ships `docs/memory-files.md`, `keel-caps.example` and the
  `reports/team/README.md` header. The entry-budget hook prefers the project's working `.venv`
  python. Doc wording is synced (T2-only Review, KB triggers in `/keel-distill`, steering cap keys).
