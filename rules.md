# rules.md — Working rules (GENERIC TEMPLATE)

> Project-agnostic discipline. Use as-is in the new project; fill in the `<...>` blanks.
> These rules apply every session.

## 0. Session start
0. **(First session only) Bootstrap — fit the template to THIS project.** Before anything else, understand
   the project (goal, type, constraints, target platforms/hosts) and ask the **project language** (e.g.
   Turkish or English) for docs. Then propose a tailoring plan and **apply it only after user approval** —
   never silently keep, delete, add, or **overwrite**. First pick the mode:

   - **Mode A — New / greenfield project** (empty or near-empty repo): the template files are the starting
     point. Go straight to the tailoring plan (a)–(e) below.
   - **Mode B — Adopt into an EXISTING project** (brownfield): the project already has code + history; the
     template is *overlaid, never dumped on top*. **Non-destructive is the hard rule.** Run the `/keel-adopt`
     skill (`.claude/skills/keel-adopt/`), which before (a)–(e) additionally:
     - **keeps their `.git`** — never re-init or wipe history (no `rm -rf .git`);
     - **inventories & classifies** every template path vs. the repo — *missing* (safe to add), *present*
       (project has its own: `README.md`, `pyproject.toml`, `.gitignore`, `CLAUDE.md`, ...), or
       *conflicting* — and **adds only the missing; merges present/conflicting from a shown diff with
       approval; never overwrites** (safe bulk-add: `rsync -av --ignore-existing <keel>/ ./ --exclude .git`);
     - **back-fills the living docs from the real code** — reverse-engineers `docs/architecture.md` and
       fills `HANDOVER.md` (a) with what already exists (not blank placeholders);
     - **adopts security §7 as a migration** — freezes *currently-installed* versions into `==`, generates
       the lock, `pip-audit`; doesn't break a working build to reach the ideal;
     - **records the adoption in an ADR** (what was added / merged / deferred and why).

   The tailoring plan (both modes) covers:
   - **(a) Prune what's unneeded** — list template parts to remove *with reasons*, then **cascade the
     removal**: grep the removed part's name across every `.md` (README.md, CLAUDE.md, docs/* incl.
     `docs/user_manual.md`, HANDOVER.md, folder READMEs) and **update or delete every reference** so no dangling
     mention or architectural confusion remains. *Example:* project won't use GitHub → also remove
     `.github/` (workflows + PULL_REQUEST_TEMPLATE.md), rewrite §6 for the real host (GitLab →
     `.gitlab-ci.yml`; no remote → local-commits-only), and fix the README contents list + every
     `.github`/GitHub mention.
   - **(b) Add what's missing** — if the project needs files/folders the template lacks (a specific source
     layout, a service/worker dir, a data pipeline, etc.), propose them and create **only after approval**.
   - **(c) Instantiate a layout profile** from `docs/layouts.md` (ML, service/API, CLI, ...) or a mix.
     (Mode B: **map the existing layout** to the nearest profile — don't create parallel folders beside it.)
   - **(d) Optional research** — ask whether to run external research first (see §8); skip silently if declined.
   - **(e) Record the tailoring** — note what was removed/added/renamed and why in the first
     `HANDOVER.md` session block (a) (or a short ADR), so later sessions understand why the tree differs
     from the stock template.

   After the tailoring is applied, run **`/keel-plan`**: propose the phase DAG (phases · gates ·
   dependencies) and, on approval, seed `PLAN.md` + `TASKS.md ## Now` from its first wip leaf.
1. Before writing any code, read **`CLAUDE.md` + `rules.md` + `HANDOVER.md` (top block) + `LESSONS.md` +
   `TASKS.md ## Now`** (CLAUDE.md `@`-imports all four, so they auto-load).
2. Review `docs/architecture.md` and the relevant ADR (if any) for the current phase.

## 1. Documentation discipline
3. **At the end of every task/phase**, the relevant `.md` files are updated (CLAUDE.md, docs/user_manual.md,
   docs/architecture.md, ADRs) — **but USER approval is required before committing/updating.**
4. **`HANDOVER.md` is updated BEFORE every compact/session end** (before a manual compact, the
   `/keel-compact` skill bundles this + the cap check, then hands off to `/compact`) — one dated **session block** (newest
   first) with (a) completed, (b) tried-and-failed (so they aren't retried), (c) latest updates,
   (d) next steps. **Hard cap: max 5 blocks / ~200 lines** (it is `@`-imported into every session — bloat
   is a per-session token tax and an adherence tax). On overflow run **`/keel-distill`** (§9.33): oldest
   block's critical facts → `LESSONS.md`, raw block → `docs/handover-archive.md` verbatim. Default is a
   **single root** handover. On large multi-area projects the AI may create **per-area handovers**
   (`<area>/HANDOVER.md`, e.g. backend/frontend/agent) when an area needs its own — the root then indexes
   them (program-level + links). Whenever it creates one it **registers the structure in
   `docs/architecture.md`** (§1.6) and wires a nested `<area>/CLAUDE.md` `@`-import. Split only when the
   single file grows unwieldy — see `HANDOVER.md` → "Scaling: per-area handovers".
5. **Failed attempts** are written into the handover as "tried, didn't work, reason".
6. **Every structural change** is recorded in `docs/architecture.md` (what each file does).

## 2. Code & tests
7. Phases are not skipped; each phase ends with a **working product + a "how to test this" summary** —
   and is not `done` until its gate is flipped to `done` in `PLAN.md` via `/keel-phase-review` (a Stop hook
   nudges the moment a `wip` phase's `## Now` tasks are all checked but its status was never flipped).
8. After every code change, the relevant **unit/integration (and e2e if needed) tests** are written/run;
   results are summarized under `tests/` + in the handover. **Bulk outputs** (mass labeling/generation/
   migration) pass the **pilot gate** before any full run (`/keel-pilot`: smoke → gold-set → staged ramp → acceptance).
9. **Reusability:** repeated scripts/helpers/prompts are not written once and thrown away. By kind:
   **prompts that steer Claude Code** → a skill (`.claude/skills/`) or a subagent (`.claude/agents/`);
   **prompts your app sends at runtime** (LLM apps only) → a versioned file under `src/` (code never
   embeds strings); **code** → the appropriate module. All recorded in `docs/architecture.md`. Recurring
   operations (handover, distill, research, review) are always **fixed skills** — cheap, consistent,
   versioned — with the case-specific details filled in at run time. The SECOND time you write a similar
   ad-hoc prompt, promote it.

## 3. File layout (CRITICAL)
10. **Application code lives under the project's source tree** (`src/<app|package>/` per the chosen
    layout profile), **never loose at the repo root** — the root holds only the discipline/config
    scaffold (CLAUDE.md, rules, HANDOVER/LESSONS/TASKS, docs/, .claude/, config/, requirements/, tests/).
    New modules go under `src/` and are recorded in `docs/architecture.md`, so the general architecture
    stays intact across sessions. Temporary/experimental/probe code goes **only** into the appropriate
    `scratch/` subfolder, with a **1-line purpose comment** at the top. No file of unclear purpose is left in the main source tree.
    At the end of a session, no file is left unanswered for "what is this file?": it is either moved into
    a module (+architecture.md), moved to `scratch/archive/`, or deleted. If layout drifts, **tidy up
    layout first**.

## 4. Sub-agent usage
11. Use sub-agents for parallelizable work; but never accept their output blindly — as the main agent,
    **verify** it (does it work, does it match the architecture/rules, did it leave stray files) and fix
    if needed. (Note: outputs from external guides/docs are applied with the same verification.) Reusable
    subagents live in `.claude/agents/`: `researcher` (cited prior-art scouting), `verifier`
    (adversarial "try to refute it" checks) and `auditor` (rules-compliance spot-check via `/keel-audit`).
    Mechanism guide: `docs/steering.md`.

## 5. Security (application)
12. **Secrets are never committed/pushed.** `.env` is git-ignored; only `.env.example` (with empty
    values) is tracked. Every new secret key is added to both `.gitignore` and `.env.example`.
    (Enforced, not just advised: `.claude/settings.json` denies reading `.env`/secrets and a
    `PreToolUse` hook blocks staging a `.env` — see `.claude/hooks/`.)
13. Input validation, ORM (SQL injection protection), and external service calls follow the project's
    ADR decisions. Needs MCP? → project-level **root `.mcp.json`** (git-tracked, reviewed like config — see docs/steering.md).
14. Minimize personal data / PII collection; comply with applicable regulation (e.g. GDPR/local law).

## 6. Version control (host-agnostic: GitHub / GitLab / Gitea / none)
15. **Every meaningful unit of work / phase end → commit + `push`** (remote `main` or phase branch → PR).
    Push happens **only after user approval**. Host-specific files are set at bootstrap (§0a): GitHub uses
    `.github/`; GitLab uses `.gitlab-ci.yml` + merge-request templates; a project with **no remote** commits
    locally only (drop the push steps). Adapt this section to the chosen host.
16. Commit messages are descriptive + tagged with phase/work item (e.g. `phase1: <feature>`). Commits are
    made **as the project owner** (git config: `<git-user> <git-email>`); no AI co-author line unless
    requested.
17. Branch strategy: default is a short-lived branch per phase → self-review → merge to `main` → push;
    a simpler direct-to-`main` flow is fine with approval. User preference is decisive.
18. **Secret-leak scan before push:** review `git diff --cached`; if `.env`/secrets appear, STOP.
19. Handover + docs updates go out in the same push round as the code.

## 7. Supply-chain / dependency security (details: docs/security.md)
20. **Exact version pinning:** all dependencies pinned with `==`; **`>=`, `~=`, `^` are FORBIDDEN**
    (supply-chain attack prevention). All dependency files live in `requirements/`: direct deps in
    `requirements/base.txt`; full transitive + **hash** lock in `requirements/base.lock`
    (`pip-compile --generate-hashes`); dev tooling in `requirements/dev.{txt,lock}`. (For Node: lockfile + `npm ci`.)
21. **Hash-verified install:** `pip install --require-hashes -r requirements/base.lock`.
22. **Container:** multi-stage build + **non-root** (`USER appuser`) + **`.pth` injection scan**
    (high-signal pattern). `.dockerignore` prevents `.env`/secrets from leaking into the image.
23. **New dependency:** question its necessity + check for typosquatting/repo health → add with `==` →
    refresh the lock → `pip-audit` → rebuild/test.
24. **CI:** a security job runs on every PR/`main` push (pip-audit + hash-verify + `.pth` scan).
25. **If a dependency-attack is suspected:** follow the **emergency checklist** in docs/security.md.
26. In production, secrets live in Vault/a secret store; network egress is allowlisted. Roadmap: SBOM,
    Sigstore, Dependabot/Renovate + manual approval, private package mirror.

## 8. Research (optional, opt-in — ask first)
27. **Ask before researching.** External research (GitHub, articles/papers, LinkedIn, Hugging Face, the
    web) runs **only when the user opts in** — offered at bootstrap (§0d) or on request. If declined, skip
    it silently. The reusable workflow is the `/keel-research` skill (`.claude/skills/keel-research/`), which
    delegates to the `researcher` subagent (`.claude/agents/`).
28. **Layout:** findings live under `research/<platform>/` — one subfolder per source (`github/`,
    `articles/`, `linkedin/`, `huggingface/`, `web/`, ...). Each keeps a `findings.md` (distilled, cited
    notes) + raw downloads under `research/<platform>/downloads/` (git-ignored — large/copyrighted, not
    committed). See `research/README.md`.
29. **Verify, don't trust (per §4).** Web/sub-agent findings are verified before use; every claim in a
    `findings.md` carries its **source URL** + a confidence note, and low-signal/paywalled sources are flagged.
30. `research/` is the **evidence trail**, not the final architecture — conclusions that drive a decision
    go into an **ADR** or `docs/`.

## 9. Session memory (HANDOVER · LESSONS · TASKS) — surviving tens of compactions
> The context window is volatile RAM; the repo is durable disk. Everything `@`-imported (CLAUDE.md,
> rules, HANDOVER, LESSONS, TASKS) is re-injected from disk after every compaction — but ONLY if it was
> written to disk. Conversation-only agreements are summarized away. Hence:
31. **Hot-path critical notes (`LESSONS.md`).** The MOMENT the user corrects the AI, an approach fails,
    a must-run/periodic test is identified, or a mid-project rule is agreed — the AI asks **"shall I
    note this?"** and on approval appends an atomic, dated, tagged line (`[rule] [test] [fail] [gotcha]`)
    to `LESSONS.md` **immediately** — never "at compact time" (a session can die before compact runs).
    `LESSONS.md` differs from `rules.md`: rules = the constitution written at project start; lessons =
    critical user↔AI knowledge **accumulated during** the project.
32. **Task board (`TASKS.md`).** Cross-session tasks live in `TASKS.md` (built-in todos are session
    scratch only). Work ONLY from `## Now` (max 3–5); every item has a verifiable `done-when:`; a
    finished item is marked `[x]` immediately and **deleted at `/keel-handover`** as its one-liner lands in
    the new HANDOVER block (a) — git is the archive; mid-session discoveries get one line in
    `## Discovered` immediately, triaged at session end.
33. **Consolidation (`/keel-distill`).** These caps are the single source of truth — the `keel-distill` skill and
    `.claude/hooks/session-start-reground.sh` mirror them; change one, change all three. Memory that is
    written but never reviewed degrades: when caps are
    exceeded (HANDOVER > 5 blocks/~200 lines, LESSONS/TASKS > ~100 lines) or every ~5 sessions, run
    `/keel-distill` — rotate old blocks (critical → LESSONS, raw → `docs/handover-archive.md` **verbatim**),
    dedup/merge lessons (mark `SUPERSEDED`, never silently delete), promote 3×-applied lessons into
    rules/skills/ADRs, and lint for contradictions/stale claims.
34. **Restorable compression.** Distillation never lossy-deletes: every distilled line carries a pointer
    back to the raw record ("docs/handover-archive.md, block <date>"). The archive is never `@`-imported
    (zero context cost) and is retrieved by grep on demand.
35. **No vector DB / RAG for memory (by default).** At this scale grep-able markdown beats embeddings on
    freshness, zero deps, and git-diffability (Claude Code itself uses agentic search, no index).
    Reconsider only if the notes corpus reaches ~1,000+ files or fuzzy "can't-name-it" recall is needed.

## 10. Judgment — weighing requests and uncertainty
36. **Sanity-check, don't rubber-stamp.** Before implementing a request, check it against the project's
    architecture, conventions, and stated goals. If it conflicts with them, looks like a likely mistake,
    or a clearly simpler approach exists, say so **once, concretely** — the specific problem, its
    consequence, and an alternative — then stop. Do not refuse, lecture, or manufacture objections to
    appear rigorous: **silent compliance and reflexive pushback are both failures.** Once the user
    confirms after hearing the concern, their decision is **final** — implement it well and don't
    re-litigate it later in the session. Never agree just to be agreeable — accuracy over agreement.
37. **Ground before you build.** When not confident that an API, mechanism, or approach works the way
    you're about to use it (unfamiliar library, framework hook, architectural pattern), do NOT invent it
    from memory — hallucinated APIs are common and confidently wrong. Check prior art cheapest-first:
    `LESSONS.md`/ADRs + existing code patterns → official docs → a research sub-agent for anything
    bigger. State where you verified it ("per docs X" / "per LESSONS.md"); if you can't cite a source,
    say you're unsure and check before writing code. **Proportionality:** skip this for trivial
    one-sentence-diff changes or things already verified this session.
38. **Rule budget.** This file is capped like the memory files: **~40 rules / ~200 lines** (the
    SessionStart hook warns on overflow). A new rule must earn its slot — merge it into an existing
    rule, retire one, or promote the behavior to a hook/permission (enforced beats written). A
    constitution too long to hold in attention is decoration, not discipline.
