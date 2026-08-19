# rules.md — Working rules (GENERIC TEMPLATE)

> Project-agnostic discipline. Use as-is in the new project; fill in the `<...>` blanks.
> These rules apply every session.

## 0. Session start
0. **(First session only) Bootstrap — fit the template to THIS project.** Before anything else, understand
   the project (goal, type, constraints, target platforms/hosts) and ask the **project language** (e.g.
   Turkish or English) for docs — that choice governs the HUMAN surfaces (docs, TASKS.md, PLAN.md,
   `reports/team/*`); the MACHINE-memory files (HANDOVER.md · LESSONS.md · worker boards) are ALWAYS
   English regardless (§9.31 language rule). Then propose a tailoring plan and **apply it only after user approval** —
   never silently keep, delete, add, or **overwrite**. First pick the mode:

   - **Mode A — New / greenfield project** (empty or near-empty repo): the template files are the starting
     point. Go straight to the tailoring plan (a)–(e) below.
   - **Mode B — Adopt into an EXISTING project** (brownfield): the project already has code + history;
     the template is *overlaid, never dumped on top*. **Non-destructive is the hard rule** — their
     `.git` is KEPT (never re-init, no `rm -rf .git`), only MISSING paths are added, and anything
     present or conflicting is merged from a shown diff with approval, never overwritten. Run
     **`/keel-adopt`**, which carries the procedure (inventory & classify · back-fill
     `docs/architecture.md` + HANDOVER (a) from the REAL code, not placeholders · adopt §7 security as
     a migration that doesn't break a working build · record the adoption as an ADR) before (a)–(e).

   The tailoring plan (both modes) covers:
   - **(a) Prune what's unneeded** — list template parts to remove *with reasons*, then **cascade the
     removal**: grep the removed part's name across every `.md` (README.md, CLAUDE.md, docs/* incl.
     `docs/user_manual.md`, HANDOVER.md, folder READMEs) and **update or delete every reference** so no
     dangling mention or architectural confusion remains — dropping GitHub means `.github/` AND §6 AND
     every README mention, in the same pass.
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
   (d) next steps — in ENGLISH (machine-read memory, §9.31). **Hard cap: max 3 blocks / ~150 lines** (it is `@`-imported into every session — bloat
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
   `make test` auto-logs each run to `reports/tests/` (dated; summary → handover; a why-one-liner per test file in its folder README — `tests/README.md`);
   **bulk outputs** (mass labeling/generation/migration) pass the **pilot gate** before any full run (`/keel-pilot`).
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
    a module (+architecture.md), moved to `scratch/archive/`, or deleted — **unless a permanent artifact
    CITES it**: a probe named by a `reports/` note, ADR or doc is that claim's EVIDENCE (§10.40), so it
    stays put and its AGE is no argument (`/keel-tidy` sweeps by citation, never by date). If layout
    drifts, **tidy up layout first** (`/keel-tidy`).

## 4. Sub-agent usage
11. Use sub-agents for parallelizable work; but never accept their output blindly — as the main agent,
    **verify** it (does it work, does it match the architecture/rules, did it leave stray files) and fix
    if needed. (Note: outputs from external guides/docs are applied with the same verification.) Reusable
    subagents live in `.claude/agents/`: `researcher` (cited prior-art scouting), `verifier`
    (adversarial "try to refute it" checks) and `auditor` (rules-compliance spot-check via `/keel-audit`).
    Mechanism guide: `docs/steering.md`.
    **Self-check before you deliver:** nothing is marked `delivered` straight from your own keyboard —
    an INDEPENDENT sub-agent code-reviews the diff first (scope: changed files + what the `done-when`
    CLAIMS; a measurement claim gets its probe re-run), findings fixed and re-reviewed until clean;
    the orchestrator gates its OWN changes the same way before committing. Its output still isn't
    taken blindly (verify each finding, record why one was rejected), and it never replaces §10.41's
    routed review — you still don't pick your own official reviewer.

## 5. Security (application)
12. **Secrets are never committed/pushed.** `.env` is git-ignored; only `.env.example` (with empty
    values) is tracked. Every new secret key is added to both `.gitignore` and `.env.example`.
    (Enforced, not just advised: `.claude/settings.json` denies reading `.env`/secrets and a
    `PreToolUse` hook blocks staging a `.env` — see `.claude/hooks/`.)
13. Input validation, ORM (SQL injection protection), and external service calls follow the project's
    ADR decisions. Needs MCP? → project-level **root `.mcp.json`** (git-tracked, reviewed like config — see docs/steering.md).
14. Minimize personal data / PII collection; comply with applicable regulation (e.g. GDPR/local law).

## 6. Version control (host-agnostic: GitHub / GitLab / Gitea / none)
15. **Commit at every meaningful unit of work; PUSH in a batch at a boundary** (phase end, or session end /
    `/keel-compact`) — ONE approval, not a prompt per commit. Push happens **only after user approval** (the
    `ask` on push stays — the enforced backstop, never removed). Host files set at bootstrap (§0a): GitHub
    `.github/`; GitLab `.gitlab-ci.yml` + MR templates; **no remote** = commit locally only.
16. Commit messages are descriptive + tagged with phase/work item (e.g. `phase1: <feature>`). Commits are
    made **as the project owner** (git config: `<git-user> <git-email>`); no AI co-author line unless
    requested.
17. Branch strategy: default is a short-lived branch per phase → self-review → merge to `main` → push;
    a simpler direct-to-`main` flow is fine with approval. User preference is decisive. Multi-user
    projects adopt what the HOST can enforce — same-repo branch→PR, or **fork→PR** where developers are
    Read-only (docs/steering.md "Multi-user") — and rewrite this §6 to match (ADR it, §10.40).
18. **Review what you stage — for secrets AND for provenance.** Secrets: read `git diff --cached`;
    if `.env`/secrets appear, STOP. Provenance: `git add -A` / `git add .` is FORBIDDEN whenever
    another writer may be active (a co-agent §10.42, a teammate, an open editor) — stage EXPLICIT
    paths after reading each modified file's diff; "this `M` must be mine" is an unverified
    attribution (§10.37) and sweeping someone's in-flight work into your commit mislabels both
    (field: twice in one day). A shared file may also hold a STALE buffer in someone's editor that
    silently overwrites the repo copy on their next save — re-check `git status` mid-round;
    `git checkout HEAD -- <file>` and re-apply when in doubt.
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
24. **CI:** a security job runs on every PR/`main` push (pip-audit + hash-verify + `.pth` scan) —
    **shaped to the §6 contribution model:** fork PRs receive NO repo secrets, so the gating suite must
    pass secret-less (a live-cred/network test SKIPs, never fails); a bootstrap that pruned `.github/`
    reverses the prune at team scale-up (ADR addendum, never a silent re-add).
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
    critical user↔AI knowledge **accumulated during** the project. **Machine-memory language =
    ENGLISH:** HANDOVER/LESSONS/worker boards are read by sessions, not humans — EN costs fewer
    tokens per always-imported line; write them in English on every project regardless of the
    project language (the user's verbatim words may stay quoted in their language; human surfaces —
    TASKS/PLAN/reports/docs — follow the project language; owner-facing questions are surfaced in
    CHAT in the project language, the file line stays EN — and a LANGUAGE-SPECIFIC domain fact
    (morphology, a locale's casing/collation trap) keeps its example in that language: translating
    the example destroys the lesson).
32. **Task board (`TASKS.md`).** Cross-session tasks live in `TASKS.md` (built-in todos are session
    scratch only). Work ONLY from `## Now` (max 3–5); every item has a verifiable `done-when:`; a
    finished item is marked `[x]` immediately and **deleted at `/keel-handover`** as its one-liner lands in
    the new HANDOVER block (a) — git is the archive; mid-session discoveries get one line in
    `## Discovered` immediately, triaged at session end.
    **Ids are per-lane and stable** (`co1`,`fro2`): a lane's lowercase prefix is fixed when the
    lane is born, numbers are allocated by the ORCHESTRATOR only, and an id is NEVER renamed or
    reused — reports, `scratch/<id>/` and citations carry it (§10.40). Reassignment moves the id
    WITH the work; per-agent throughput is counted from the author folder, not the prefix.
33. **Consolidation (`/keel-distill`).** The caps are SOLO DEFAULTS — a team project tunes them in
    `.claude/keel-caps` (§10.40); the SessionStart hook reads that file, skills/headers follow it. Memory
    written but never reviewed degrades: when caps hit (defaults: HANDOVER > 3 blocks/~150 lines, LESSONS > ~250, TASKS >
    ~100 lines) or every ~5 sessions, run `/keel-distill` — rotate old blocks (critical → LESSONS,
    raw → `docs/handover-archive.md` **verbatim**), dedup/merge lessons (mark `SUPERSEDED`, never
    silently delete), promote 3×-applied lessons into rules/skills/ADRs (file-scoped ones → a
    `paths:`-scoped `.claude/rules/` rule, or a `paths:`-scoped SKILL when the cluster must survive
    a mid-task compaction; **promotion DELETES the entry** — its one pointer is a router line in
    LESSONS `## Index`, never a "moved to X" stub), and lint for contradictions.
    **A memory file's HEADER is doctrine, not state:** it says how the file works, is written once and
    frozen, and carries no date, measurement, pending decision, cap NUMBER (`.claude/keel-caps` is the
    authority — a copy drifts) or chat quote; those go in the BODY or the proper board. Detail that
    merely restates these rules lives in `docs/memory-files.md`, not in a header paid every session.
34. **Restorable compression.** Distillation never lossy-deletes: every distilled line points back to the
    raw record ("docs/handover-archive.md, block <date>"); the archive is never `@`-imported — grep it on demand.
35. **No vector DB / RAG for memory (by default).** Grep-able markdown beats embeddings on freshness,
    zero deps, and git-diffability; reconsider only at ~1,000+ note files or fuzzy "can't-name-it" recall.

## 10. Judgment — weighing requests and uncertainty
36. **Sanity-check, don't rubber-stamp.** Before implementing a request, check it against the project's
    architecture, conventions, and stated goals. If it conflicts with them, looks like a likely mistake,
    or a clearly simpler approach exists, say so **once, concretely** — the specific problem, its
    consequence, and an alternative — then stop. Do not refuse, lecture, or manufacture objections to
    appear rigorous: **silent compliance and reflexive pushback are both failures** — accuracy over
    agreement. Once the user confirms, their decision is **final** — implement well, don't re-litigate.
37. **Ground before you build.** When not confident that an API, mechanism, or approach works the way
    you're about to use it (unfamiliar library, framework hook, architectural pattern), do NOT invent it
    from memory — hallucinated APIs are common and confidently wrong. Check prior art cheapest-first:
    `LESSONS.md`/ADRs + existing code patterns → official docs → a research sub-agent for anything bigger.
    State where you verified it ("per docs X"); no citable source = say you're unsure and check first.
    **Proportionality:** skip for trivial one-sentence diffs or things already verified this session.
    **A surprising measurement indicts your own INSTRUMENT first.** Before reporting "the system is
    wrong", re-derive the reference: assumed window/argument semantics, invented parameters, defaults
    that don't match, raw vs. deduplicated counting. Report the discrepancy only once the instrument
    is cleared — and say which side you checked. (Field: bit four times in one project; a probe's
    exclusive `< end` against a tool's inclusive end manufactured a suspiciously clean ratio, and a
    raw `count()` reference read ~17% high on unmerged row versions — the TOOL was right both times.)
38. **Rule budget.** Capped like the memory files: **~400 lines**, `.claude/keel-caps`-tunable (the
    SessionStart hook warns on overflow). A new rule must earn its slot — merge it into an existing
    rule, retire one, or promote the behavior to a hook/permission (enforced beats written); a
    constitution too long to hold in attention is decoration. The stock TEMPLATE is ~290 of those
    lines, so **your project's own rules get ~110** — the budget line is drawn there, not at the
    template. (It was ~300 total until 2026-08-18, which measured out as ~6 lines for the project and
    forced every real project to raise the cap on day one — the default was wrong, not the projects.)
    Template text that merely restates a skill is compressed to the invariant + the pointer.
39. **Fix the class, not the instance.** When a fix targets one failing case (a query, a test, an input),
    find the mechanism-level cause and fix THERE — never hard-wire case-specific instructions into
    runtime prompts or code so one example passes. Verified = a **variant case the fix was not built on**
    also passes + the original failing case joins the regression/golden set (§2.8, `tests/fixtures/`).
    A deliberate point-fix is OK only when **declared**: "point fix — generalize later" in TASKS/LESSONS.
    Proving a fix by REMOVING it (revert-sensitivity) has a mandatory order: fix → tests green →
    **COMMIT** → remove → show the break → restore (on an UNCOMMITTED fix the `git checkout` ending
    the probe deletes the fix too); remove in file+suite order — a cached loader hides it otherwise.
40. **Team scale-up** (one-run setup: `/keel-team`). Memory caps GROW with headcount: the AI PROPOSES a raise (a starving board, a 5+
    person `## Now`) and on approval pins it in **`.claude/keel-caps`** (`KEY=NUMBER` per line: HANDOVER ·
    LESSONS · TASKS · RULES · HANDOVER_BLOCKS) — owner-only, `/keel-update`-safe, never raised silently.
    `TASKS.md` stays LEAN at any size: an item = id + `@owner` + `due:` + done-when; the detailed SPEC
    (requirements, manual test scripts) is an owner-approved SPEC file and every delivery ships a
    SOLUTION NOTE (problem → root cause → fix + why → changed files → tests). **A delivery exists
    only as its file:** a chat summary is NOT a delivery — an item may not move to `## Review`
    without its note's path on the line (the reground hook flags pathless lines AND files missing on
    disk), and each delivery walks ONE state chain: `wip → delivered → verified (owner part: <one
    sentence>) → closed <date> accepted|rejected`. Team reports file
    per AUTHOR — `reports/team/<@tag>/<task>_spec.md` / `<task>_fix_<date>.md` (+ evidence subfolders;
    **Markdown only**) — each carrying ONE line in the `reports/team/README.md` index, which IS the
    team's review todolist ("what's finished under @X" = the `[x]` lines in their section; exact
    format, status vocabulary and who-flips-what live in that template — on same-machine agent teams
    the orchestrator writes every transition, §10.42). Reports are never deleted — they are the
    permanent artifacts other files cite (§ steering "Team reports"); findability lives in the
    index. ONE sanctioned move: at `/keel-distill`, a `closed` task's files sweep into the author's
    `done/` subfolder WITH every citation rewritten in the same pass (the flat folder shows only
    live work); nothing else moves them. Every developer must be able to run the product LOCALLY from
    their own `.env` + Makefile overrides (steering "Dev-local runs") — "runs only on the owner's
    machine" is a bootstrap bug, not a norm.
41. **Human ownership (AI-assisted ≠ AI-verified).** The assignee OWNS their delivery: the human/manual
    part of a `done-when` (eyes-on tests, live checks) is performed PERSONALLY — an AI-run check never
    substitutes for it, and evidence names WHO ran WHAT, HOW. **Comprehension gate — before work
    starts on EVERY task** (assigned or not, the owner's own included): the session briefs it and
    confirms understanding with 2–3 questions that are SPECIFIC to this task's spec/done-when (one
    that would fit any task is a violation) and SELF-EXPLANATORY (they carry their own context and
    ask why/consequence — a bare yes/no teaches nothing). Q&A lands dated in the task's spec
    (`reports/team/<@tag>/<task>_spec.md` "## Comprehension log"), which makes the gate IDEMPOTENT:
    READ the log first — an answered question is NEVER re-asked, so a task spanning sessions/compacts
    resumes from it. Work waits for confirmation; the assignee advances KNOWING what they do.
    At `## Review`, ROUTING is the orchestrator's alone (owner's main session, or the leader agent
    under §10.42): a deliverer never picks their own reviewer, and the MECHANICAL half (re-running
    done-whens, parity scripts, source reads) is DELEGATED to a verifier whose written report flips
    the line to `verified (owner part: <one sentence>)` — the owner's time goes to what only a human
    can do. There the owner probes the same understanding proportionally: a delivery its author
    cannot explain is REJECTED to `## Now` ("comprehension gap"). Binds work carrying
    test/verification claims or changing product behavior (owner may waive trivia); applies to
    EVERYONE, the owner included (their probe = the phase-review gate).
42. **Parallel sessions — co-agents and agent teams** (mechanism + setup: docs/steering.md "Agent
    teams", `/keel-agent-team-create|-start`; the roster is OWNER-only like all governance).
    Extra Claude sessions in the same repo may work the board like teammates — unlike a sub-agent
    they keep their own chat history, so the owner inspects and steers them mid-task. Each gets its
    own lane (`### <name>` / `@<name>` in TASKS) + author folder (`reports/team/<name>/`, §10.40),
    and runs INTERMEDIATE work only. FORBIDDEN to a worker/co-agent: rituals/skills (handover ·
    distill · compact · phase-review · audit), commit/push, and rewriting anyone ELSE's lines.
    Rituals, git, assignment, review ROUTING (§10.41) and memory curation belong to the MAIN session
    / ORCHESTRATOR alone — which takes no work items itself and READS fresh worker writes
    (`git status`/`git diff`) before curating anything away.
    **Write-surface split — the race is closed by construction, not discipline:** humans on separate
    machines are merged by GIT; same-machine sessions have NO merge layer, so every shared memory
    file (TASKS · LESSONS · HANDOVER · reports index · PLAN) has exactly ONE writer — the
    orchestrator. A worker writes only in its own folder: `reports/team/<name>/board.md` (lane mirror
    refreshed read-only from TASKS · findings inbox on the §9.31 hot path · requests) plus its
    spec/fix files; the orchestrator SYNCS boards into the shared files each work block with
    `@<name>` attribution. Without this, two writers clobber each other SILENTLY (field case:
    alice_v2 2026-08-12, fresh progress nearly overwritten twice during a cap pass).
    **Star, not mesh — and WOKEN, not polling:** the orchestrator assigns, workers report back to IT,
    and worker→worker messaging is BLOCKED by a hook (a permission rule cannot decide by target; and
    a decision two workers reach alone is one no shared file records). A message WAKES an idle peer
    session and fires SessionStart, so identity and memory return from disk — hence no sleep loops
    anywhere: `/keel-continue` ends in IDLE and stops. Each chat is `/rename`d to its agent, because
    that name IS the messaging address. A message is a POINTER; the delivery is the file. Deliveries
    land in `## Review`; §10.41 + the §4.11 verify duty apply unchanged.
