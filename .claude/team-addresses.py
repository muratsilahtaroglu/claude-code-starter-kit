#!/usr/bin/env python3
"""Agent-team ADDRESS resolver: registered identity (session-id) -> that identity's CURRENT
message name. Backported from a live team project (alice_v2, measured 2026-08-24); extended
2026-09-03 with the two-machine case.

WHY THIS EXISTS. A session's NAME is process-local — it lives in the `name` field of
`~/.claude/sessions/<PID>.json`, keyed by pid. Every time the window/process is recreated
(IDE extension reload · `--resume` · a new window) there is a NEW pid => a NEW file => the name
silently reverts to `<repo>-xx`. The IDENTITY, by contrast, lives on disk in
`.claude/agent-team-sessions`, keyed by session-id, and survives all of that. Consequence:
identity is durable, the address is VOLATILE => an address is never REMEMBERED, it is RESOLVED
(rules §10.42). Field cost of not knowing this: an orchestrator read "name unreachable" as
"session dead" and broadcast a needless re-identify to three live workers (2026-08-19).

TWO MACHINES, TWO VS CODE BUILDS (measured 2026-09-03). An owner working the same remote host from
home and from work, with the two clients on different VS Code versions, gets TWO VS Code servers
alive at once (`~/.vscode-server/cli/servers/Stable-<commit>/`, one per build). Each client's
server keeps its own `claude` processes and resumes the SAME session ids => every identity shows
2-3 live processes ("windows"), all with live sockets. Process AGE is the WRONG axis to pick the
real one (when the owner goes back to the other machine, the OLDER twin is the one in use). The
right axis is whether that process's VS Code server currently has a CLIENT attached: the server
build's `command-shell` process holds an ESTABLISHED TCP connection iff a client is connected.
This resolver reports ATTACHED / DETACHED per twin and names the detached pids — the owner decides
to kill them (both twins share ONE transcript; a detached twin holds nothing that is not on disk).

Usage:  python3 .claude/team-addresses.py [--check] [--json] [--hook]
  --check : exit 1 when any registered identity has no live address, a name diverges from its
            identity, an UNREGISTERED live session works this repo, or one identity is driven
            from two windows.
  --hook  : compact SessionStart output (a single line when healthy); ALWAYS exit 0 (fail-open —
            telemetry must never break a session start). Also performs the SELF check: if THIS
            session's identity is @X but its address is not "X", the first line says so and names
            the fix (`/rename X`, or the launch wrapper that makes it automatic).

The core (`resolve`, `attachment`, `format_hook`, `self_line`) is PURE — it reads no machine
state; everything arrives as arguments, so the test matrix feeds it fixtures
(tests/unit/test_keel_team_addresses.py).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

REGISTRY = ".claude/agent-team-sessions"
SESSIONS_GLOB = "~/.claude/sessions/*.json"
_BUILD_RE = re.compile(r"\.vscode-server/cli/servers/Stable-([0-9a-f]{6,})/")


def parse_registry(lines):
    """'<session-id> <agent> [date]' lines -> [(sid, agent)]."""
    out = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2 and "-" in parts[0]:
            out.append((parts[0], parts[1]))
    return out


def resolve(registry, records, is_alive, repo_cwd, attached=None):
    """Pure core. registry: [(session_id, agent)] · records: [dict] (sessions/*.json contents) ·
    is_alive: pid -> bool · repo_cwd: this repo's absolute path · attached: {pid: True|False|None}.
    Returns (rows, unregistered): one row per live process of each registered identity (or one
    NO_PROCESS row), plus live sessions working THIS repo that adopted no identity."""
    attached = attached or {}
    by_sid = {}
    for rec in records:
        by_sid.setdefault(rec.get("sessionId"), []).append(rec)

    rows = []
    for sid, agent in registry:
        live = [r for r in by_sid.get(sid, []) if is_alive(r.get("pid"))]
        if not live:
            rows.append({"agent": agent, "sid": sid, "name": None, "pid": None,
                         "status": "NO_PROCESS", "cwd": None, "windows": 0, "attached": None})
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
                         "status": status, "cwd": cwd, "windows": len(live),
                         "attached": attached.get(rec.get("pid"))})

    known = {sid for sid, _ in registry}
    unregistered = [r for r in records
                    if r.get("sessionId") not in known
                    and r.get("cwd") == repo_cwd
                    and is_alive(r.get("pid"))]
    return rows, unregistered


def attachment(pid_build, build_has_client):
    """Pure: {pid: build} × {build: bool} -> {pid: True|False|None}. None = not under a VS Code
    remote server (a plain terminal session) or the signal was unavailable — never guessed."""
    out = {}
    for pid, build in pid_build.items():
        out[pid] = None if build is None or build not in build_has_client else bool(build_has_client[build])
    return out


def self_line(own, registry):
    """Pure: the SELF check for --hook. own = this process's session record (or None).
    Returns [] when healthy/unknown, else ONE loud line addressed to this window."""
    if not own:
        return []
    agent = dict(registry).get(own.get("sessionId"))
    if not agent or own.get("name") == agent:
        return []
    return ["[team] ⚠ THIS window is @%s but its address is '%s' — peers cannot reach @%s until the "
            "owner types `/rename %s` here (a resumed/reopened window loses its name; the launch "
            "wrapper in /keel-agent-team-start §2b makes this automatic)."
            % (agent, own.get("name"), agent, agent)]


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
            det = [r for r in live if r["attached"] is False]
            att = [r for r in live if r["attached"] is True]
            if att and det:
                warn.append("[team] 🔴 %s is driven from **%d WINDOWS** — attached: pid %s ('%s'); "
                            "DETACHED (its VS Code server has no client — the other machine's "
                            "leftover): %s. All twins write ONE transcript (silent-clobber risk, §10.42); "
                            "a detached twin holds nothing that is not on disk — kill: `kill %s`"
                            % (agent, windows,
                               ", ".join(str(r["pid"]) for r in att),
                               ", ".join(str(r["name"]) for r in att),
                               ", ".join("pid %s ('%s')" % (r["pid"], r["name"]) for r in det),
                               " ".join(str(r["pid"]) for r in det)))
            else:
                warn.append("[team] 🔴 %s is driven from **%d WINDOWS** (pid %s) — silent-clobber "
                            "risk on shared files (§10.42); close one."
                            % (agent, windows, ", ".join(str(r["pid"]) for r in live)))
        mism = [r for r in live if r["status"] == "NAME_MISMATCH" and r["attached"] is not False]
        if mism and not any(r["status"] == "OK" and r["attached"] is not False for r in live):
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


# ---- machine readers (Linux; every one of them fails open to "unknown") -------------------------

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


def _cmdline(pid):
    try:
        with open("/proc/%s/cmdline" % pid, "rb") as fh:
            return fh.read().replace(b"\0", b" ").decode("utf-8", "replace")
    except OSError:
        return ""


def _ppid(pid):
    try:
        with open("/proc/%s/status" % pid) as fh:
            for line in fh:
                if line.startswith("PPid:"):
                    return int(line.split()[1])
    except (OSError, ValueError):
        pass
    return 0


def _ancestors(pid, limit=12):
    out, p = [], pid
    while p and p > 1 and len(out) < limit:
        out.append(p)
        p = _ppid(p)
    return out


def _build_of(pid):
    """The VS Code server build (commit) this process runs under, or None."""
    for a in _ancestors(pid):
        m = _BUILD_RE.search(_cmdline(a))
        if m:
            return m.group(1)
    return None


def _established_pids():
    try:
        out = subprocess.run(["ss", "-tnp"], capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return {int(m) for m in re.findall(r"pid=(\d+)", out)}


def _build_has_client(builds, established):
    """A build has a client iff one of its `code-<commit> … command-shell` processes holds an
    ESTABLISHED TCP connection (the client's control channel over the SSH tunnel)."""
    res = {}
    if established is None or not builds:
        return res
    shells = {}
    for d in glob.glob("/proc/[0-9]*"):
        try:
            pid = int(os.path.basename(d))
        except ValueError:
            continue
        c = _cmdline(pid)
        if " command-shell" not in c:
            continue
        for b in builds:
            if ("code-%s" % b) in c:
                shells.setdefault(b, []).append(pid)
    for b in builds:
        res[b] = any(p in established for p in shells.get(b, []))
    return res


def _attachment_for(records):
    live = [r.get("pid") for r in records if _pid_alive(r.get("pid"))]
    pid_build = {p: _build_of(p) for p in live}
    builds = {b for b in pid_build.values() if b}
    return attachment(pid_build, _build_has_client(builds, _established_pids()))


def _own_record(records):
    """This process's session record: the first ancestor pid that owns a sessions/<pid>.json."""
    by_pid = {r.get("pid"): r for r in records}
    for a in _ancestors(os.getpid()):
        if a in by_pid:
            return by_pid[a]
    return None


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

    records = _load_records()
    try:
        attached = _attachment_for(records)
    except Exception:                  # the signal is a bonus, never a blocker
        attached = {}
    rows, unregistered = resolve(registry, records, _pid_alive, repo, attached)

    if args.hook:
        try:
            own = _own_record(records)
        except Exception:
            own = None
        for line in self_line(own, registry) + format_hook(rows, unregistered):
            print(line)
        return 0                       # never breaks a session start (fail-open)
    if args.json:
        print(json.dumps({"rows": rows, "unregistered": unregistered}, indent=2, ensure_ascii=False))
    else:
        print("%-18s %-18s %-8s %-9s %s" % ("identity", "ADDRESS (current name)", "pid", "client", "status"))
        print("-" * 72)
        for r in rows:
            note = {"OK": "", "NAME_MISMATCH": "  <- name diverged (messages go to the NAME)",
                    "OTHER_REPO": "  <- working ANOTHER repo", "NO_PROCESS": "  <- window closed"}[r["status"]]
            if r["windows"] > 1:
                note += "  ** SAME IDENTITY driven from %d windows **" % r["windows"]
            client = {True: "attached", False: "DETACHED", None: "-"}[r["attached"]]
            print("%-18s %-18s %-8s %-9s %s%s" % (r["agent"], r["name"] or "-", r["pid"] or "-",
                                                  client, r["status"], note))
        for r in unregistered:
            print("%-18s %-18s %-8s %-9s UNREGISTERED  <- live in this repo, no identity"
                  % ("(none)", r.get("name"), r.get("pid"), "-"))

    if args.check:
        bad = [r for r in rows if r["status"] != "OK" or r["windows"] > 1]
        return 1 if (bad or unregistered) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
