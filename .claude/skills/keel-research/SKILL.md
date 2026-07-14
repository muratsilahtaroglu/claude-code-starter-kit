---
name: keel-research
description: Opt-in external research — scan GitHub/articles/LinkedIn/HuggingFace/web and save cited findings per platform under research/.
---

# /keel-research — structured, opt-in external research

**HARD GATE: never run without the user's explicit opt-in in THIS session (rules.md §8.27).** If the
user hasn't opted in, stop and ask first. Produce a **verified, cited evidence trail** — never blind copy.

Workflow:
1. **Scope** — confirm the question + which platforms to scan (`github`, `articles`, `linkedin`,
   `huggingface`, `web`). Add/drop platforms to fit the question.
2. **Fan out** — one `researcher` subagent (`.claude/agents/researcher.md`) per platform, in parallel.
   Each searches, reads *real* sources (not just snippets), and writes `research/<platform>/findings.md`.
   Large/raw artifacts go to `research/<platform>/downloads/` (git-ignored).
3. **Cite + rate** — every claim carries its source URL + a confidence note; flag low-signal/paywalled sources.
4. **Verify (rules.md §4)** — as the main agent, don't accept sub-agent output blindly; sanity-check the
   load-bearing claims before they drive anything.
5. **Synthesize** — a short cross-platform summary; conclusions that drive a decision go into an ADR
   (`docs/adr/`) or `docs/`, not left buried under `research/`.
