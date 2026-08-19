# docs/steering.md — which Claude Code mechanism for what

Claude Code offers several ways to steer an agent; each has a different context cost, authority, and
compaction behavior. Put each instruction in the RIGHT one instead of piling everything into `CLAUDE.md`.
(Reference: Anthropic, ["Steering Claude Code"](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more).)

| Mechanism | What it's for | Loads | Survives compaction? | Authority |
|---|---|---|---|---|
| **`CLAUDE.md`** (root) | **Facts**: build commands, layout, conventions, the always-true rules (via `@`-imports) | every session, in full | ✅ re-injected from disk | guidance |
| **`.claude/rules/`** | Constraints; **path-scoped** ones (with `paths:`) load only for matching files | unscoped: always · scoped: on match | unscoped ✅ · scoped ❌ (until a match is re-read) | guidance |
| **`.claude/skills/`** | **Procedures** you want to watch/steer in the main thread (deploy, handover, review) | name+desc always · body when invoked | ✅ invoked bodies re-injected (to a budget) | guidance |
| **`.claude/agents/`** | **Side tasks** whose intermediate output would clutter the thread (deep research, audits, verification) | name+desc always · body only when called | isolated context — bypasses main compaction | guidance |
| **`.claude/hooks/`** | Things that must happen **deterministically** (block a command, snapshot, re-ground) | on lifecycle events | ✅ runs outside the context window | **enforced** |
| **`.claude/settings.json` permissions** | Hard **allow/deny/ask** on tools (deny reading secrets, ask before push) | always | ✅ | **enforced** |
| **`.mcp.json`** (repo root) | **External tool bridges** (MCP servers: DB, browser, internal APIs) — project-level, git-tracked | approved servers at session start | ✅ config on disk | tool access |

## Rules of thumb (from the Anthropic guidance)
- **"Every time X, always do Y"** or **"never do X"** → a **hook** or a **permission**, not a `CLAUDE.md`
  line. Instructions are probabilistic; only hooks/permissions are guarantees.
- **A 30-line procedure** → a **skill**, not `CLAUDE.md`. Facts go in `CLAUDE.md`; procedures go in skills.
- **A file-specific constraint** ("migrations are append-only") → a **path-scoped rule** so it stays out
  of context during unrelated work. Must it survive a mid-task compaction? → a **`paths:`-scoped
  skill** (invoked bodies re-inject, ≈5k/25k budget; a path rule waits for the next file match).
- **A read-heavy side investigation** whose details you won't reference again → a **subagent** (it returns
  only a distilled summary; the raw exploration never enters your main context).
- **Keep `CLAUDE.md` under ~200 lines** and treat it as an index pointing to the above, not a manual.
  An unscoped rule is mechanically identical to `CLAUDE.md` content: always loaded, always costing tokens.

## How Keel maps onto this
- **Always-on discipline** (`rules.md`, `HANDOVER.md`, `LESSONS.md`, `TASKS.md`) → `@`-imported by `CLAUDE.md`.
- **Procedures** → skills: `/keel-continue` (decide and continue after a compact/cold start/wake: cross-check the
  auto-loaded memory against PLAN.md + git → a "where you left off · in-flight · warnings · next step"
  brief; read-only, so even co-agents may run it),
  `/keel-agent-team-create` + `/keel-agent-team-start` (same-machine agent team: owner-only
  roster/charters · per-chat identity that survives compaction via the session map — see "Agent
  teams" under Multi-user below), `/keel-team` (human team on different machines: owner-only one-run
  setup of the whole Multi-user playbook),
  `/keel-handover`, `/keel-phase-review`, `/keel-research`, `/keel-adopt`, `/keel-distill`, `/keel-update`
  (pull the latest template with per-file approval), `/keel-audit` (rules-compliance spot-check when due),
  `/keel-plan` (phase map: status table + regenerated Mermaid DAG in `PLAN.md`), `/keel-compact`
  (pre-compact bundle: refresh the disk via `/keel-handover`, verify freshness, hand off to `/compact`),
  `/keel-pilot` (staged bulk-run gate: declare thresholds → smoke → gold-set validation → ramp → acceptance),
  `/keel-autopilot` (gated autonomy for one session: phases advance back-to-back, every gate still runs the
  full `/keel-phase-review` with real evidence, commits are local, pushes batch for ONE approval),
  `/keel-tidy` (layout-hygiene sweep, rules.md §3.10: stray/obsolete files triaged with evidence +
  approval — module-ize · delete [git is the archive] · `scratch/archive/` · gitignore the class).
- **Side tasks** → subagents: `researcher`, `verifier`, `auditor` (`.claude/agents/`).
- **Guarantees** → hooks (`block-dangerous`, `compact-gate` (blocks a stale manual `/compact`),
  `pre-compact-snapshot`, `session-start-reground`, handover reminder, `plan-phase-nudge`,
  `owner-guard` (multi-user: blocks non-owner governance edits AND non-owner `git push` to main,
  armed by `.claude/project-owner`)) +
  `settings.json` permissions. Plus `ritual-log` telemetry: every Skill-tool invocation, every
  user-typed command (custom via `UserPromptExpansion`; built-ins like `/compact`/`/model` only
  via `UserPromptSubmit` — first token only, prose never logged), compact boundary
  (manual/auto), session start and hook BLOCK is appended to `.claude/ritual-log` (git-ignored,
  self-trimmed). **`/keel-stats`** renders it into `reports/ritual-stats.md` — PLAN.md-style
  colored Mermaid interval boxes + a counts table.
- **File-local constraints** → optional `.claude/rules/` (see the example there).
- **Task-scoped lessons (three tiers)** → `LESSONS.md` keeps only the ALWAYS-relevant core plus an
  `## Index` router (one line per graduated cluster: what → where → when it loads); file-scoped
  lesson clusters graduate to `paths:`-scoped rules — or `paths:`-scoped skills when they must
  survive compaction — and domain facts go to docs. Why this shape and not a note graph or RAG:
  `research/{articles,web}/findings.md` + the field audit `reports/2026-08-17-lessons-scope-audit.md`
  (a focused context measurably beats a full one CONTAINING the same facts; index+scoped-bodies is
  the only pattern the platform ships and enforces).

## Language: machine surfaces vs human surfaces (rules §9.31)
Split by READER, not by project. `HANDOVER.md` · `LESSONS.md` · agent-team worker boards are read by
SESSIONS and `@`-imported every time → **always English**, on every project, because every line is a
permanent always-on token cost. `TASKS.md` · `PLAN.md` · `reports/team/*` · `docs/` are read by
PEOPLE (the owner reviews and answers there) → the **project language**. Two carve-outs: the user's
verbatim wording may stay quoted in their language inside an EN line, and anything needing an owner
decision is raised in CHAT in the project language even though the file line is EN. Adopting this
mid-project: never bulk-translate — `/keel-distill` converts lines as it rewrites them.

## Auto memory vs Keel memory
Claude Code also keeps an **auto memory** per project (`~/.claude/projects/<project>/memory/` —
`MEMORY.md` index + topic files, on by default): the assistant's own private notes. It is
**machine-local** — it never enters git, so teammates and CI never see it. Division of labor:
auto memory = one person's scratch recall; **anything the team must know goes to `LESSONS.md` /
`HANDOVER.md`** (git-shared, `@`-imported, cap-controlled). A team-relevant lesson that lives only
in one machine's auto memory is a lesson the team does not have.

## Headless `claude` calls from inside the repo (trap)
A script or LLM-provider that shells out to the `claude` CLI **with cwd inside the project** (benchmark
runners, LLM judges, batch jobs) starts a FULL Claude Code session per call: SessionStart hooks fire
(`.claude/ritual-log` fills with `session-start startup` lines), and `CLAUDE.md` + its `@`-imports
(~500 lines of constitution) load into EVERY call — per-call token cost, plus the callee model reads
your project rules (judge-bias risk in eval pipelines). Run such calls from a neutral cwd outside the
repo; a burst of same-minute `session-start startup` lines in the ritual-log is the telltale.

## MCP (external tool servers)
The kit ships **no MCP servers** — the discipline layer needs none (files + bash + hooks cover it).
MCP itself is often essential (semantic search, vLLM endpoints, DB bridges…); what Keel standardizes
is **where each server lives**, by who needs it:

| Who needs the server | Where it goes | Why |
|---|---|---|
| **Only this project** (its own DB/API) | **root `.mcp.json`** (rules.md §5.13) | git-tracked, reviewed like config, teammates get it with the repo |
| **You, in every project** (your personal toolbelt) | `claude mcp add --scope user` | written ONCE into your user config, available machine-wide — never re-written per project |
| **A team / several machines**, versioned | a small personal **MCP plugin** in your own marketplace | one `/plugin install` distributes + updates the whole set centrally (needs marketplace access — blocked networks fall back to the row above) |

So "rewriting the same MCP config in every project" is the one option that should never happen.
The plugin-bundled variant (an `.mcp.json` at a plugin's root, as drawn in ecosystem diagrams) is that
third row — *distribution*, not project config. Agent Teams and observer agents remain experimental:
watch, don't build on them.

## Multi-user: owner vs developers (optional — off by default)
Single-user projects: skip this — no file, zero cost. When helpers join, the FOUNDER declares ownership
by writing **`.claude/project-owner`** (one line: the owner's `git config user.name`; a bootstrap run by
someone else ASKS who the owner is, never assumes). One-run setup of everything below: **`/keel-team`**
(owner-only wizard — members/@tags, contribution model + host wall, caps, author folders, team doc).
Roles from then on:
- **Owner (founder)** — the only one who changes GOVERNANCE: `PLAN.md` (the plan itself + assignments),
  `rules.md`, `CLAUDE.md`, `docs/architecture.md`, ADRs, `.claude/` config. Assigns work by tagging
  TASKS items `(@name)` / the PLAN `owner` column, then pushes.
- **Developers** — pull, work ONLY their `@name` (or unassigned) items, mark them `[x]`, add
  `## Discovered` lines, write their own HANDOVER blocks (headings carry `@<git user.name>`), append
  LESSONS. Their sessions: the re-ground hook prints the role line; `/keel-autopilot` STOPS at
  foreign-owned items; the **`owner-guard` hook BLOCKS governance edits** (exit 2, propose-to-owner
  message). Ritual surfaces stay shared — a session that cannot write HANDOVER/LESSONS/TASKS cannot
  run the discipline at all.
- **Review loop (owner verifies developer work — file-first, four states, rules §10.40/41)** — a
  developer's finished item is MOVED, not deleted, to a TASKS `## Review` section at their handover,
  and the line NAMES its evidence file (`- [x] ... (@dev) — evidence:
  reports/team/<@dev>/<task>_fix_<date>.md`). **A chat summary is not a delivery:** the re-ground hook
  flags pathless lines AND files missing on disk. Each delivery walks `wip → delivered → verified
  (owner part: <one sentence>) → closed <date> accepted|rejected`, mirrored in the
  `reports/team/README.md` index — the team's review TODOLIST ("what's finished under @X" = the `[x]`
  lines in their section). Review ROUTING is the orchestrator's alone (the owner's main session, or
  the leader agent of an agent team): the deliverer never picks their own reviewer; the MECHANICAL
  half (re-run the done-when, parity scripts, source reads) is delegated to a verifier
  subagent/reviewer whose written report flips the line to `verified — owner part: <…>`; the owner
  performs that one named human step (§10.41 probe included), then **accepts** (delete → owner's
  HANDOVER (a); index `closed <date> accepted`) or **rejects** (back to `## Now`, one reason line,
  index back to `wip`). Phase grain needs no extra machinery: PLAN.md is governance, so a developer
  cannot flip a phase — the owner flips it after reviewing the gate evidence.
- **Identity = `git config user.name`** — every ownership mechanism (tags, owner-guard, autopilot
  stop, handover headings) matches this ONE string. Onboarding rule: repo-local
  `git config user.name "<tag>"`, single token, byte-for-byte the repo's `@tag` spelling (it need
  NOT equal the GitHub handle). A spaced or mismatched user.name silently unarms the machinery —
  the re-ground hook nags when it is unset.
- **Push wall (AI-side):** on armed projects `owner-guard` also blocks a non-owner session's
  `git push` that targets `main`/`master` (explicit refspec, or a bare push while checked out on
  it) — developers push topic branches and open PRs; even a fork's own main stays clean (= a clean
  PR base). The owner keeps the normal `ask`-gated push.
- **Host wall (the one humans can't bypass) — pick by hosting reality:**
  | Hosting | The wall |
  |---|---|
  | Public GitHub repo | branch ruleset on `main` (free): require PR, block force-push + deletion |
  | Private PERSONAL repo (free) | ⚠️ NO real wall: collaborators always get WRITE (no read-only role) and rulesets aren't enforced without a paid plan — hooks + discipline only |
  | Private repo in a FREE organization | transfer the repo to an org → developers get the **Read** role, org setting "allow forking of private repos" ON → they fork + PR; write access physically stays with the owner |
  | Paid GitHub (Pro/Team) · GitLab | enforced ruleset / protected branches directly on the private repo |
- **Fork-CI discipline (shape CI to the contribution flow, not the other way around):** on a fork PR
  the host injects NO repo secrets (and GitHub holds a first-time contributor's workflow run for
  approval) — so the PR-gating suite must pass SECRET-LESS: a test needing live creds/network SKIPs
  instead of failing (the CI twin of §10.40's "runs only on the owner's machine" bootstrap bug). If
  bootstrap pruned `.github/` in the solo era, team scale-up is the moment the prune is reversed —
  as a recorded ADR addendum, never a silent re-add.
- **Team etiquette on shared surfaces** (a PR should merge without stepping on anyone): sign
  LESSONS / `## Discovered` lines with your `@tag` (HANDOVER block headings carry it automatically);
  a developer PR touches only their OWN TASKS items + their OWN handover block; a HANDOVER merge
  conflict resolves as keep-both-blocks, newest first. `## Now` reads per-person on teams (~2–3
  items each). Sprint deadlines ride the item as `due: YYYY-MM-DD` — the re-ground hook surfaces
  past-due dates at session start.
- **Caps scale with the team:** the kit's memory caps are SOLO defaults — on a growing team the AI
  proposes larger ones (a starving `## Now`, a churning handover) and, with the owner's approval, pins
  them in **`.claude/keel-caps`** (`KEY=NUMBER` per line: HANDOVER · LESSONS · TASKS · RULES ·
  HANDOVER_BLOCKS). PROTECTED + owner-guarded: `/keel-update` never resets it, developers can't edit it.
- **Spec + solution-note convention (the board stays lean):** `TASKS.md ## Now` carries only
  id + `@owner` + `due:` + done-when; the detailed SPEC of an assignment (requirements, manual test
  scripts, acceptance details) is an owner-approved `<task>_spec.md`, and every delivered fix ships a
  SOLUTION NOTE (`<task>_fix_<date>.md`: problem → root cause → fix + why → changed files → tests).
  `## Review` evidence links BOTH files — the owner verifies against the spec.
- **Team reports: per-author folders + one index (clutter control, rules §10.40):** everything under
  `reports/team/` files into the AUTHOR's own folder — `reports/team/<@tag>/` for each developer, the
  owner, and every co-agent — with task-prefixed names inside (`<task>_spec.md`, `<task>_fix_<date>.md`;
  bulky/raw evidence as a `<task>_<what>/` subfolder), **Markdown only** (no .docx/binary docs).
  `reports/team/README.md` is the single INDEX **and the review todolist**: one line per report —
  `file · task · what · status` — appended at delivery (part of the solution-note step); statuses come
  ONLY from the controlled vocabulary `wip · delivered · verified — owner part: <…> · closed <date>
  accepted|rejected` (`[x]` only at closed; the author appends, the orchestrator flips — the format
  and who-flips-what live in the template README itself, and the `/keel-distill` lint checks the
  index mirrors the folders). Reports are NEVER deleted, and moved only ONE way: they are the
  permanent artifacts that Review evidence, LESSONS, ADRs, and path-scoped rules cite — an ad-hoc
  move dangles those references, and the trail costs zero always-on tokens (never `@`-imported);
  findability is the index's job. The one sanctioned move is the `/keel-distill` sweep: a `closed`
  task's files `git mv` into the author's `done/` subfolder with every citation rewritten in the
  same pass, so the flat folder stays a readable picture of LIVE work (a months-long author folder
  otherwise buries its open items under dozens of finished ones — field complaint, 2026-08-19).
  Adopting mid-project: leave existing flat files exactly where they are, back-fill
  their index lines, and let NEW reports be born into author folders.
- **Human ownership (comprehension gate, rules §10.41):** AI-assisted ≠ AI-verified. At EVERY task
  start (assigned or the owner's own) the session briefs the task and confirms understanding with
  2–3 questions. **Question quality bar:** each question (1) derives from THIS task's spec/done-when —
  it names the concrete file, metric, threshold, or risk; a question that would fit any task is a
  violation; (2) is self-explanatory — it carries its own context ("X works via Y; why not Z?" — the
  assignee learns while answering), never a bare yes/no; (3) targets why · how-it-will-be-verified ·
  what-breaks — the three things a reviewer must know. Q&A is appended DATED to the task's spec file
  (`reports/team/<@tag>/<task>_spec.md` **`## Comprehension log`**), and the gate is IDEMPOTENT: the
  session reads the log before asking and never re-asks an answered question — a task spanning
  sessions/compacts resumes from the log; only genuinely new-scope questions are added. Work doesn't
  start until confirmed. The manual/eyes-on parts of a done-when are run PERSONALLY by the assignee
  (evidence names who/how). At `## Review` the owner probes the same understanding proportionally —
  a delivery its author cannot explain is rejected ("comprehension gap"). Honesty about enforcement:
  the dev-session briefing is a NUDGE that steers the assignee into conscious, controlled work; the
  probe that BITES is the owner's — final say stays with the owner.
- **Co-agent sessions (one human, many hands — rules §10.42):** the owner may run EXTRA Claude
  sessions in the same repo as pseudo-teammates ("co-agents") — unlike a spawned sub-agent they keep
  their own chat history, so the owner inspects and steers them mid-task. Give each its own TASKS
  lane (`### <name>`) and hold it to intermediate work only: no rituals/skills, no commit/push, no
  touching anyone else's lines — memory files are single-writer surfaces and concurrent writers
  clobber each other SILENTLY; the main session reads fresh co-agent writes (`git diff`) before any
  curation pass. Honest enforcement note: a co-agent runs under the owner's git identity, so
  owner-guard cannot wall it — the rule is discipline, backed by the ritual gates it cannot pass
  (its `/compact` stalls at the compact-gate because HANDOVER is not its surface; the main session's
  handover clears it). Deliveries land in `## Review` like any teammate's (§10.41).
- **Agent teams (structured co-agents — `/keel-agent-team-create` + `/keel-agent-team-start`):** the
  owner names a roster (ONE **orchestrator** + specialized workers — `mechanic`, `frontend`, `test`,
  `provider`…; English single tokens preferred) and each agent gets an owner-approved charter in
  `.claude/agents/team-<name>.md` (mission · scope paths · lane · author folder · FORBIDDEN list; a
  greppable `Role:` body line), plus a TASKS lane and a `reports/team/<name>/` folder. **Identity is
  per-chat and survives compaction:** `/keel-agent-team-start @<name>` runs ONCE in a new chat and
  records `session_id → agent` into git-ignored `.claude/agent-team-sessions`; the re-ground hook
  reads its own session id on every start/compact/`--resume` and re-injects the identity from disk —
  asked once, never again. The orchestrator runs rituals/assignment/review routing (mechanical half
  delegated, §10.41) and holds no work items; workers inherit the co-agent FORBIDDEN list above.
  **Write-surface split (what makes concurrency race-proof by construction, not by discipline):**
  humans on different machines are merged by GIT; same-machine sessions have no merge layer — so in
  agent-team mode the shared memory files (TASKS · LESSONS · HANDOVER · the reports index · PLAN) are
  written by the ORCHESTRATOR alone. A worker writes only inside its own author folder:
  `reports/team/<name>/board.md` (lane mirror refreshed read-only from TASKS · findings inbox on the
  §9.31 hot path — durable through compaction · requests) plus its spec/fix files; the orchestrator
  syncs boards into the shared files each work block (the re-ground hook flags boards newer than
  TASKS.md). Charters double as spawnable subagents ONLY on the orchestrator's explicit request
  (their `description` says so). Enforcement honesty: these sessions all share the owner's git
  identity, so owner-guard cannot tell them apart — the walls are the charter text, the
  create-skill's owner gate (+ owner-guard on the charter files themselves), and the compact-gate
  workers cannot clear.
- **Dev-local runs:** every developer runs the product on their OWN machine without editing tracked
  files — machine-local knobs (PORT, hosts, creds) come from their own `.env` (defaults documented in
  `.env.example`; Makefile targets accept `make run-x PORT=8135`-style overrides); scarce shared
  backends (GPU endpoints, live read-only DBs) are consumed as services named in the team doc.
- **Onboarding doc:** materialize the team's concrete flow as a project-owned `docs/team.md` (roles
  table, fork/clone + `git config` steps, secret handoff via a safe channel, ritual etiquette). The
  kit deliberately ships NO team.md template — it is project content, and `/keel-update` must never
  overwrite it.
- **Scaling beyond a few developers:** the 3-block HANDOVER cap churns when ≥~4 people write
  concurrently — then apply the per-area valve per USER: `handovers/HANDOVER-<user>.md` (same block
  format + cap), root `HANDOVER.md` becomes the program index linking them (one "latest" per person,
  no duplicated truth). Do NOT split LESSONS per user: lessons are PROJECT knowledge — one person's
  gotcha is exactly what the others need. Sign lines instead; split per AREA if the file truly hurts.

Enforcement honesty (layered): hooks stop the AI *drafting* foreign governance edits or main-pushes —
the accidental collision. The wall for intentional human action is the HOST row above — a plain
terminal bypasses any hook, and on a free private personal repo that wall DOES NOT EXIST: either move
to a free org (Read + fork PRs) or accept discipline-only and say so in the project's team doc.

## Agent teams: how a waiting agent gets woken

An agent team spends most of its time with someone blocked on someone else. The question is what a
session does while it has nothing to do — and the field has a settled answer that is worth adopting
rather than re-deriving.

### The vocabulary

| Term | Means |
|---|---|
| **attended** | a human is present and starts the work (RPA's term; "human-in-the-loop" in agent frameworks) |
| **unattended** | the agent is triggered by a schedule or an event, with no human at the keyboard |
| **hybrid** | unattended by default, escalating to a human on anything outside its rules |
| **idle** | a session with nothing to do — a legitimate state, not a failure |
| **supervisor pattern** | one lead delegates to specialised workers who report only to the lead |

Keel's agent teams are **hybrid**: workers run unattended between assignments and escalate to the
orchestrator, which escalates to the owner. Every session stays an ordinary chat the owner can open
and type into at any moment — the messaging rides on top of that, it does not replace it.

### Event-driven, never polling

The 2026 consensus across multi-agent frameworks is that idle workers should not poll; they should
be activated by events. Claude Code implements exactly that, and it was **measured here** rather
than assumed (2026-08-19, `reports/2026-08-19-agent-team-messaging.md`):

- A message sent to an **idle** peer session **wakes it**, within seconds.
- The wake arrives as the first turn of a fresh context and **fires `SessionStart`** — so the
  reground hook re-injects the agent identity from `.claude/agent-team-sessions`, and CLAUDE.md's
  `@`-imports come back from disk. A woken worker rebuilds itself before it does anything.

So there is no sleep loop and no polling interval anywhere in Keel. `/keel-continue` ends in **IDLE**
and stops; the next assignment wakes the session. Two consequences worth knowing:

- **A closed chat cannot be woken.** `/list-agents` only lists live sessions — keeping the team's
  chats open is an operating requirement, not a bug.
- **A wake re-sends the woken session's whole context.** Keep messages short; they are pointers.

### The star, and why it is a hook

Everything goes through the centre: the orchestrator assigns, workers report back to it, no worker
messages another worker. The reason is not tidiness — the shared memory files have exactly ONE
writer, so a decision two workers reach between themselves is a decision no shared file records.

`permissions.deny` cannot express this: it takes the bare tool name, so denying `SendMessage` would
also cut the worker→orchestrator path the design runs on. `.claude/hooks/star-topology.sh` decides
by TARGET instead — it blocks a worker addressing another roster worker and allows everything else
(the orchestrator to anyone, anyone to the orchestrator, subagents, `main`, unrelated sessions, and
any session that has adopted no identity).

### Addressing: the session name IS the address

`SendMessage`'s `to:` is the peer's **session name** from `/list-agents`, not the keel agent name. An
unnamed session is named after its working directory, so a five-agent team reads as `my-app-3f`,
`my-app-a1`… mutually indistinguishable. `/keel-agent-team-start` therefore has each chat run
**`/rename <agent>`**; after that `to: "<agent>"` reaches it, the star wall recognises the roster,
and the `@<agent>` tag on every ritual-log line matches the address people actually use.

**Identity and addressing are two different layers, and only one survives a client restart.**
Field case, 2026-08-19: closing and reopening VS Code left the session id and
`.claude/agent-team-sessions` mapping completely intact (the reground hook re-injected "@frontend"
correctly, confirmed by the worker itself) — but `/list-agents` went back to showing the window
under its directory-derived name. The orchestrator read "the name I know is unreachable" as "the
session is dead" and broadcast a needless re-identify to three live workers.

**"Name unreachable" is never proof of death — diagnose in this order:**
1. Check `.claude/agent-team-sessions` for the lane's agent. The date column is a **last-seen
   heartbeat** (the reground hook touches it to today on every resolve, not just at first adopt).
2. Recent heartbeat (~2 days) → the session is alive; the DISPLAY NAME reset, the identity did not.
   Message the last-known name, or ask the owner to confirm the window before broadcasting anything.
3. Only a stale-or-absent heartbeat is grounds to treat the lane as free.

The same incident surfaced a second, rarer case worth watching for: two live windows resolving to
the **same** `session_id` (a duplicated client connection, not a duplicated agent). The
double-claim guard in `/keel-agent-team-start` (§2) catches the agent-level version of this — a
second session adopting an already-recently-claimed name — but a session-id collision is a client
bug, not something a hook can distinguish from normal reconnection; if it recurs, treat it as a
signal to restart the client cleanly rather than to reassign the lane.

### The message protocol

Two fixed forms, deliberately terse:

```
<id> yours     · done-when: <criterion> · spec: reports/team/<name>/<id>_spec.md
<id> delivered · evidence: reports/team/<name>/<id>_fix_<date>.md
```

**A message is a pointer, never the delivery.** The delivery is the file (rules §10.40); a chat
summary is not one, and the reground hook flags a `## Review` line whose evidence file is missing.
Waking a worker does not start its work either: it lands at the §10.41 comprehension gate first.

### Claude Code's own agent teams (optional accelerator)

Claude Code ships an experimental agent-teams feature — a lead spawning teammates, a shared task
list, a mailbox, idle notifications, and a `TeammateIdle` hook that can keep a teammate working by
exiting 2. Where it is available it is a fine accelerator, and a keel charter doubles as a teammate
definition (its body is appended to the teammate's system prompt).

Keel does not depend on it, for two reasons. It is **disabled by default** and unavailable on some
platforms and providers; and its documented limitation is precisely Keel's thesis — *"`/resume` and
`/rewind` do not restore in-process teammates"*. Keel's session map plus the reground hook rebuild
an identity from disk after any compaction or resume, which is the gap. File-based roster is the
base; the built-in feature is the option.

## Distribution: clone-only (and the double-fire trap)
Keel ships as a **clone**, one channel. The plugin/marketplace half was retired in v0.8.23 (it
shipped through v0.8.22): a plugin
structurally cannot carry `rules.md`, the memory files, or `settings.json` permissions — so it always
delivered a partial kit — while adding a second hook registration and needing marketplace access that
locked-down networks block. `/keel-update` is the update path (pull, reviewed, per-file).

**Double-firing hooks** (every nudge printed twice; the `session-start-reground` detector flags
same-second identical `.claude/ritual-log` lines) means the SAME hook is registered twice: a plugin
that registers keel-style hooks (`keel@keel` from the retired marketplace, or any other) enabled at
**user scope** (`~/.claude/settings.json` `enabledPlugins`) fires alongside the clone's own
`.claude/settings.json` registration. A project-scope `false` *should* win by settings precedence,
but a plugin whose hooks load before the enable-filter (a stale/`failed to load` cache) fires anyway.
Fix, in order: (1) `.claude/settings.local.json` (Local scope, higher precedence, git-ignored) with
`"enabledPlugins": {"<name>": false}`, then a **fresh session** (`enabledPlugins` is read at session
start, not hot-reloaded); (2) if it still fires, remove/uninstall the plugin at user scope — a clone
is self-contained and needs no plugin at all. The other cause is mundane: a long-lived session that
predates a settings change; refreshing the session clears it.
