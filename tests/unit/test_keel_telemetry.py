"""Regression matrix for Keel's OBSERVABILITY layer — rules.md §9, §10.37.

WHY THIS FILE EXISTS. The enforcement hooks were covered by `test_keel_hooks.py`, but nothing
covered the layer that answers "did the ritual actually run?". Two defects lived there
undetected and cost real trust on 2026-08-19:

  1. `.claude/ritual-log` defaulted to `.` when `CLAUDE_PROJECT_DIR` was unset, so ad-hoc probe
     runs wrote into the LIVE telemetry. The duplicate-line detector then reported "hooks are
     double-firing — uninstall that plugin" at every session start for two days; 10 of its 11
     hits were test runs and the machine had no plugin installed.
  2. The same detector counted repeated BLOCK lines as evidence of double registration, which
     they are not: one guard legitimately stops two commands of the same class in a row.

And two gaps: Stop hooks left no trace at all, and every session of an agent team wrote to one
log with no attribution. Evidence: reports/2026-08-19-observability-audit.md.

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
Run: `make test` or `pytest tests/unit/test_keel_telemetry.py -v`.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".claude" / "hooks"
REPORT = REPO / ".claude" / "ritual-report.py"

SID = "sess-abc123"


def run_hook(script, payload, project_dir, with_project_dir=True):
    """Run a hook. with_project_dir=False simulates an ad-hoc probe: Claude Code always
    exports CLAUDE_PROJECT_DIR to a real hook invocation, a hand-piped payload does not."""
    env = dict(os.environ)
    env.pop("CLAUDE_PROJECT_DIR", None)
    if with_project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    proc = subprocess.run(
        ["bash", str(HOOKS / script)],
        input=json.dumps(payload), capture_output=True, text=True,
        env=env, cwd=str(project_dir),
    )
    return proc.returncode, proc.stdout + proc.stderr


def log_lines(project_dir):
    p = project_dir / ".claude" / "ritual-log"
    return p.read_text().splitlines() if p.exists() else []


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".claude").mkdir()
    return tmp_path


@pytest.fixture
def team_project(project):
    """A project with an agent-team roster and this session mapped to @frontend."""
    (project / ".claude" / "agents").mkdir()
    (project / ".claude" / "agents" / "team-frontend.md").write_text("Role: worker\n")
    (project / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-08-19\n")
    return project


# --------------------------------------------------------------------------
# A1 — every line carries the writing session's @agent
# --------------------------------------------------------------------------

def test_ritual_log_tags_the_writing_agent(team_project):
    run_hook("ritual-log.sh",
             {"hook_event_name": "PreCompact", "trigger": "manual", "session_id": SID},
             team_project)
    assert log_lines(team_project)[-1].endswith("@frontend compact manual"), log_lines(team_project)


def test_ritual_log_untagged_when_session_adopted_no_identity(team_project):
    run_hook("ritual-log.sh",
             {"hook_event_name": "PreCompact", "trigger": "manual", "session_id": "sess-stranger"},
             team_project)
    assert log_lines(team_project)[-1].endswith("compact manual")
    assert "@" not in log_lines(team_project)[-1]


def test_ritual_log_untagged_on_a_solo_project(project):
    """No roster, no map — a single-user project pays nothing and never sees a tag."""
    run_hook("ritual-log.sh",
             {"hook_event_name": "SessionStart", "source": "startup", "session_id": SID},
             project)
    assert log_lines(project)[-1].endswith("session-start startup")
    assert "@" not in log_lines(project)[-1]


# --------------------------------------------------------------------------
# A4 — telemetry never written from a probe run
# --------------------------------------------------------------------------

@pytest.mark.parametrize("script,payload", [
    ("ritual-log.sh", {"hook_event_name": "SessionStart", "source": "startup"}),
    ("block-dangerous.sh", {"tool_input": {"command": "rm -rf /"}}),
])
def test_no_telemetry_without_project_dir(script, payload, project):
    """The measurement must not contaminate what it measures."""
    run_hook(script, payload, project, with_project_dir=False)
    assert not (project / ".claude" / "ritual-log").exists(), (
        "a probe run wrote into the live telemetry — this is the defect that produced two days "
        "of false 'hooks are double-firing' warnings"
    )


def test_block_still_blocks_without_project_dir(project):
    """Telemetry is optional; the guard is not. Losing the log must never lose the wall."""
    rc, out = run_hook("block-dangerous.sh",
                       {"tool_input": {"command": "rm -rf /"}}, project,
                       with_project_dir=False)
    assert rc == 2, out


# --------------------------------------------------------------------------
# A2 — Stop hooks leave a trace when they actually nudge
# --------------------------------------------------------------------------

def _git(*args, cwd):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def test_handover_reminder_records_its_nudge(project):
    _git("init", "-q", ".", cwd=project)
    _git("config", "user.name", "t", cwd=project)
    _git("config", "user.email", "t@x", cwd=project)
    (project / "src.py").write_text("x = 1\n")          # dirty tree, HANDOVER untouched
    (project / "HANDOVER.md").write_text("# H\n")
    _git("add", "HANDOVER.md", cwd=project)
    _git("commit", "-qm", "seed", cwd=project)
    _, out = run_hook("handover-reminder.sh", {"hook_event_name": "Stop"}, project)
    assert "systemMessage" in out, out
    assert any(l.endswith("nudge handover") for l in log_lines(project)), log_lines(project)


def test_handover_reminder_silent_and_traceless_on_a_clean_tree(project):
    _git("init", "-q", ".", cwd=project)
    _git("config", "user.name", "t", cwd=project)
    _git("config", "user.email", "t@x", cwd=project)
    (project / "HANDOVER.md").write_text("# H\n")
    _git("add", "-A", cwd=project)
    _git("commit", "-qm", "seed", cwd=project)
    _, out = run_hook("handover-reminder.sh", {"hook_event_name": "Stop"}, project)
    assert "systemMessage" not in out
    assert not any("nudge" in l for l in log_lines(project)), (
        "a nudge was logged that never fired — the log would claim enforcement that did not happen"
    )


# --------------------------------------------------------------------------
# A3 — the duplicate detector proves double-firing, not normal blocking
# --------------------------------------------------------------------------

def _reground(project):
    return run_hook("session-start-reground.sh", {"source": "startup"}, project)[1]


def test_repeated_event_lines_are_flagged(project):
    (project / ".claude" / "ritual-log").write_text(
        "2026-08-19 12:00:00 session-start startup\n" * 4)
    assert "double-firing" in _reground(project)


def test_repeated_block_lines_are_not_double_firing(project):
    """One guard legitimately stops several commands of the same class in a row."""
    (project / ".claude" / "ritual-log").write_text(
        "2026-08-19 12:00:00 block-dangerous BLOCK: recursive delete of root/home/cwd\n" * 6)
    assert "double-firing" not in _reground(project)


# --------------------------------------------------------------------------
# A5 — the report separates "nothing happened" from "the event never arrived"
# --------------------------------------------------------------------------

def _render(tmp_path, log_text):
    root = tmp_path / "proj"
    (root / ".claude").mkdir(parents=True)
    (root / "reports").mkdir()
    (root / ".claude" / "ritual-log").write_text(log_text)
    script = root / ".claude" / "ritual-report.py"
    script.write_text(REPORT.read_text())
    subprocess.run(["python3", str(script)], check=True, capture_output=True)
    return (root / "reports" / "ritual-stats.md").read_text()


ALL_KINDS = (
    "2026-08-19 10:00:00 session-start startup\n"
    "2026-08-19 10:01:00 skill keel-handover\n"
    "2026-08-19 10:02:00 command keel-compact\n"
    "2026-08-19 10:03:00 nudge handover\n"
    "2026-08-19 10:04:00 compact manual\n"
)


def test_report_flags_event_kinds_that_never_arrived(tmp_path):
    out = _render(tmp_path, "2026-08-19 10:00:00 session-start startup\n"
                            "2026-08-19 10:04:00 compact manual\n")
    assert "No record of:" in out
    assert "`skill`" in out and "`command`" in out and "`nudge`" in out
    assert "statement about the" in out and "INSTRUMENT" in out


def test_report_quiet_when_every_kind_is_present(tmp_path):
    assert "No record of:" not in _render(tmp_path, ALL_KINDS)


def test_report_lists_the_agents_writing_to_the_log(tmp_path):
    out = _render(tmp_path, ALL_KINDS.replace("10:01:00 skill", "10:01:00 @frontend skill")
                                     .replace("10:04:00 compact", "10:04:00 @orchestrator compact"))
    assert "@frontend" in out and "@orchestrator" in out
