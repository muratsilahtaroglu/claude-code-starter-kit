# docs/retro/ — the COLD layer of LESSONS.md

`LESSONS.md` is the HOT layer: it is `@`-imported into every session, so only a lesson that is still
CITED earns a line there. A lesson that is still TRUE but no longer cited moves here, into a monthly
file `<YYYY-MM>.md`, at `/keel-distill` (rules §9.33). One router line stays in `LESSONS.md ## Index`
so the lesson is found when its trigger fires.

**This is COOLING, not deletion — and not retirement.** Three exits, three destinations:
- proven WRONG → `docs/lessons-retired.md` with its refutation (one corrective line stays in LESSONS);
- still true, applied 3+ times → PROMOTED into rules / a skill / an ADR / docs (the entry is deleted);
- still true, no longer cited → HERE (verbatim, with its original date).

**The criterion is a PROXY, and says so.** "Applied in the last 60 days" cannot be measured — no tool
counts where a lesson was applied. The measurable proxy is: *is it cited from `## Index` or from any
report/spec/ADR?* (`grep -rl` the entry's key phrase). A criterion nobody can measure is not written;
a measurable proxy labelled as one is. Field origin: a 5-agent project's LESSONS sat at 1000/1000
lines for weeks because the entry budget slowed the INFLOW and nothing opened an OUTFLOW — 82 of 132
entries were single-copy knowledge, so a bulk sweep was impossible and the exit had to be per entry.

This folder is never `@`-imported — `grep` it on demand (the §9.34 archive logic).
