# articles/ findings — batch-QA literature & agent-harness engineering posts (2026-07-16)

> Question: citable best practice for validating large LLM batch jobs (pilot runs, agreement
> thresholds, LLM-as-judge reliability, halt conditions). Feeds the pilot-gate design
> (candidate v0.8.2). Distilled per rules.md §8.

## Synthesis
One loop recurs across annotation science, MLOps and Anthropic's own harness engineering posts:
**gold set → small pilot → gate on pre-declared metrics → progressive ramp with runtime guards →
final acceptance sampling**, with generation and evaluation deliberately separated to defeat
self-assessment bias. Aggregate model competence says nothing about YOUR task — per-task
validation is non-negotiable.

## Findings (claim | source | confidence | note)
- LLM annotation must be validated PER TASK against human labels: across 27 real tasks GPT-4's
  median accuracy was 0.850, yet **1/3 of tasks had precision or recall < 0.5** |
  https://arxiv.org/abs/2306.00176 | high (PDF read by researcher) | Pangakis, Wolken & Fasching
  2023 — the canonical paper. Also: "consistency score" (classify repeatedly at T≈0.6, take modal
  label; low consistency ⇒ escalate to human) and a **250–1,250-item** human validation set (fn. 7).
- LLM-as-judge reaches >80% agreement with humans (≈ the human-human ceiling) BUT carries
  position, verbosity and self-enhancement biases | https://arxiv.org/abs/2306.05685 | high |
  Zheng et al. 2023 (MT-Bench/Chatbot Arena).
- Position bias studied systematically; swap-positions(-and-tie) is the standard mitigation |
  https://arxiv.org/abs/2406.07791 | medium-high | "Judging the Judges" 2024.
- Self-preference bias quantified: judges rate their own outputs higher |
  https://arxiv.org/pdf/2410.21819 | medium (abstract level).
- Panel of small diverse-family judges + voting outperforms a single big judge, with less bias
  and lower cost | https://arxiv.org/abs/2404.18796 | high | PoLL, Verga et al. 2024.
- Self-consistency: sample multiple reasoning paths, majority-vote (+17.9% GSM8K) |
  https://arxiv.org/abs/2203.11171 | high | Wang et al. 2022 — basis for multi-vote labeling.
- CoAnnotating: allocate items human-vs-LLM by LLM uncertainty (entropy over repeated
  annotations); up to +21% over random allocation | https://arxiv.org/abs/2310.15638 | high |
  EMNLP 2023 — disagreement-triggered escalation.
- Alt-test: statistical procedure for justifying replacing human annotators with an LLM |
  https://arxiv.org/pdf/2501.10970 | medium — read at abstract level only, FLAGGED unread.
- "LLM hacking": plausible config choices (model/prompt) alone flip scientific conclusions drawn
  from LLM annotations ⇒ validate per task AND per config | https://arxiv.org/pdf/2509.08825 |
  medium (abstract) | FLAGGED.
- Anthropic 2-agent harness (2025-11): initializer/coder, pass-fail feature-list JSON + progress
  file + git checkpoints; names the failure mode "premature victory declarations" |
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | high.
- Anthropic 3-agent harness (2026-03): planner/generator/EVALUATOR — "separating generation from
  evaluation to prevent self-assessment bias"; evaluator tests against a negotiated "sprint
  contract" | https://www.anthropic.com/engineering/harness-design-long-running-apps | high.
- Evaluator-optimizer workflow (generator loop + evaluator scoring against explicit criteria) —
  the primitive under all of the above |
  https://www.anthropic.com/research/building-effective-agents | high.

## Numbers to reuse (defensible defaults, sources above)
- Human-labeled validation set: **250–1,250 items** (more if positive class <1%) — Pangakis.
- Smoke pilot: **10–50 items eyeballed** (convention, no single citation — FLAG); formal pilot
  **100–200 items or 5–10%** (vendor guides, medium confidence).
- Agreement bar: **Krippendorff α ≥ 0.800** to rely; 0.667–0.800 tentative only (see web/).
- LLM-judge trust bar: **>80% human agreement**, de-biased via swapped positions + diverse panel.
- Self-consistency escalation: **3–7 votes at T≈0.6, modal label**; non-unanimous → human
  (vote count is convention — FLAG).

## Takeaway for Keel
The pilot gate is not folklore — it is the published norm (Anthropic's own harness posts
included). The kit's job is to turn it into a non-skippable ritual with pre-declared thresholds;
the existing `verifier` subagent is the "evaluation separated from generation" leg.

---

# articles/ findings — "second brain" / Zettelkasten / Obsidian graph pattern (2026-08-17)

> Question: should `LESSONS.md` become a linked note graph (Obsidian-style) so a session sees only
> task-relevant lessons? Feeds the task-scoped memory design. Distilled per rules.md §8.

## Synthesis
The pattern's evidence base is almost entirely practitioner opinion — **no controlled study** shows a
note graph improves retrieval. Even its defenders concede the **global graph is decorative**; the
load-bearing parts are Luhmann's **hubs (index notes)** and manually-reasoned links. The only
replicated science nearby (Bergman, PIM) says people retrieve by **navigating a known structure**,
using search as a fallback — which argues for a router that is IN context, pointing at bodies that
are deterministically reachable.

## Findings (claim | source | confidence | note)
- Global graph degrades with size and is used as hygiene (spot orphans/duplicates), not navigation —
  its best steelman still frames it that way | https://www.eleanorkonik.com/p/its-not-just-a-pretty-gimmick-in-defense-of-obsidians-graph-view · https://forum.obsidian.md/t/whats-the-point-of-the-graph-view-how-are-you-using-it/71316 | medium | practitioner self-report, many independent voices.
- **Auto-backlinks are contested by the community's own authority**: context-free backlinks are "one
  of the least useful type of link" and add decision cost; links should be placed manually WITH the
  reason to follow them | https://zettelkasten.de/posts/backlinks-are-bad-links/ | medium-high | opinion, well argued.
- **"The money is in the hubs"** — Luhmann's ~24k/66k-slip archives had a deliberately INCOMPLETE
  keyword index (~3,200 keywords, 1–4 entry points each); hub notes (pure link lists) carried
  navigation | https://zettelkasten.de/posts/zettelkasten-hubs/ · https://forum.zettelkasten.de/discussion/184 | high | primary scholarship (Schmidt, archive curator).
- MOC sizing squeeze: 3-item indexes proliferate, 100-item indexes are unwieldy; practitioner sweet
  spot ~10–15 entries per index | https://forum.obsidian.md/t/too-many-maps-of-content/25886 | medium.
- **Index staleness is the default state**, invisible until something surfaces orphans — the reason
  dedicated broken-link/orphan plugins exist | https://practicalpkm.com/how-healthy-is-your-obsidian-vault/ · https://github.com/Vinzent03/find-unlinked-files | medium-high | tools existing = failure is recurrent.
- Query-assembled views (Dataview) fail in the one way memory cannot tolerate: a `WHERE` on a missing
  field **silently drops** notes; ~90% of query issues are metadata typos | https://www.dsebastien.net/the-complete-guide-to-dataview-in-obsidian/ · https://github.com/blacksmithgu/obsidian-dataview/discussions/2151 | medium.
- Atomicity enforced at capture produces underdeveloped "prompt machine" notes offering little beyond
  the title | https://zettelkasten.de/posts/principle-of-atomicity-difference-between-principle-and-implementation/ | medium-high.
- What breaks at scale is RESTRUCTURING, not storage (10k-note vaults work; mass renames break links
  and freeze the app); veteran advice is to NOT migrate old notes | https://forum.obsidian.md/t/for-those-with-huge-vaults-anything-you-d-do-differently-or-wish-you-d-known-before-starting/99754 | medium.
- Collector's fallacy: collecting feels like learning; unprocessed notes pile up | https://zettelkasten.de/posts/collectors-fallacy/ | medium-high.
- **Replicated science (the only hard evidence here):** users prefer navigating a known structure over
  search, regardless of search quality | https://www.tau.ac.il/education/muse/publications/101.pdf · https://www.tandfonline.com/doi/full/10.1080/07370024.2024.2379838 | high | about human file retrieval, not LLMs — transfer with care.
- **Absence of evidence:** no writeup measures which retrieval path is actually used in a vault; every
  "the graph helped me find X" claim is a single anecdote | — | high | searched multiple framings.

## Conclusion (drives the design; decision → ADR)
DROP: global graph · auto-backlinks · query-assembled views · serendipity-as-goal. KEEP: **hub/index
over graph**, ~10–20 entries per index, and **mechanical orphan/staleness lints** (every community
that adopted indexes ended up building them). Do the minimum: at 250–450 lines we are two orders of
magnitude below where practitioners report structural pain.
