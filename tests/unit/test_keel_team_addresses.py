"""Regression matrix for the agent-team address resolver — rules.md §10.42.

WHY THIS FILE EXISTS. A session's NAME is process-local (`~/.claude/sessions/<PID>.json`, keyed by
pid) and silently reverts on every window/process recreation; the IDENTITY lives on disk keyed by
session-id and survives. Confusing the two cost a live team a broadcast re-identify and nearly a
double-assigned lane (2026-08-19), and its rarer sibling — one session-id driven from TWO windows —
is the silent-clobber shape §10.42 exists to prevent. On 2026-09-03 that sibling turned out to be
the NORMAL case for an owner who works one remote host from two machines on different VS Code
versions: two VS Code servers, every identity twinned. Process AGE is the wrong axis to pick the
live twin (going back to the other machine makes the OLDER one live); whether the twin's VS Code
server has a CLIENT attached is the right one. The resolver's core is pure, so this matrix feeds it
fixtures directly. Backported from alice_v2 (`scripts/team_addresses.py`, 2026-08-24).

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
                     "status": "OK", "cwd": CWD, "windows": 1, "attached": None}]
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


def test_attachment_is_carried_per_pid():
    rows, _ = ta.resolve([("s1", "frontend")],
                         [rec("s1", "frontend", 11), rec("s1", "alice-v2-ea", 12)],
                         alive(11, 12), CWD, attached={11: False, 12: True})
    assert {r["pid"]: r["attached"] for r in rows} == {11: False, 12: True}


# --------------------------------------------------------------------------
# attachment() — the two-machine axis
# --------------------------------------------------------------------------

def test_attachment_maps_build_signal_onto_pids():
    """Two VS Code builds alive: only the one with a connected client counts as attached."""
    res = ta.attachment({302033: "08d4889f", 1442911: "fc3def67", 777: None},
                        {"08d4889f": False, "fc3def67": True})
    assert res == {302033: False, 1442911: True, 777: None}


def test_attachment_never_guesses_when_signal_is_missing():
    """A build we could not measure (ss unavailable, foreign tree) stays None, never False."""
    assert ta.attachment({11: "abc"}, {}) == {11: None}


# --------------------------------------------------------------------------
# self_line() — the SELF check at SessionStart
# --------------------------------------------------------------------------

def test_self_check_names_the_rename_when_own_address_diverged():
    """The 2026-09-03 case, seen from inside: identity @frontend, address 'alice-v2-ea'."""
    lines = ta.self_line({"sessionId": "s1", "name": "alice-v2-ea"}, [("s1", "frontend")])
    assert len(lines) == 1
    assert "THIS window is @frontend" in lines[0] and "/rename frontend" in lines[0]


def test_self_check_silent_when_address_matches():
    assert ta.self_line({"sessionId": "s1", "name": "frontend"}, [("s1", "frontend")]) == []


def test_self_check_silent_when_not_a_registered_identity():
    assert ta.self_line({"sessionId": "s-solo", "name": "repo-1a"}, [("s1", "frontend")]) == []
    assert ta.self_line(None, [("s1", "frontend")]) == []


# --------------------------------------------------------------------------
# format_hook() — what SessionStart injects
# --------------------------------------------------------------------------

def _hook(registry, records, live_pids, attached=None):
    rows, unreg = ta.resolve(registry, records, alive(*live_pids), CWD, attached)
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


def test_double_window_without_signal_warns_clobber():
    lines = _hook([("s1", "frontend")],
                  [rec("s1", "frontend", 11), rec("s1", "frontend", 12)], (11, 12))
    assert any("2 WINDOWS" in l for l in lines)


def test_detached_twin_is_named_with_the_kill_command():
    """The measured shape: the renamed OLD twin is detached, the derived NEW twin is attached."""
    lines = _hook([("s1", "orchestrator")],
                  [rec("s1", "orchestrator", 302033), rec("s1", "alice-v2-ea", 1442911)],
                  (302033, 1442911), attached={302033: False, 1442911: True})
    joined = "\n".join(lines)
    assert "DETACHED" in joined and "pid 302033" in joined
    assert "kill 302033" in joined, "the owner decides, but the exact command must be on the line"
    assert "attached: pid 1442911" in joined


def test_detached_twins_name_does_not_count_as_the_reachable_address():
    """Only the attached twin carries the renamed identity here — the resolver must still tell the
    owner to /rename the ATTACHED one, not report the lane healthy because a dead-end twin is named."""
    lines = _hook([("s1", "orchestrator")],
                  [rec("s1", "orchestrator", 302033), rec("s1", "alice-v2-ea", 1442911)],
                  (302033, 1442911), attached={302033: False, 1442911: True})
    joined = "\n".join(lines)
    assert "ADDRESS ≠ IDENTITY" in joined and "/rename orchestrator" in joined
    assert "address=identity" not in joined
