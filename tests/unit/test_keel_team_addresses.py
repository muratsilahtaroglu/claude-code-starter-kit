"""Regression matrix for the agent-team address resolver — rules.md §10.42.

WHY THIS FILE EXISTS. A session's NAME is process-local (`~/.claude/sessions/<PID>.json`, keyed by
pid) and silently reverts on every window/process recreation; the IDENTITY lives on disk keyed by
session-id and survives. Confusing the two cost a live team a broadcast re-identify and nearly a
double-assigned lane (2026-08-19), and its rarer sibling — one session-id driven from TWO windows —
is the silent-clobber shape §10.42 exists to prevent. On 2026-09-03 that sibling turned out to be
the NORMAL case: every reconnect (sleep, tunnel, a second machine) resumes the SAME session id in a
NEW process, so twins accumulate on their own. The first port picked the live twin by `attached`,
which is computed per VS Code BUILD and read True for 11 of 11 processes (2026-09-06); the right
axis is START TIME — the newest process is live, older ones are lossless leftovers. The resolver's core is pure, so this matrix feeds it
fixtures directly. Backported from alice_v2 (`scripts/team_addresses.py`, 2026-08-24).

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import re
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
                     "status": "OK", "cwd": CWD, "windows": 1, "attached": None,
                     "leftover": None, "started": None}]
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

def _hook(registry, records, live_pids, attached=None, started=None):
    rows, unreg = ta.resolve(registry, records, alive(*live_pids), CWD, attached, started)
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


def test_the_newest_process_of_a_session_id_is_live_and_the_older_are_leftovers():
    """Owner 2026-09-06, measured the same day: a reconnect respawns the SAME session-id in a NEW
    process, so the LIVE twin is the newest by START TIME. `attached` is deliberately set to the
    OPPOSITE of the verdict here — it must not be able to change the answer, because it is computed
    per VS Code BUILD (11 of 11 processes read attached in the live measurement)."""
    lines = _hook([("s1", "orchestrator")],
                  [rec("s1", "orchestrator", 302033), rec("s1", "alice-v2-ea", 1442911)],
                  (302033, 1442911),
                  attached={302033: True, 1442911: False},
                  started={302033: 100, 1442911: 900})
    joined = "\n".join(lines)
    assert "NEWEST (pid 1442911)" in joined
    assert "leftovers: pid 302033" in joined
    assert "LOSSLESS" in joined
    # The word may appear as a PROHIBITION ("do NOT kill by pid"); what must never appear is a
    # runnable `kill <pid>` command, because pids are recycled and a frozen one is a security error.
    assert not re.search(r"kill\s+\d", joined)
    assert "do NOT kill by pid" in joined


def test_a_leftovers_name_does_not_count_as_the_reachable_address():
    """The renamed identity sits on the OLD process; the reachable address is the newest one, so the
    owner must still be told to /rename it — not shown a healthy lane because a leftover is named."""
    lines = _hook([("s1", "orchestrator")],
                  [rec("s1", "orchestrator", 302033), rec("s1", "alice-v2-ea", 1442911)],
                  (302033, 1442911), started={302033: 100, 1442911: 900})
    joined = "\n".join(lines)
    assert "ADDRESS ≠ IDENTITY" in joined and "/rename orchestrator" in joined
    assert "address=identity" not in joined


def test_unmeasured_start_time_is_never_called_a_leftover():
    """UNKNOWN is not OLD. With no start times the twin warning still fires (two windows IS a
    clobber risk) but it must NOT name a leftover, because nothing measured which is older."""
    lines = _hook([("s1", "orchestrator")],
                  [rec("s1", "orchestrator", 302033), rec("s1", "orchestrator", 1442911)],
                  (302033, 1442911))
    joined = "\n".join(lines)
    assert "WINDOWS" in joined and "UNMEASURED" in joined
    assert "leftovers" not in joined and not re.search(r"kill\s+\d", joined)
