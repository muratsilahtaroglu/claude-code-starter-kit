"""Regression matrix for `.claude/keel-compact-check.py` — /keel-compact's mechanical half in ONE call.

WHY THIS FILE EXISTS. On a live 5-agent project the freshness checklist cost 17 / 25 / 59 tool turns
per ritual, at the fullest context of the session (~37M cache reads for one run); the script turns it
into one call. A gate that replaces a checklist must be proven to go RED on each thing the checklist
caught — and to FAIL CLOSED (rc=2) when it cannot run, because a silent green is worse than no gate.

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import datetime
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / ".claude" / "keel-compact-check.py"
TODAY = datetime.date.today().isoformat()


def sh(*args, cwd):
    subprocess.run(args, cwd=str(cwd), check=True, capture_output=True)


@pytest.fixture
def project(tmp_path):
    """A healthy, just-handed-over project: every mechanical gate should be green."""
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    for f in ("entry-budget.py", "citation-gate.py"):
        (tmp_path / ".claude" / "hooks" / f).write_text((REPO / ".claude" / "hooks" / f).read_text())
    (tmp_path / "HANDOVER.md").write_text("# HANDOVER\n\n### %s 10:00 — @t — ok\n- (a) done\n" % TODAY)
    (tmp_path / "TASKS.md").write_text("# TASKS\n\n## Now\n- [ ] T1: x — done-when: y\n")
    sh("git", "init", "-q", ".", cwd=tmp_path)
    sh("git", "-c", "user.name=t", "-c", "user.email=t@e", "add", "-A", cwd=tmp_path)
    sh("git", "-c", "user.name=t", "-c", "user.email=t@e", "commit", "-qm", "base", cwd=tmp_path)
    return tmp_path


def copy_script(project):
    """Run the script FROM the project so it resolves the project's own hooks, like a clone does."""
    dst = project / ".claude" / "keel-compact-check.py"
    dst.write_text(SCRIPT.read_text())
    return dst


def run_local(project):
    dst = copy_script(project)
    p = subprocess.run(["python3", str(dst)], cwd=str(project), capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)))
    return p.returncode, p.stdout + p.stderr


def test_a_fresh_project_passes_and_still_prints_the_human_step(project):
    rc, out = run_local(project)
    assert rc == 0, out
    assert "VERDICT: PASS" in out
    assert "§9.31 sweep" in out, "the unmeasurable half must be printed, never faked"


def test_one_huge_line_is_red_even_under_the_line_cap(project):
    """The field case: 146/150 lines, green on every line cap, 244 KB because of one line."""
    (project / "HANDOVER.md").write_text(
        "# HANDOVER\n\n### %s 10:00 — @t — ok\n- (a) %s\n" % (TODAY, "n" * 30000))
    rc, out = run_local(project)
    assert rc == 1
    assert "longest line 4" in out and "KB" in out


def test_a_top_block_from_another_day_is_red_and_a_date_range_heading_is_accepted(project):
    (project / "HANDOVER.md").write_text("# HANDOVER\n\n### 2020-01-01 10:00 — old\n- (a) x\n")
    rc, out = run_local(project)
    assert rc == 1 and "top block is 2020-01-01" in out
    (project / "HANDOVER.md").write_text("# HANDOVER\n\n### 2020-01-01 → %s — spans days\n" % TODAY)
    _, out = run_local(project)
    assert "top block heading carries %s" % TODAY in out


def test_stale_disk_debt_is_red_until_handover_is_newer(project):
    old = datetime.datetime.now() - datetime.timedelta(hours=1)
    os.utime(project / "HANDOVER.md", (old.timestamp(), old.timestamp()))
    stamp = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    (project / ".claude" / "ritual-log").write_text(stamp + " compact auto STALE-DISK: tree dirty\n")
    rc, out = run_local(project)
    assert rc == 1 and "crossed a dirty tree" in out


def test_now_limit_is_per_lane_on_a_team_board(project):
    lane = "".join("- [ ] co%d: x — done-when: y\n" % i for i in range(4))
    (project / "TASKS.md").write_text("# TASKS\n\n## Now\n### alpha\n%s### beta\n%s" % (lane, lane))
    rc, out = run_local(project)
    assert "alpha 4 · beta 4" in out and "RED  ## Now" not in out, "8 on the board, 4 per lane"
    (project / "TASKS.md").write_text("# TASKS\n\n## Now\n### alpha\n%s%s" % (lane, lane))
    _, out = run_local(project)
    assert "RED  ## Now" in out


def test_review_line_without_an_existing_note_is_red(project):
    (project / "TASKS.md").write_text(
        "# TASKS\n\n## Now\n\n## Review\n- [x] T1 (@t) — evidence: reports/team/t/T1_fix.md\n")
    rc, out = run_local(project)
    assert rc == 1 and "without an existing note file" in out


def test_a_ghost_citation_is_red(project):
    (project / "reports").mkdir()
    (project / "reports" / "ghost.md").write_text("never staged\n")
    (project / "TASKS.md").write_text("# TASKS\n\n## Now\n- [ ] T1: see reports/ghost.md\n")
    rc, out = run_local(project)
    assert rc == 1 and "RED  ghost citations" in out


def test_instrument_fault_fails_closed(project):
    (project / ".claude" / "hooks" / "citation-gate.py").write_text("raise SystemError('boom')\n")
    rc, out = run_local(project)
    assert rc == 2 and "INSTRUMENT FAULT" in out


def test_defaults_equal_the_session_start_hook():
    """Two readers of the same caps must agree on the defaults, or one of them is lying."""
    src = SCRIPT.read_text()
    hook = (REPO / ".claude" / "hooks" / "session-start-reground.sh").read_text()
    code = next(l for l in hook.splitlines() if l.startswith("kb_H="))
    for key, var in (("HANDOVER_KB", "kb_H"), ("LESSONS_KB", "kb_L"), ("TASKS_KB", "kb_T"),
                     ("RULES_KB", "kb_R"), ("CLAUDE_KB", "kb_C"), ("CONTEXT_KB", "kb_ALL")):
        assert '"%s": %s' % (key, code.split(var + "=")[1].split(";")[0].strip()) in src
    lines = next(l for l in hook.splitlines() if l.startswith("cap_H="))
    for key, var in (("HANDOVER", "cap_H"), ("LESSONS", "cap_L"), ("TASKS", "cap_T"),
                     ("RULES", "cap_R"), ("HANDOVER_BLOCKS", "cap_B")):
        assert '"%s": %s' % (key, lines.split(var + "=")[1].split(";")[0].strip()) in src


# Pre-release review findings (2026-09-25), each pinned.

def test_one_existing_path_does_not_vouch_for_a_missing_evidence_note(project):
    """It used to PASS when ANY path on the line existed; the SessionStart hook says MISSING."""
    (project / "docs").mkdir()
    (project / "docs" / "steering.md").write_text("x\n")
    (project / "TASKS.md").write_text(
        "# TASKS\n\n## Now\n\n## Review\n"
        "- [x] T1 (@t) — evidence: reports/team/t/T1_fix_MISSING.md (per docs/steering.md)\n")
    rc, out = run_local(project)
    assert rc == 1 and "without an existing note file" in out


def test_a_raised_line_cap_scales_its_kb_default_and_an_explicit_kb_wins(project):
    """A live project set LESSONS=1000 and met a hidden 40 KB default — a second, silent limit."""
    (project / "LESSONS.md").write_text("# LESSONS\n" + ("- 2026-01-01 — %s\n" % ("w" * 90)) * 500)
    (project / ".claude" / "keel-caps").write_text("LESSONS=1000\n")
    _, out = run_local(project)
    assert "/160 KB" in out and "RED  LESSONS.md" not in out
    (project / ".claude" / "keel-caps").write_text("LESSONS=1000\nLESSONS_KB=20\n")
    _, out = run_local(project)
    assert "RED  LESSONS.md" in out


def test_kb_scaling_agrees_with_the_session_start_hook(project):
    (project / "LESSONS.md").write_text("# LESSONS\n" + ("- 2026-01-01 — %s\n" % ("w" * 90)) * 500)
    (project / ".claude" / "keel-caps").write_text("LESSONS=1000\n")
    hook = subprocess.run(["bash", str(REPO / ".claude" / "hooks" / "session-start-reground.sh")],
                          input="{}", capture_output=True, text=True, cwd=str(project),
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)))
    assert "LESSONS.md is" not in hook.stdout, "the hook must scale exactly like the script"
    (project / ".claude" / "keel-caps").write_text("LESSONS=1000\nLESSONS_KB=20\n")
    hook = subprocess.run(["bash", str(REPO / ".claude" / "hooks" / "session-start-reground.sh")],
                          input="{}", capture_output=True, text=True, cwd=str(project),
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)))
    assert "LESSONS.md is " in hook.stdout and "(cap 20 KB" in hook.stdout


def test_an_unreadable_stale_disk_marker_is_not_settled(project):
    (project / ".claude" / "ritual-log").write_text("garbage-time compact auto STALE-DISK: x\n")
    rc, out = run_local(project)
    assert rc == 1 and "crossed a dirty tree" in out
