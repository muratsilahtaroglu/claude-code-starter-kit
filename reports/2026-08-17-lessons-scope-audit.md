# LESSONS.md scope audit — how much of an always-loaded lessons file any one task actually needs

_2026-08-17 · internal measurement (not external research — the citations live in
`research/{web,articles}/findings.md`) · corpus: `alice_v2/LESSONS.md`, a live 10-month project._

## Headline

| Metric | Value |
|---|---|
| Entries / file lines | **83 / 451** (declared cap 400 → 13% over) |
| Average entry | **5.16 lines** — 96% are MULTI-line, not the one-liners the template prescribes |
| (A) Always-relevant discipline | **22 entries / 124 lines (26.5%)** |
| (B) File/area-scoped | **43 entries / 229 lines (51.8%)** |
| (C) Domain/reference facts (belong in docs) | 7 / 33 |
| (D) Historical / promoted-out stubs | 11 / 42 |
| **Retrieval hit rate (4 realistic tasks)** | **≈15% — 12.5 of 83 entries per task** |
| Stale path references | 3 of 56 (5.4%) — the file is well maintained |

**The problem is not staleness, it is volume-per-relevance.** For a router-prompt task, 34 irrelevant
file-scoped entries (~180 lines) ride along. Per the context-rot evidence (research/web), those are
not merely a token cost — distractors measurably degrade retrieval of the lines that DO apply.

## What scoping would buy
Moving bucket B behind `paths:` triggers removes ~180–190 of 428 entry-lines (**~44%**) from a typical
session with no loss of what that session needs. With (C) → docs and (D) deleted, the always-loaded
core lands at **~124–150 lines** — about a third of today's file, and back under cap.

## Two structural findings

**1. The A-bucket is a floor, not waste.** Across all four tasks, 6–9 of the needed entries were
bucket A (verification duty, measurement epistemics, ritual protocol) — ~100% utilisation. Scoping
those would be a regression. The counter-case is instructive: a *release* task needs 11 entries that
are almost all A/D and would gain nothing from path-scoping. **Scoping pays off for code-touching
work and is neutral-to-negative for ritual work.**

**2. Our graduation pipeline has a bug: it promotes the content but never deletes the pointer.**
10 entries carry an explicit "TERFİ ETTİ" (promoted) marker and remain as 3–4 line signposts —
42 lines of residue, paid every session. Fix: promotion DELETES the entry; the router line in the
index is the only pointer that survives. (7 of the 11 keep a live 1–2 line tail — that tail belongs in
the target file, not here.)

## Cluster structure (does an index have real edges?)
Yes: ~65% of entries link outward already (18 → docs, 16 → reports/team evidence, 11 → ADRs, 3 →
`.claude/rules/`), and **14 entries explicitly name a sibling entry** inside the file. Ten natural
clusters emerged; 5 of them map cleanly onto directories (keyword/word-boundary · counting-dedup ·
router/tool-selection · guard/honesty · test-validity), and two (measurement epistemics · ritual)
map onto nothing file-shaped — which is exactly the A/B boundary drawn by hand.

Cluster sizes land at 4–11 entries: inside the 10–20 sweet spot the PKM literature reports for an
index, and the three clusters that already became `.claude/rules/` files are the working proof.

## Lint implication (measured)
30 of 33 initially-unresolved references were **basename-only** citations (`keyword_filter.py`,
`column_notes.yaml`) that do resolve. A naive freshness lint would report ~54% false staleness —
**it must resolve by basename** before flagging.

## Method / limits
Classification and the per-task retrieval sets are a careful reading, not observed sessions; the
audit biased toward inclusive ("needed" if it plausibly changes a decision), so **15% is an upper
bound** on hit rate. ~15 entries were mixed-bucket and got a primary-bucket call; splitting their
sub-lessons would move 5–8 entries from B to A.
