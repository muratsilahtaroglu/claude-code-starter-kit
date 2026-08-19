"""Regression matrix for agent-team identity resolution — rules.md §10.42.

WHY THIS FILE EXISTS. Field case 2026-08-19 (alice_v2): a VS Code restart left the session id and
`.claude/agent-team-sessions` mapping completely intact — the reground hook re-injected the right
identity — but `/list-agents` went back to showing the window under its directory-derived name.
The orchestrator read "the name I know is unreachable" as "the session is dead" and broadcast a
needless re-identify to three live workers, one step from a double-ownership assignment.

The mapping's date column was write-once ("adopted on"), so nothing distinguished a quiet-but-alive
lane from a dead one. Fix: the reground hook now touches a resolved session's date to TODAY on
every SessionStart, turning it into a LAST-SEEN heartbeat `/keel-continue`'s orchestrator branch can
check before declaring a lane free. Design: docs/steering.md "Addressing: the session name IS the
address".

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "session-start-reground.sh"

SID = "sess-frontend-001"
TODAY = datetime.now().strftime("%Y-%m-%d")
OLD = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")


def run(project, payload):
    proc = subprocess.run(
        ["bash", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)), cwd=str(project),
    )
    return proc.returncode, proc.stdout + proc.stderr


def mapping_lines(project):
    p = project / ".claude" / "agent-team-sessions"
    return p.read_text().splitlines() if p.exists() else []


@pytest.fixture
def team(tmp_path):
    agents = tmp_path / ".claude" / "agents"
    agents.mkdir(parents=True)
    (agents / "team-orchestrator.md").write_text("Role: orchestrator\n# @orchestrator\n")
    (agents / "team-frontend.md").write_text("Role: worker\n# @frontend\n")
    (agents / "team-provider.md").write_text("Role: worker\n# @provider\n")
    (tmp_path / ".claude" / "agent-team-sessions").write_text(
        f"{SID} frontend {OLD}\nsess-provider-999 provider {OLD}\n"
    )
    (tmp_path / "TASKS.md").write_text("# TASKS.md\n\n## Now\n")
    return tmp_path


def test_resolving_identity_touches_this_sessions_date_to_today(team):
    run(team, {"hook_event_name": "SessionStart", "source": "startup", "session_id": SID})
    lines = mapping_lines(team)
    assert f"{SID} frontend {TODAY}" in lines, lines


def test_touching_one_session_leaves_the_others_dates_alone(team):
    run(team, {"hook_event_name": "SessionStart", "source": "startup", "session_id": SID})
    lines = mapping_lines(team)
    assert f"sess-provider-999 provider {OLD}" in lines, (
        "resolving @frontend's identity must not touch @provider's heartbeat"
    )


def test_unresolved_session_id_does_not_write_a_new_line(team):
    run(team, {"hook_event_name": "SessionStart", "source": "startup", "session_id": "sess-nobody"})
    lines = mapping_lines(team)
    assert len(lines) == 2, "an unmapped session must not fabricate a mapping row"


def test_agent_identity_message_still_names_the_session_id(team):
    _, out = run(team, {"hook_event_name": "SessionStart", "source": "startup", "session_id": SID})
    assert f"Session-id: {SID}" in out


def test_no_team_no_mapping_file_is_a_silent_noop(tmp_path):
    """Solo project: no .claude/agents/team-*.md at all — the identity block must not run."""
    (tmp_path / ".claude").mkdir()
    (tmp_path / "TASKS.md").write_text("# TASKS.md\n\n## Now\n")
    rc, _ = run(tmp_path, {"hook_event_name": "SessionStart", "source": "startup", "session_id": SID})
    assert rc == 0
    assert not (tmp_path / ".claude" / "agent-team-sessions").exists()
