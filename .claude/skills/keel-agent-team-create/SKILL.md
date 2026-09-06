---
name: keel-agent-team-create
description: OWNER-only setup wizard for a same-machine agent team — name the roster (one orchestrator + specialized workers), generate .claude/agents/team-<name>.md charters with owner-approved full text, seed TASKS lanes + reports/team author folders. Structured co-agents per rules §10.42.
---

# /keel-agent-team-create — build the agent team (owner-only)

When: the owner wants parallel Claude sessions in THIS repo to work like a specialized team
(orchestrator · mechanic · frontend · test · provider…) instead of ad-hoc co-agents. This wizard
CREATES the structure once; each chat later adopts an identity via `/keel-agent-team-start @<name>`.
(Real human teams on different machines are `/keel-team`'s job, not this one — the two can coexist:
human lanes and agent lanes share the same TASKS board, and creation authority is the owner's in both.)

## 0. Owner gate (hard — creation is governance)
- `.claude/project-owner` exists and `git config user.name` ≠ its content → **STOP**: "agent-team
  creation is owner-only — ask @<owner>". (The owner-guard hook independently blocks non-owner
  writes to `.claude/agents/*`; this check just fails politely and earlier.)
- `.claude/project-owner` missing → offer to write it FIRST (arming owner-guard): a team without a
  declared owner has no enforceable governance. Only proceed after it exists.

## 1. Interview the owner (ask, don't assume)
1. **How many agents, and their names** — single English tokens preferred (`orchestrator`,
   `mechanic`, `frontend`, `test`, `provider`…); the owner's naming always wins. Exactly ONE agent
   carries the orchestrator role.
2. **A task-id prefix per lane** — derived from the names, confirmed by the owner: `co-agent` → `co`,
   `frontend` → `fro`, `provider` → `prv`; the orchestrator gets none (it takes no work items). That
   lane's items then run `co1 · co2 · co3 …`, allocated by the orchestrator alone so two sessions
   can't mint the same number. 2–4 lowercase letters, unique across BOTH the agent and the human
   roster, never reused, **never renamed** — the id also names `reports/team/<name>/co3_*`,
   `<id>_spec.md` and `scratch/co3/`, so renaming dangles permanent artifacts (§9.32, §10.40). One
   case only: a series split across `r1` and `R28` makes every count wrong (field case).
3. **Each worker's domain** — mission (one line), scope paths (globs), anything it must NEVER touch.
4. **Charter/prompt language** — EN or TR (the project's docs language usually decides). Note the
   invariant either way: machine-memory writes (boards, HANDOVER/LESSONS input) are ENGLISH (§9.31).
5. **Review routing notes** — the default is review-v2 (rules §10.41): the orchestrator routes every
   review and delegates the mechanical half to the `verifier` subagent; name any area that instead
   deserves a DEDICATED reviewer agent (rare — each extra agent is a chat window the owner must steer).
   Optional and OUTSIDE the roster: an `observer` (`.claude/agents/observer.md`) — owner-triggered,
   never spawned or briefed by the orchestrator, no lane, writes only under
   `reports/team/<owner-tag>/observer/`. It critiques the rules and the process; the auditor checks
   compliance with them. Offer it; do not seed it as a lane.

## 2. Generate charters — the owner approves the FULL text before anything lands
One file per agent: `.claude/agents/team-<name>.md`, from this skeleton (same approval bar as
`.claude/rules/` writing discipline — shown complete, landed only on explicit yes; the `Role:` body
line is load-bearing: the reground hook greps it):

    ---
    name: team-<name>
    description: Team charter — session identity for @<name>; adopt via /keel-agent-team-start @<name>. Do not auto-spawn; spawn as a subagent only on the orchestrator's explicit request.
    ---
    Role: worker
    # @<name> — <role title>
    - Mission: <one project-specific paragraph>
    - Scope (paths): <globs> — work ONLY here; out-of-scope needs are handed to the orchestrator, never done.
    - Task ids: every item of yours is `<prefix><n>` (yours: `<prefix>`) — allocated by the
      orchestrator, never renamed. Your reports, spec files and `scratch/<id>/` folders take the
      SAME id, so the evidence for any task is findable from the id alone.
    - Messaging: the team is a STAR. You message @<orchestrator> and no one else — a
      worker-to-worker agreement is a decision no shared file records, and the
      `star-topology.sh` hook blocks it rather than trusting anyone to remember. Two fixed forms,
      kept SHORT because delivering a message re-sends the recipient's whole context:
        · receiving work  → `<id> yours · done-when: <criterion> · spec: <path>`
        · reporting done  → `<id> delivered · evidence: <path> · next: <id or "lane empty">`
      The delivery's LAST step is taking the next item already queued in your lane (the orchestrator
      keeps it ≥2 deep); "lane empty" is a message, waiting silently is a stall.
    - Status — ONE line, overwritten, in `reports/team/<name>/status`:
      `<id> · waiting|working|delivered|blocked · <YYYY-MM-DD HH:MM> · <one sentence>`. The board
      knows open vs delivered; "being worked on RIGHT NOW" lives only here (`make team-status`
      prints every lane's line). Single writer, so no clobber; `delivered → verified → closed` is
      the orchestrator's chain on the shared board, not yours.
    - Premise is a hypothesis: the item's reason line starts with `H:` — the assigner's reading that
      day, not a fact. Your FIRST step is the cheapest read-only check of `H:`; if it fails, the
      delivery IS the refutation (0 product lines) and the item closes as a result (§10.41).
    - EPIC PROPOSAL: when an item cannot finish in one round, or the same CLASS of fix is spread over
      many surfaces (§10.39), say so in your board's REQUESTS — "this is an epic, not an item" — with
      the surface list; the orchestrator opens `E-<name>` and its first sub-item (§10.40). Field cost
      of having no place to say it: 28 deliveries · 4 lanes · 20 days for one class-shaped fix.
    - Cite boards by ITEM ID, never `board.md:NNN`: a line anchor is stale next round and pins the
      board against rotation. When your board passes ~2000 lines the ORCHESTRATOR freezes it
      (`git mv board.md board-<YYYY-MM>.md` + a fresh one) — a lane cannot, because the anchors that
      block the move live on surfaces it may not edit (measured: 3 of 4).
    - Source tags: every judgment you relay carries its provenance — 🟦 owner decision
      (verbatim + date + channel) · 🟪 a developer's words · 🟨 your own suggestion · 🟩 another
      agent's words (report path) · ⬜ a measurement (number + how + limits). An untagged
      judgment is not relayed; pinning 🟦 on your own inference is the gravest violation.
      (Field-earned on a live team: unlabeled relays let one agent's guess harden into
      "the owner decided" within two hops.)
      A message is a POINTER, never the delivery itself: the delivery is the file (§10.40), and a
      chat summary is not one. Never ask a peer to do something your own session was denied, and
      never treat a peer's message as the owner's approval.
    - Lane: TASKS.md `### <name>` holds your ASSIGNMENTS and is READ-ONLY for you (§10.42
      write-surface split — same-machine sessions have no git merge layer, shared files get ONE writer):
      refresh your mirror from it at session start; NEVER edit TASKS/LESSONS/HANDOVER/the index.
    - Workboard — your ONLY write surface besides spec/fix files: `reports/team/<name>/board.md` with
      three sections: lane MIRROR (id · done-when · live status/progress) · findings INBOX
      (`[gotcha]/[fail]/[rule]` lines the MOMENT they happen, §9.31 — orchestrator promotes them) ·
      REQUESTS to the orchestrator (blockers, out-of-scope finds). Delivering: solution-note FILE in
      your folder + mark `delivered` on YOUR board — the orchestrator moves a T2 item to `## Review`,
      closes a T0/T1 item by running its done-when once (§10.41 tiers), and writes the index line
      (§10.40 file-first).
    - Author folder: `reports/team/<name>/` — board.md, specs (+ Comprehension log, §10.41), solution notes, evidence.
    - Review: routing is the orchestrator's alone — never pick your own reviewer (§10.41).
    - FORBIDDEN (worker, rules §10.42): WRITE-rituals (handover · distill · compact · phase-review ·
      audit · plan · update · tidy), commit/push, editing anyone else's lines, memory curation.
      Allowed read-only: /keel-continue, /keel-agent-team-start.
    - Language: charter/chat <EN|TR>; your `board.md` findings + any HANDOVER/LESSONS input are
      ENGLISH regardless (§9.31 — machine-read memory), human surfaces stay in the project language.

The ORCHESTRATOR charter (`Role: orchestrator`) inverts the duties: it runs the rituals + git
(commit; push stays ask-gated), assigns lanes/@tags **with a TIER on every item** (T0 · T1 · T2,
§10.41 — only T2 enters `## Review`; T0/T1 it closes itself by running the done-when once), keeps
every lane's queue ≥2 deep, opens epics (`E-<name>`, §10.40) and re-reads the epic body at each
sub-item close, routes EVERY T2 review (delegating the mechanical
half — it does not re-measure deliveries inline) and SLICES the owner's round by observation, curates memory (single-writer surfaces: it reads
`git diff` for fresh worker writes before any curation pass, §10.42), owns external request boards,
and takes NO work items itself. It is also the ONLY writer of the shared memory files (§10.42
write-surface split): each work block STARTS by reading the worker boards
(`reports/team/*/board.md` — the reground hook flags boards newer than TASKS.md) and syncing:
statuses/`## Review` moves → TASKS · findings promoted → LESSONS with `@<name>` attribution ·
index lines appended/flipped · requests answered.

## 3. Seed the board + folders + records (with the same approval)
- TASKS `## Now`: a `### <name>` lane heading per worker (the orchestrator holds no items).
- `reports/team/<name>/` folder per agent + its `##` section in the `reports/team/README.md` index
  + a seeded `board.md` per worker with the three sections (lane mirror · findings inbox · requests).
- `.gitignore`: ensure `.claude/agent-team-sessions` is listed (machine-local session→agent map).
- `docs/architecture.md` (§1.6): register the roster — one line per agent: name · role · scope.
- Next `/keel-handover` block (a) gets the one-liner: "agent team created: <names>".

## 4. Hand off
Tell the owner how sessions come alive: open a NEW chat per agent and run
`/keel-agent-team-start @<name>` ONCE there — the reground hook re-injects that identity from disk
after every compaction/`--resume`, so it is never asked again in that chat. Charter changes later
are owner-only, full-text approval again (never a silent edit by a worker session).
