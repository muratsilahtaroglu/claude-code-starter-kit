#!/usr/bin/env python3
"""Render `.claude/ritual-log` into `reports/ritual-stats.md` — a PLAN.md-style colored
Mermaid flowchart (one box per interval between session-start/compact boundaries, with
event counts) + a detail table. Deterministic, stdlib-only; run via /keel-stats or:
    python3 .claude/ritual-report.py
Colors reuse PLAN.md's classDefs: session=green, manual compact=amber, auto compact=red.
"""
import os
import re
from collections import Counter
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, ".claude", "ritual-log")
OUT = os.path.join(ROOT, "reports", "ritual-stats.md")
MAX_DIAGRAM_INTERVALS = 12  # keep the diagram readable; the table shows more

# Lines are "<date> <time> [@agent ]<event text>" — the @agent tag is present only on sessions
# that adopted an agent-team identity, so it is optional and captured separately.
LINE_RE = re.compile(r"^(\d{4}-\d\d-\d\d) (\d\d:\d\d):\d\d (?:@(\S+) )?(.+)$")

# What each event kind PROVES fired. A kind with zero records is reported as an instrument gap,
# never silently as "nothing happened": reading an empty table as "no rituals ran" is the mistake
# this file exists to prevent (rules §10.37 — a surprising measurement indicts the instrument).
EVENT_KINDS = {
    "session-start": "SessionStart",
    "compact": "PreCompact",
    "skill": "PreToolUse(Skill)",
    "command": "UserPromptExpansion",
    "typed": "UserPromptSubmit (slash commands only — built-ins included)",
    "nudge": "Stop (handover-reminder · plan-phase-nudge)",
}


def parse(path):
    """Yield (date, hh:mm, agent-or-None, event-text) tuples; skip malformed lines."""
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            m = LINE_RE.match(raw.strip())
            if m:
                out.append(m.groups())
    return out


def build_intervals(entries):
    """Split the log at boundaries (session-start / compact). Each interval carries its
    boundary label + a Counter of the events that happened until the next boundary."""
    intervals = []
    cur = {"kind": "start", "label": "(log start)", "date": "", "time": "",
           "agent": None, "events": Counter()}
    for date, hhmm, agent, text in entries:
        if text.startswith("session-start"):
            intervals.append(cur)
            cur = {"kind": "session", "label": text, "date": date, "time": hhmm,
                   "agent": agent, "events": Counter()}
        elif text.startswith("compact"):
            intervals.append(cur)
            trig = text.split()[1] if len(text.split()) > 1 else "?"
            cur = {"kind": f"compact-{trig}", "label": text, "date": date, "time": hhmm,
                   "agent": agent, "events": Counter()}
        else:
            # normalize: "skill keel-x" / "command code-review" / "<hook> BLOCK: reason"
            key = "BLOCK " + text.split(" BLOCK")[0] if " BLOCK" in text else text
            if agent:
                key = f"@{agent} {key}"
            cur["events"][key] += 1
    intervals.append(cur)
    # drop empty leading pseudo-interval
    return [iv for iv in intervals if iv["events"] or iv["kind"] != "start"]


def esc(s):
    return s.replace('"', "'")


def mermaid(intervals):
    ivs = intervals[-MAX_DIAGRAM_INTERVALS:]
    lines = ["```mermaid", "flowchart LR"]
    ids = []
    for i, iv in enumerate(ivs):
        nid = f"i{i}"
        ids.append((nid, iv))
        head = f"{iv['date'][5:]} {iv['time']}".strip() or "start"
        body = "<br/>".join(f"{esc(k)} x{v}" for k, v in iv["events"].most_common(4)) or "quiet"
        cls = {"session": "sess", "compact-manual": "cman", "compact-auto": "caut"}.get(iv["kind"], "sess")
        lines.append(f'  {nid}["{esc(head)} {esc(iv["kind"])}<br/>{body}"]:::{cls}')
    for (a, _), (b, _) in zip(ids, ids[1:]):
        lines.append(f"  {a} --> {b}")
    lines += [
        "  classDef sess fill:#2e7d32,color:#ffffff,stroke:#1b5e20",
        "  classDef cman fill:#f9a825,color:#000000,stroke:#b28704",
        "  classDef caut fill:#c62828,color:#ffffff,stroke:#8e0000",
        "```",
    ]
    return "\n".join(lines)


def table(intervals):
    rows = ["| # | boundary | interval events (count) |", "|---|---|---|"]
    for i, iv in enumerate(intervals):
        when = f"{iv['date']} {iv['time']}".strip() or "—"
        evs = " · ".join(f"{k} ×{v}" for k, v in iv["events"].most_common()) or "—"
        rows.append(f"| {i} | {when} `{iv['kind']}` | {evs} |")
    return "\n".join(rows)


def main():
    entries = parse(LOG)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not entries:
        body = (f"# Ritual stats — {stamp}\n\nNo telemetry yet: `.claude/ritual-log` is empty or "
                f"missing. It fills up as hooks fire (skills, commands, compacts, session starts).\n")
    else:
        ivs = build_intervals(entries)
        totals = Counter()
        for iv in ivs:
            totals.update(iv["events"])
        tot = " · ".join(f"{k} ×{v}" for k, v in totals.most_common(10)) or "—"
        seen = {t.split()[0] for _, _, _, t in entries}
        silent = [f"`{k}` ({EVENT_KINDS[k]})" for k in EVENT_KINDS if k not in seen]
        agents = sorted({a for _, _, a, _ in entries if a})
        cover = ""
        if silent:
            cover += ("\n> ⚠ **No record of: " + " · ".join(silent) + ".** That is a statement about the\n"
                      "> INSTRUMENT, not about the project: either the event never fired here, or nothing\n"
                      "> triggered it. Do not read it as \"these rituals never ran\" — check `/hooks` for the\n"
                      "> registration first.\n")
        if agents:
            cover += "\n> Agents writing to this log: " + " · ".join("@" + a for a in agents) + ".\n"
        elif os.path.isfile(os.path.join(ROOT, ".claude", "agent-team-sessions")):
            cover += ("\n> ⚠ An agent-team roster exists but NO line carries an @agent tag — sessions are\n"
                      "> writing unattributed, so \"which agent did this?\" cannot be answered.\n")
        body = (
            f"# Ritual stats — {stamp}\n\n"
            f"> Generated from `.claude/ritual-log` ({len(entries)} lines, machine-local) by\n"
            f"> `.claude/ritual-report.py` — re-run via `/keel-stats`. Boxes are the intervals between\n"
            f"> session starts (green) and compacts (amber=manual, red=auto); PLAN.md's palette.\n\n"
            f"**Totals:** {tot}\n{cover}\n"
            f"## Timeline (last {MAX_DIAGRAM_INTERVALS} intervals)\n\n{mermaid(ivs)}\n\n"
            f"## All intervals\n\n{table(ivs)}\n"
        )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"wrote {OUT} ({len(entries)} log lines)")


if __name__ == "__main__":
    main()
