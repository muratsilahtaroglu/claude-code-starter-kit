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
2. **Each worker's domain** — mission (one line), scope paths (globs), anything it must NEVER touch.
3. **Charter/prompt language** — EN or TR (the project's docs language usually decides).
4. **Review routing notes** — the default is review-v2 (rules §10.41): the orchestrator routes every
   review and delegates the mechanical half to the `verifier` subagent; name any area that instead
   deserves a DEDICATED reviewer agent (rare — each extra agent is a chat window the owner must steer).

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
    - Lane: TASKS.md `### <name>` holds your ASSIGNMENTS and is READ-ONLY for you (§10.42
      write-surface split — same-machine sessions have no git merge layer, shared files get ONE writer):
      refresh your mirror from it at session start; NEVER edit TASKS/LESSONS/HANDOVER/the index.
    - Workboard — your ONLY write surface besides spec/fix files: `reports/team/<name>/board.md` with
      three sections: lane MIRROR (id · done-when · live status/progress) · findings INBOX
      (`[gotcha]/[fail]/[rule]` lines the MOMENT they happen, §9.31 — orchestrator promotes them) ·
      REQUESTS to the orchestrator (blockers, out-of-scope finds). Delivering: solution-note FILE in
      your folder + mark `delivered` on YOUR board — the orchestrator moves the TASKS item to
      `## Review` and writes the index line (§10.40 file-first).
    - Author folder: `reports/team/<name>/` — board.md, specs (+ Comprehension log, §10.41), solution notes, evidence.
    - Review: routing is the orchestrator's alone — never pick your own reviewer (§10.41).
    - FORBIDDEN (worker, rules §10.42): WRITE-rituals (handover · distill · compact · phase-review ·
      audit · plan · update · tidy), commit/push, editing anyone else's lines, memory curation.
      Allowed read-only: /keel-start, /keel-agent-team-start.
    - Language: <EN|TR>.

The ORCHESTRATOR charter (`Role: orchestrator`) inverts the duties: it runs the rituals + git
(commit; push stays ask-gated), assigns lanes/@tags, routes EVERY review (delegating the mechanical
half — it does not re-measure deliveries inline), curates memory (single-writer surfaces: it reads
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
