# .claude/skills/ — the kit's rituals

A skill is a reusable procedure Claude Code loads on demand: the user types `/<name>`, or the model
invokes it when the task matches its `description`. Everything here is a **fixed ritual with the
case-specific detail filled in at run time** (rules §2.9) — the second time you write a similar
ad-hoc prompt, it belongs here instead.

Which mechanism for what (skill vs. subagent vs. rule vs. hook vs. CLAUDE.md): `docs/steering.md`.

## Session rhythm
| Skill | When |
|---|---|
| `keel-continue` | Decide what this session does next and do it — RESUME half-done work · TAKE the lane's next assigned item (through the comprehension gate) · or report IDLE. Role-aware; read-only, so any session type may run it |
| `keel-handover` | Before ending a session: add the dated block (done / tried-failed / latest / next), drain `## Discovered`, move deliveries to `## Review` |
| `keel-compact` | Before a manual `/compact`: runs the handover procedure, verifies freshness, then hands off to `/compact`. One command instead of several |
| `keel-distill` | When a memory file hits its cap: rotate HANDOVER blocks to the archive, scope-triage and promote LESSONS entries, drain the inbox, lint for drift |

## Project lifecycle
| Skill | When |
|---|---|
| `keel-plan` | Create or revise `PLAN.md` — the phase DAG (phases · gates · dependencies) + its generated diagram |
| `keel-adopt` | Overlay the kit onto an EXISTING project (brownfield). Non-destructive: inventory, merge from a shown diff, back-fill docs from the real code |
| `keel-update` | Pull later kit improvements into a project that cloned it earlier. Tooling in one reviewed batch, tailored files hunk-by-hunk |
| `keel-phase-review` | The phase gate: working product, tests, docs, ADRs, handover — then flip the PLAN status |
| `keel-autopilot` | Gated autonomy for one session: advance phases back-to-back, stopping at every gate FAIL, uncertain decision, or security-adjacent change. Push is never automatic. Solo sessions or an agent team's ORCHESTRATOR only — it runs phase-review and commits, both §10.42-forbidden to a worker |

## Quality gates
| Skill | When |
|---|---|
| `keel-audit` | Periodic rules-compliance spot-check over the commits since the last audit (read-only `auditor` subagent) |
| `keel-pilot` | Before any bulk run (mass labeling / generation / migration): thresholds → smoke → gold set → ramp → acceptance. No full run on an unvalidated pipeline |
| `keel-tidy` | Layout hygiene — sweep stray files, attach evidence to each, then triage with approval |
| `keel-research` | Opt-in external research → cited findings under `research/<platform>/` (`researcher` subagent) |
| `keel-stats` | Render `.claude/ritual-log` into a visual report: which rituals actually ran, how often |

## Teams (owner-only)
| Skill | When |
|---|---|
| `keel-team` | Real humans on different machines: declare the owner (arms `owner-guard`), register `@tags`, size the caps, pick the §6 contribution model + host wall |
| `keel-agent-team-create` | Same machine, several Claude sessions: name the roster (one orchestrator + specialized workers), generate the `.claude/agents/team-<name>.md` charters, seed lanes + author folders |
| `keel-agent-team-start` | Run once in each new worker chat: adopt the charter, `/rename` the session to the agent name (that name IS its messaging address), and record the session→agent mapping so the identity is re-injected from disk after every compaction |

Setting up a team is governance — those three are gated to the project owner and land only with
explicit approval, exactly like a rules change (rules §10.40, §10.42).

## Writing a new one

`<name>/SKILL.md` with `name` + `description` frontmatter; the description is what makes the model
reach for it, so write it as *when to use this*, not what it is. Keep the body a procedure — numbered
steps, an approval point before anything is written, and a report at the end. A skill that only
prints advice should have been a line in `rules.md`; one that must run deterministically on every
occurrence should have been a hook.
