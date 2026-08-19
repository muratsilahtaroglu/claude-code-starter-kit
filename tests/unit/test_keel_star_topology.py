"""Regression matrix for the star-topology wall — rules.md §10.42.

WHY THIS FILE EXISTS. An agent team is a STAR: the orchestrator assigns, workers deliver back to it,
and no worker talks to another worker. That is not decoration — the shared memory files
(TASKS · LESSONS · HANDOVER · the reports index) have exactly ONE writer, so a decision two workers
reach between themselves is a decision no shared file records.

A permission rule cannot express this: `permissions.deny` takes the BARE tool name, so denying
`SendMessage` would also cut the worker→orchestrator path the whole design runs on. Only a hook can
decide by TARGET, which is why this wall is a hook and why it needs a matrix.

Design + the measurement behind it: docs/steering.md "Agent teams: how a waiting agent
gets woken" and reports/2026-08-19-agent-team-messaging.md.

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "star-topology.sh"

BLOCK = 2
ALLOW = 0

SID = "sess-me-0001"


@pytest.fixture
def team(tmp_path):
    """orchestrator + two workers; this session is @frontend."""
    agents = tmp_path / ".claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "team-orchestrator.md").write_text("Role: orchestrator\n# @orchestrator\n")
    (agents / "team-frontend.md").write_text("Role: worker\n# @frontend\n")
    (agents / "team-provider.md").write_text("Role: worker\n# @provider\n")
    (tmp_path / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-08-19\n")
    return tmp_path


def send(project, to, session_id=SID):
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "SendMessage",
        "session_id": session_id,
        "tool_input": {"to": to, "message": "..."},
    }
    proc = subprocess.run(
        ["bash", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)), cwd=str(project),
    )
    return proc.returncode, proc.stderr


# --------------------------------------------------------------------------
# The one thing it blocks
# --------------------------------------------------------------------------

def test_worker_to_worker_is_blocked(team):
    rc, err = send(team, "provider")
    assert rc == BLOCK
    assert "@frontend may not message @provider" in err
    assert "@orchestrator" in err, "the message must name where to send it instead"


def test_block_survives_the_ref_disambiguator(team):
    """SendMessage accepts `name [ref]`; the wall must not be walked around with one."""
    assert send(team, "provider [3fa9c1]")[0] == BLOCK


def test_block_survives_surrounding_whitespace(team):
    assert send(team, "  provider  ")[0] == BLOCK


# --------------------------------------------------------------------------
# Everything it must NOT break
# --------------------------------------------------------------------------

def test_worker_to_orchestrator_is_allowed(team):
    """The delivery path. Blocking this would break the whole design."""
    assert send(team, "orchestrator")[0] == ALLOW


def test_orchestrator_may_message_anyone(team):
    (team / ".claude" / "agent-team-sessions").write_text(f"{SID} orchestrator 2026-08-19\n")
    for target in ("frontend", "provider", "orchestrator"):
        assert send(team, target)[0] == ALLOW, target


def test_target_outside_the_roster_is_allowed(team):
    """An unrelated peer session, a subagent, or "main" — not a teammate, not our business."""
    for target in ("main", "researcher", "db-migrate-21", "some-other-session"):
        assert send(team, target)[0] == ALLOW, target


def test_session_with_no_adopted_identity_is_allowed(team):
    assert send(team, "provider", session_id="sess-stranger")[0] == ALLOW


def test_solo_project_pays_nothing(tmp_path):
    """No roster at all: the hook must exit before doing any work."""
    (tmp_path / ".claude").mkdir()
    assert send(tmp_path, "anyone")[0] == ALLOW


def test_other_tools_are_untouched(team):
    payload = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
               "session_id": SID, "tool_input": {"command": "ls"}}
    proc = subprocess.run(["bash", str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True,
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(team)), cwd=str(team))
    assert proc.returncode == ALLOW


def test_fails_open_on_unparseable_input(team):
    proc = subprocess.run(["bash", str(HOOK)], input="not json",
                          capture_output=True, text=True,
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(team)), cwd=str(team))
    assert proc.returncode == ALLOW, "a broken guard must not brick the session"


# --------------------------------------------------------------------------
# It records what it did
# --------------------------------------------------------------------------

def test_block_is_recorded_with_attribution(team):
    send(team, "provider")
    log = (team / ".claude" / "ritual-log").read_text()
    assert "@frontend star-topology BLOCK: -> @provider" in log


def test_no_telemetry_from_a_probe_run(team):
    """Same contract as every other hook: no CLAUDE_PROJECT_DIR, no writing to a live log."""
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    payload = {"hook_event_name": "PreToolUse", "tool_name": "SendMessage",
               "session_id": SID, "tool_input": {"to": "provider"}}
    subprocess.run(["bash", str(HOOK)], input=json.dumps(payload),
                   capture_output=True, text=True, env=env, cwd=str(team))
    assert not (team / ".claude" / "ritual-log").exists()
