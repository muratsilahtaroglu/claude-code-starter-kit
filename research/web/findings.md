# web/ findings — official docs, SRE runbooks & industry QA guides (2026-07-16)

> Question: what do official Claude Code docs and industry runbooks prescribe for staged/verified
> batch runs, and which NATIVE mechanisms can enforce it. Feeds the pilot-gate design
> (candidate v0.8.2). Distilled per rules.md §8.

## Synthesis
Claude Code's own best-practices page prescribes exactly the ladder we need — in-prompt check →
`/goal` per-turn evaluator → **Stop-hook deterministic gate (exit 2)** → fresh-context
verification subagent — plus pilot-then-scale fan-out for bulk jobs. SRE canarying,
Write-Audit-Publish and acceptance sampling supply the numbers and the staging pattern. What no
source supplies is the enforcement RITUAL — that is the kit's slot.

## Findings (claim | source | confidence | note)
- Official verification ladder: "give Claude a check it can run"; Stop hook exit-2 gate
  (auto-overridden after 8 consecutive blocks); verification subagent that "tries to refute the
  result, so the agent doing the work isn't the one grading it" |
  https://code.claude.com/docs/en/best-practices | high | canonical, fetched in full.
- Official fan-out for bulk jobs: "test on a few files, then run at scale"; refine the prompt on
  the first 2-3 failures | same URL | high | = the user's exact "5000 tweets" scenario.
- Hooks mechanics: **exit 2 = blocking** (event-dependent), **exit 1 = non-blocking** (classic
  silent-pass gotcha); PostToolUse cannot undo the tool but its stderr IS fed back to Claude;
  Stop + exit 2 prevents stopping | https://code.claude.com/docs/en/hooks | high.
- Native capability map for pilot→verify→batch→monitor: PreToolUse gates by script/command
  pattern; **Monitor tool = the only native line-by-line output watcher**; `run_in_background`
  notifies on completion (no mid-run interrupt); subagents can verify but cannot halt the parent;
  permissions are too coarse for semantic gating |
  https://code.claude.com/docs/en/tools-reference.md ·
  https://code.claude.com/docs/en/sub-agents.md ·
  https://code.claude.com/docs/en/hooks-guide.md | high | guide-agent survey, spot-checked.
- Experimental "observer agents" (env-gated, v2.1.207+): read-only digest, ONE advisory message,
  **cannot halt/pause/veto**; absent from official docs |
  https://claudefa.st/blog/guide/agents/observer-agents | medium | third-party writeup of an
  undocumented feature — do NOT build on it.
- Ralph loop pattern (community): `while` loop around `claude -p`; guards = tests as
  backpressure, one task per loop, spec files; known failures = placeholder implementations;
  recovery = `git reset` | https://ghuntley.com/ralph | high | pattern essay, widely referenced.
- The "Hermes watchdog" phrase = community blog describing a **cron job that restarts the crashed
  Hermes gateway process** — uptime supervision, not output QA |
  https://buttondown.com/witcheer/archive/mac-mini-24-7/ | high | primary source of the phrase.
- Hermes official docs: security = command approval / DM pairing / container isolation; no
  verification watchdog | https://hermes-agent.nousresearch.com/docs/ | high.
- SRE canarying: expose to a small population first, widen progressively, **auto-halt when the
  canary error metric diverges from control** | https://sre.google/workbook/canarying-releases/ |
  high | the 1%→10%→100% split is convention, not prescribed — FLAG.
- Anthropic Batch API: "verify your request shape with the Messages API first"; per-request
  terminal states (succeeded/errored/canceled/expired); results unordered — match by custom_id |
  https://platform.claude.com/docs/en/docs/build-with-claude/batch-processing | high | retry &
  resume are per-request, which is what makes checkpointing workable.
- OpenAI batch cookbook: try requests on the sync endpoint first; results unordered |
  https://developers.openai.com/cookbook/examples/batch_processing | high | honest negative:
  API docs do NOT supply QA methodology — the discipline must come from elsewhere.
- Krippendorff α thresholds: **α ≥ 0.800 reliable; 0.667–0.800 tentative conclusions only** |
  https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff's%20Alpha-Reliability.pdf |
  high | the author's own canonical guidance; applies to LLM-vs-human agreement.
- Honeypots/gold items seeded into live batches at **5–10% coverage**; per-job quality scored
  from honeypot accuracy | https://www.cvat.ai/resources/blog/annotation-qa-honeypots | high |
  vendor doc but concrete.
- Pilot sizing **100–200 items or 5–10%** of dataset (industry labeling guides) |
  https://www.taskmonk.ai/blogs/guide-to-data-labeling-quality ·
  https://labelyourdata.com/articles/data-annotation/quality-assurance | medium | search-summary
  figures — FLAG.
- **Rule of three**: 0 errors in n sampled outputs ⇒ true error rate < 3/n at 95% confidence
  (spot-check 60 ⇒ <5%; 300 ⇒ <1%) |
  https://www.statology.org/a-concise-guide-to-the-statistical-rule-of-three/ ·
  https://asq.org/quality-progress/articles/back-to-basics-zero-defect-sampling?id=1f11b12f0dd74b3887336e7ad907c561 | high.
- dbt `severity`/`warn_if`/`error_if` = the citable error-rate circuit breaker (e.g.
  `error_if: ">10"` halts; failed upstream test skips downstream models) |
  https://docs.getdbt.com/reference/resource-configs/severity | high.
- Great Expectations checkpoints gate pipelines on validation results |
  https://docs.greatexpectations.io/docs/0.18/reference/learn/terms/checkpoint/ | medium-high.
- Write-Audit-Publish (Netflix-origin): write batch outputs to a STAGING location → audit there →
  publish only on pass | https://lakefs.io/blog/data-engineering-patterns-write-audit-publish/ ·
  https://aws.amazon.com/blogs/big-data/build-write-audit-publish-pattern-with-apache-iceberg-branching-and-aws-glue-data-quality/ | high.
- AWS Augmented AI human-loop triggers: below-confidence routing + random-sample audit — the
  industry-standard two human gates |
  https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-use-augmented-ai-a2i-human-review-loops.html | high.

## Takeaway for Keel
Everything needed exists natively (PreToolUse gate + verifier subagent + Monitor + Stop hook).
What is missing in every source is the non-optional RITUAL — a pilot gate with pre-declared
thresholds. That is precisely the kind of gap Keel exists to fill.

---

# web/ findings — instruction-loading semantics across coding agents (2026-08-17)

> Question: what EXACTLY loads when, and survives compaction, across Claude Code's memory mechanisms
> and comparable products — the constraint set for a task-scoped LESSONS design. Distilled per §8.

## Synthesis
Every major agent converged on the same three tiers: always-on file → glob-scoped rule files →
description-matched, body-on-demand units. Two findings change our design: (1) **skills also accept
`paths:`** AND invoked skill bodies are the ONLY scoped mechanism **re-injected after compaction**;
(2) shrinking context is an **accuracy** argument, not just a token one — a focused ~300-token
context beat a 113k one containing the same facts, and a SINGLE distractor measurably degrades
retrieval. No official doc of any product uses embeddings for rules/memory retrieval.

## Findings (claim | source | confidence | note)
- Compaction table — what survives: root `CLAUDE.md`, **unscoped** rules, auto memory → re-injected
  from disk; **`paths:`-scoped rules → LOST until a matching file is read again**; nested CLAUDE.md →
  lost until that subdir is read; **invoked SKILL bodies → re-injected (5,000 tok/skill, 25,000 tok
  total, oldest dropped first)** | https://code.claude.com/docs/en/context-window | high | OFFICIAL; confirms our §9.33 caveat verbatim.
- **Skills accept `paths:` frontmatter** ("same format as path-specific rules") + description-matched
  activation; body loads on invoke and persists for the session; truncation keeps the START of the
  file | https://code.claude.com/docs/en/skills | high | OFFICIAL, little-known — this is the missing graduation destination.
- Official steering: for "task-specific instructions that don't need to be in context all the time,
  use skills instead… loaded when you invoke them or when Claude determines they're relevant" |
  https://code.claude.com/docs/en/memory | high | OFFICIAL endorsement of description-matched selection.
- `@`-imports do NOT reduce context (all load at launch, depth max 4); "target under 200 lines per
  CLAUDE.md — longer files consume more context and **reduce adherence**" | same | high | OFFICIAL adherence tax, stated by the vendor.
- Auto-memory shape = **capped index + on-demand bodies**: `MEMORY.md` loaded every session but
  TRUNCATED at 200 lines / 25KB; topic files are **not** loaded at startup, read on demand; a write
  that overflows the index ERRORS and demands a rewrite | same | high | the pattern Anthropic ships AND enforces.
- Path-glob failure modes are SILENT: brace expansion budget 1,000 patterns / 4 MiB (over-budget →
  used unexpanded → matches nothing); a malformed `[` bracket matches nothing | same | high | extends our dead-glob lint.
- `InstructionsLoaded` hook logs which instruction files loaded, when and why | same | high | observability: measure whether scoping actually fires before/after.
- **Context rot (the key citation):** LongMemEval, 18 models — a ~300-token focused context beat the
  ~113k context CONTAINING the same needed information, across all model families (largest gaps:
  Claude Opus 4 / Sonnet 4); a SINGLE distractor degrades retrieval and the effect compounds |
  https://www.trychroma.com/research/context-rot | high | independent, multi-model; the accuracy argument for pruning always-on lines.
- Anthropic framing: context is "a finite resource with diminishing marginal returns"; prescribes
  just-in-time retrieval via lightweight identifiers + progressive disclosure | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | high | OFFICIAL framing (no numbers of its own).
- Vendor-measured: memory tool + context editing +39% over baseline (context editing alone +29%),
  84% token reduction on a 100-turn eval | https://claude.com/blog/context-management | medium-high | vendor's own eval, magnitude unverified.
- Comparable products' SELECTION mechanism: Cursor `.mdc` (alwaysApply / globs / **description-matched
  "Apply Intelligently"** / manual; "keep rules under 500 lines") | https://cursor.com/docs/context/rules | high | OFFICIAL.
- Copilot `.github/instructions/*.instructions.md` uses `applyTo:` globs; **not applied at all if
  absent**; "keep instructions short and self-contained, each a single simple statement" | https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot | high | OFFICIAL; glob-only, no description tier.
- Community failure data for glob selection: stale globs after a directory rename fail SILENTLY;
  vague descriptions never match | https://forum.cursor.com/t/cursor-rules-globs-inconsistencies/116958 · https://forum.cursor.com/t/rules-not-being-applied-as-expected/144731 | medium | forum reports, version-dependent, but the CLASS is corroborated.
- The anti-pattern, shipped: Cline Memory Bank — six fixed files, "I MUST read ALL memory bank files
  at the start of EVERY task"; no scoping, token cost unquantified | https://docs.cline.bot/prompting/cline-memory-bank | high | where an unscoped LESSONS.md ends up.
- No embeddings anywhere in official rule/memory retrieval; Claude Code reportedly dropped its early
  vector index for agentic search (precision · freshness · no index to maintain) | https://vadim.blog/claude-code-no-indexing/ · https://cline.bot/blog/why-cline-doesnt-index-your-codebase-and-why-thats-a-good-thing | medium | community-reported vendor decisions; the NEGATIVE (no official doc uses vectors) is high confidence.
- Agent-memory benchmarks are NOT citable: a LoCoMo audit reports ~6.4% of the answer key wrong and
  the LLM judge accepting 63% of intentionally wrong answers; mem0-vs-Zep numbers are contested by
  both vendors | https://penfieldlabs.substack.com/p/proposal-a-new-benchmark-for-long · https://blog.getzep.com/lies-damn-lies-statistics-is-mem0-really-sota-in-agent-memory/ | low-medium | report as contested, never as evidence.
- A-MEM (NeurIPS 2025) is Zettelkasten-inspired agent memory (note + keywords + links, evolving) but
  retrieves by embeddings | https://arxiv.org/abs/2502.12110 | high for existence, medium for transfer.

## Conclusion (drives the design; decision → ADR)
Keep grep + globs + descriptions (§9.35 now has citable support, not just assertion). Add the missing
destination: a **`paths:`-scoped SKILL** for lesson clusters that must survive compaction mid-work.
Copy auto-memory's shape: **capped index + on-demand bodies**. Extend the dead-glob lint to brace
budget + bracket validity. Instrument with `InstructionsLoaded` before claiming any win.
