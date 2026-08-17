# .claude/rules/ — optional path-scoped rules

`rules.md` at the repo root is the **always-loaded constitution** (universal discipline, `@`-imported
every session). This folder is for **optional, FILE-SCOPED constraints** that only matter when specific
files are touched — a rule with a `paths:` frontmatter loads *only* when Claude reads a matching file,
so it stays out of context (and off the always-on token budget) during unrelated work.

**Use a path-scoped rule** for a constraint that applies to some files but not the whole project — e.g.
"migrations are append-only", "API handlers must validate input", "generated files are never edited by
hand". See `migrations-append-only.md` for the format (delete/adapt it — it's an example).

**Keep it in `rules.md` instead** when the rule must *always* apply: path-scoped rules are **lost after
compaction until a matching file is touched again** (unlike `rules.md`, which is re-injected from disk
every compaction). So must-always-hold discipline (handover, security posture, judgment) belongs in
`rules.md`; only genuinely file-local constraints belong here.

**Must it survive a mid-task compaction?** Use a `paths:`-scoped **skill** instead
(`.claude/skills/<name>/SKILL.md` — skills accept the same `paths:` frontmatter): invoked skill
bodies are the one scoped mechanism re-injected after compaction (≈5k tokens/skill, 25k total,
truncation keeps the top), while a rule here waits for the next file match. Either way, a
graduated-lesson cluster keeps ONE router line in `LESSONS.md ## Index` so it stays findable when
its trigger hasn't fired (`/keel-distill` lints both directions).

**Writing discipline (rules here can bite — treat them as governance):**
- **Owner approves the text.** A new or changed rule here is PROPOSED as its full text and lands only
  with the owner's explicit approval — never silently as a side effect of another ritual (a distill
  turn shows it in its plan). On armed multi-user projects the owner-guard hook already blocks
  non-owner writes to `.claude/rules/*`; this approval bar binds the owner's own AI sessions too.
- **Self-contained or it's a bug.** A rule must read cold: the constraint + WHY + a verifiable check,
  inline. Evidence may cite PERMANENT artifacts (a `reports/` file, an ADR, `docs/handover-archive.md`)
  — never live state: a TASKS item, a PLAN phase status, `## Review`, or "today's/current" work. Those
  dangle the moment the board changes, leaving a rule nobody can interpret.
- **When it loads:** only while a file matching `paths:` is being read/edited — not at session start,
  and (as above) not after compaction until a match is touched again. Write it assuming the reader
  has NO other context.

(Mechanism trade-offs across skills / hooks / subagents / rules / CLAUDE.md: see `docs/steering.md`.)
