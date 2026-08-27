"""Regression matrix for the agent-team address resolver — rules.md §10.42.

WHY THIS FILE EXISTS. A session's NAME is process-local (`~/.claude/sessions/<PID>.json`, keyed by
pid) and silently reverts on every window/process recreation; the IDENTITY lives on disk keyed by
session-id and survives. Confusing the two cost a live team a broadcast re-identify and nearly a
double-assigned lane (2026-08-19), and its rarer sibling — one session-id driven from TWO windows —
is the silent-clobber shape §10.42 exists to prevent. The resolver's core is pure, so this matrix
feeds it fixtures directly. Backported from alice_v2 (`scripts/team_addresses.py`, 2026-08-24).

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "team_addresses", REPO / ".claude" / "team-addresses.py")
ta = importlib.util.module_from_spec(_spec)
sys.modules["team_addresses"] = ta
_spec.loader.exec_module(ta)

CWD = "/repo"


def rec(sid, name, pid, cwd=CWD):
    return {"sessionId": sid, "name": name, "pid": pid, "cwd": cwd}


def alive(*pids):
    live = set(pids)
    return lambda p: p in live


# --------------------------------------------------------------------------
# resolve() — the pure core
# --------------------------------------------------------------------------

def test_healthy_lane_is_ok():
    rows, unreg = ta.resolve([("s1", "frontend")], [rec("s1", "frontend", 11)], alive(11), CWD)
    assert rows == [{"agent": "frontend", "sid": "s1", "name": "frontend", "pid": 11,
                     "status": "OK", "cwd": CWD, "windows": 1}]
    assert unreg == []


def test_closed_window_is_no_process():
    rows, _ = ta.resolve([("s1", "frontend")], [rec("s1", "frontend", 11)], alive(), CWD)
    assert rows[0]["status"] == "NO_PROCESS"


def test_reverted_name_is_a_mismatch_not_a_death():
    """The 2026-08-19 incident: identity intact, display name reset by a client restart."""
    rows, _ = ta.resolve([("s1", "frontend")], [rec("s1", "my-app-3f", 11)], alive(11), CWD)
    assert rows[0]["status"] == "NAME_MISMATCH"
    assert rows[0]["name"] == "my-app-3f", "the row must carry where messages actually go"


def test_two_windows_on_one_session_id_are_flagged():
    rows, _ = ta.resolve([("s1", "frontend")],
                         [rec("s1", "frontend", 11), rec("s1", "frontend", 12)],
                         alive(11, 12), CWD)
    assert all(r["windows"] == 2 for r in rows)


def test_unregistered_live_session_in_this_repo_is_surfaced():
    _, unreg = ta.resolve([("s1", "frontend")],
                          [rec("s1", "frontend", 11), rec("s9", "stray", 99)],
                          alive(11, 99), CWD)
    assert len(unreg) == 1 and unreg[0]["sessionId"] == "s9"


def test_live_session_in_another_repo_is_not_our_business():
    _, unreg = ta.resolve([], [rec("s9", "other", 99, cwd="/elsewhere")], alive(99), CWD)
    assert unreg == []


# --------------------------------------------------------------------------
# format_hook() — what SessionStart injects
# --------------------------------------------------------------------------

def _hook(registry, records, live_pids):
    rows, unreg = ta.resolve(registry, records, alive(*live_pids), CWD)
    return ta.format_hook(rows, unreg)


def test_healthy_team_is_one_line():
    lines = _hook([("s1", "frontend"), ("s2", "orchestrator")],
                  [rec("s1", "frontend", 11), rec("s2", "orchestrator", 12)], (11, 12))
    assert len(lines) == 1 and "address=identity (2 live)" in lines[0]


def test_stale_dead_row_beside_a_live_one_is_not_a_warning():
    """Per-identity aggregation: an old dead registry row for a lane that IS reachable stays quiet
    (per-row warning was the original's first-draft bug — a false flag at every session start)."""
    lines = _hook([("s-old", "provider"), ("s-new", "provider")],
                  [rec("s-new", "provider", 21)], (21,))
    assert len(lines) == 1 and "provider" in lines[0]


def test_mismatch_names_the_rename_fix():
    lines = _hook([("s1", "frontend")], [rec("s1", "my-app-3f", 11)], (11,))
    joined = "\n".join(lines)
    assert "ADDRESS ≠ IDENTITY" in joined and "/rename frontend" in joined


def test_double_window_warns_clobber():
    lines = _hook([("s1", "frontend")],
                  [rec("s1", "frontend", 11), rec("s1", "frontend", 12)], (11, 12))
    assert any("2 WINDOWS" in l for l in lines)
