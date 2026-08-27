#!/usr/bin/env python3
"""Agent-team ADDRESS resolver: registered identity (session-id) -> that identity's CURRENT
message name. Backported from a live team project (alice_v2, measured 2026-08-24).

WHY THIS EXISTS. A session's NAME is process-local — it lives in the `name` field of
`~/.claude/sessions/<PID>.json`, keyed by pid. Every time the window/process is recreated
(IDE extension reload · `--resume` · a new window) there is a NEW pid => a NEW file => the name
silently reverts to `<repo>-xx`. The IDENTITY, by contrast, lives on disk in
`.claude/agent-team-sessions`, keyed by session-id, and survives all of that. Consequence:
identity is durable, the address is VOLATILE => an address is never REMEMBERED, it is RESOLVED
(rules §10.42). Field cost of not knowing this: an orchestrator read "name unreachable" as
"session dead" and broadcast a needless re-identify to three live workers (2026-08-19).

It also catches the rarer sibling: TWO live windows driving the SAME session-id (one session,
two processes — the silent-clobber shape). A transcript count cannot see this (both windows
share one transcript); the process files can.

Usage:  python3 .claude/team-addresses.py [--check] [--json] [--hook]
  --check : exit 1 when any registered identity has no live address, a name diverges from its
            identity, an UNREGISTERED live session works this repo, or one identity is driven
            from two windows.
  --hook  : compact SessionStart output (a single line when healthy); ALWAYS exit 0 (fail-open —
            telemetry must never break a session start).

The core (`resolve`) is PURE — it reads no machine state; everything arrives as arguments, so the
test matrix feeds it fixtures (tests/unit/test_keel_team_addresses.py).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

REGISTRY = ".claude/agent-team-sessions"
SESSIONS_GLOB = "~/.claude/sessions/*.json"


def parse_registry(lines):
    """'<session-id> <agent> [date]' lines -> [(sid, agent)]."""
    out = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and "-" in parts[0]:
            out.append((parts[0], parts[1]))
    return out


def resolve(registry, records, is_alive, repo_cwd):
    """Pure core. registry: [(session_id, agent)] · records: [dict] (sessions/*.json contents) ·
    is_alive: pid -> bool · repo_cwd: this repo's absolute path.
    Returns (rows, unregistered): one row per live process of each registered identity (or one
    NO_PROCESS row), plus live sessions working THIS repo that adopted no identity."""
    by_sid = {}
    for rec in records:
        by_sid.setdefault(rec.get("sessionId"), []).append(rec)

    rows = []
    for sid, agent in registry:
        live = [r for r in by_sid.get(sid, []) if is_alive(r.get("pid"))]
        if not live:
            rows.append({"agent": agent, "sid": sid, "name": None, "pid": None,
                         "status": "NO_PROCESS", "cwd": None, "windows": 0})
            continue
        for rec in live:
            name = rec.get("name")
            cwd = rec.get("cwd")
            if name != agent:
                status = "NAME_MISMATCH"
            elif cwd != repo_cwd:
                status = "OTHER_REPO"
            else:
                status = "OK"
            rows.append({"agent": agent, "sid": sid, "name": name, "pid": rec.get("pid"),
                         "status": status, "cwd": cwd, "windows": len(live)})

    known = {sid for sid, _ in registry}
    unregistered = [r for r in records
                    if r.get("sessionId") not in known
                    and r.get("cwd") == repo_cwd
                    and is_alive(r.get("pid"))]
    return rows, unregistered


def format_hook(rows, unregistered):
    """Compact lines for SessionStart injection (a single line when healthy).

    Aggregates PER IDENTITY, not per registry row: if an identity has a live address, a stale
    dead row for the same identity is NOT a problem — warning per-row would raise a false flag
    at every session start (the first draft of the original did exactly that)."""
    by_agent = {}
    for r in rows:
        by_agent.setdefault(r["agent"], []).append(r)

    lines, warn = [], []
    ok_names = []
    for agent, rs in sorted(by_agent.items()):
        live = [r for r in rs if r["status"] != "NO_PROCESS"]
        if not live:
            warn.append("[team] ⚠ NO PROCESS: %s — messages to that lane cannot be delivered "
                        "(its window is closed)" % agent)
            continue
        windows = max(r["windows"] for r in live)
        if windows > 1:
            warn.append("[team] 🔴 %s is driven from **%d WINDOWS** (pid %s) — silent-clobber "
                        "risk on shared files (§10.42); close one."
                        % (agent, windows, ", ".join(str(r["pid"]) for r in live)))
        mism = [r for r in live if r["status"] == "NAME_MISMATCH"]
        if mism:
            warn.append("[team] ⚠ ADDRESS ≠ IDENTITY: %s → a message reaches the name '%s' "
                        "(not the identity) — run /rename %s in that chat"
                        % (agent, mism[0]["name"], agent))
        elif any(r["status"] == "OK" for r in live):
            ok_names.append(agent)
    for u in unregistered:
        warn.append("[team] ⚠ UNREGISTERED live session: '%s' (pid %s) — it can write in this "
                    "repo with no charter; have it run /keel-agent-team-start, or close it"
                    % (u.get("name"), u.get("pid")))

    if ok_names:
        lines.append("[team] address=identity (%d live): %s" % (len(ok_names), " · ".join(ok_names)))
    lines.extend(warn)
    if warn:
        lines.append("[team] full table: python3 .claude/team-addresses.py  (the name is "
                     "PROCESS-local; the identity lives on disk keyed by session-id ⇒ an address "
                     "is never remembered, it is RESOLVED)")
    return lines


def _load_records():
    records = []
    for path in glob.glob(os.path.expanduser(SESSIONS_GLOB)):
        try:
            with open(path) as fh:
                records.append(json.load(fh))
        except (OSError, ValueError):
            continue  # a corrupt/half-written file must not break address resolution (fail-open)
    return records


def _pid_alive(pid):
    return bool(pid) and os.path.exists("/proc/%s" % pid)


def main(argv=None):
    ap = argparse.ArgumentParser(description="agent-team identity -> live message address")
    ap.add_argument("--check", action="store_true", help="exit 1 on any problem")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--hook", action="store_true",
                    help="compact SessionStart output (one line when healthy); ALWAYS exit 0")
    args = ap.parse_args(argv)

    repo = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    reg_path = os.path.join(repo, REGISTRY)
    if not os.path.exists(reg_path):
        if not args.hook:              # on a team-less project the hook is SILENT
            print("no registry: %s (no agent team set up)" % REGISTRY, file=sys.stderr)
        return 0 if args.hook else 2
    with open(reg_path) as fh:
        registry = parse_registry(fh.readlines())

    rows, unregistered = resolve(registry, _load_records(), _pid_alive, repo)

    if args.hook:
        for line in format_hook(rows, unregistered):
            print(line)
        return 0                       # never breaks a session start (fail-open)
    if args.json:
        print(json.dumps({"rows": rows, "unregistered": unregistered}, indent=2, ensure_ascii=False))
    else:
        print("%-18s %-18s %-8s %s" % ("identity", "ADDRESS (current name)", "pid", "status"))
        print("-" * 62)
        for r in rows:
            note = {"OK": "", "NAME_MISMATCH": "  <- name diverged (messages go to the NAME)",
                    "OTHER_REPO": "  <- working ANOTHER repo", "NO_PROCESS": "  <- window closed"}[r["status"]]
            if r["windows"] > 1:
                note += "  ** SAME IDENTITY driven from %d windows **" % r["windows"]
            print("%-18s %-18s %-8s %s%s" % (r["agent"], r["name"] or "-", r["pid"] or "-",
                                             r["status"], note))
        for r in unregistered:
            print("%-18s %-18s %-8s UNREGISTERED  <- live in this repo, no identity"
                  % ("(none)", r.get("name"), r.get("pid")))

    if args.check:
        bad = [r for r in rows if r["status"] != "OK" or r["windows"] > 1]
        return 1 if (bad or unregistered) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
