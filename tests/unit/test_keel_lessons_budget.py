"""Regression matrix for the LESSONS per-entry line budget — rules.md §10.38 ("enforced beats
written") applied to memory bloat.

WHY THIS FILE EXISTS. Measured on a live project (alice_v2, 2026-08-25): LESSONS grew 450 -> 1039
lines in five days while entry COUNT grew only 1.5x — entries were getting LONGER, so raising the
file cap "was never enough" (owner's words). The original hook checked only the written FRAGMENT,
so folding new material into an existing entry passed unseen — and that fold-in habit is exactly
what cap pressure produces (its backlog rose 41 -> 43 in three days). The kit's version simulates
the post-edit FILE, closing that blind spot; this matrix pins both the gate and the blind-spot fix.

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "lessons-entry-budget.py"

BLOCK = 2
ALLOW = 0

SHORT = "- 2026-08-27 — short entry\n  one detail line\n"
LONG_9 = "- 2026-08-27 — long entry\n" + "  detail\n" * 8   # 9 lines > 8 budget


def run(project, payload, mode="--hook"):
    proc = subprocess.run(
        ["python3", str(HOOK), mode], input=json.dumps(payload), capture_output=True, text=True,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=str(project)), cwd=str(project),
    )
    return proc.returncode, proc.stdout + proc.stderr


@pytest.fixture
def project(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / "LESSONS.md").write_text("# LESSONS\n\n## [rule]\n" + SHORT)
    return tmp_path


def edit(project, old, new):
    return {"tool_input": {"file_path": str(project / "LESSONS.md"),
                           "old_string": old, "new_string": new}}


def write(project, content):
    return {"tool_input": {"file_path": str(project / "LESSONS.md"), "content": content}}


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------

def test_short_new_entry_passes(project):
    rc, _ = run(project, edit(project, SHORT, SHORT + "- 2026-08-27 — another\n  fine\n"))
    assert rc == ALLOW


def test_oversized_new_entry_is_blocked(project):
    rc, out = run(project, edit(project, SHORT, SHORT + LONG_9))
    assert rc == BLOCK
    assert "RULE · MECHANISM · CHECK" in out, "the block must teach the entry shape"


def test_fold_in_growth_is_blocked_the_original_blind_spot(project):
    """An Edit whose new_string carries NO dated line — material folded INTO an existing entry,
    pushing it over budget. The original hook waved this through."""
    rc, _ = run(project, edit(project, "  one detail line\n", "  one detail line\n" + "  more\n" * 8))
    assert rc == BLOCK


def test_shrinking_an_oversized_entry_always_passes(project):
    (project / "LESSONS.md").write_text("# LESSONS\n\n## [rule]\n" + LONG_9)
    rc, _ = run(project, edit(project, "  detail\n  detail\n", "  detail\n"))
    assert rc == ALLOW, "cleanup of old backlog must never be punished"


def test_write_of_a_whole_file_with_an_oversized_entry_is_blocked(project):
    rc, _ = run(project, write(project, "# LESSONS\n\n## [rule]\n" + LONG_9))
    assert rc == BLOCK


def test_pre_existing_backlog_does_not_block_unrelated_edits(project):
    """Old oversized entries are the --check baseline's job, not the write gate's."""
    (project / "LESSONS.md").write_text("# LESSONS\n\n## [rule]\n" + LONG_9 + SHORT)
    rc, _ = run(project, edit(project, "short entry", "short entry (edited)"))
    assert rc == ALLOW


def test_other_files_are_untouched(project):
    payload = {"tool_input": {"file_path": str(project / "TASKS.md"),
                              "old_string": "x", "new_string": "y" * 5000}}
    assert run(project, payload)[0] == ALLOW


def test_cap_is_tunable_via_keel_caps(project):
    (project / ".claude" / "keel-caps").write_text("LESSONS_ENTRY=12\n")
    rc, _ = run(project, edit(project, SHORT, SHORT + LONG_9))
    assert rc == ALLOW, "a project that raised the per-entry cap to 12 must not be blocked at 9"


def test_fails_open_on_unparseable_input(project):
    proc = subprocess.run(["python3", str(HOOK), "--hook"], input="not json",
                          capture_output=True, text=True, cwd=str(project))
    assert proc.returncode == ALLOW


# --------------------------------------------------------------------------
# --check: the monotone baseline
# --------------------------------------------------------------------------

def test_check_is_silent_and_seeds_baseline_on_first_run(project):
    (project / "LESSONS.md").write_text("# LESSONS\n\n## [rule]\n" + LONG_9)
    rc, out = run(project, {}, mode="--check")
    assert rc == 0 and "GREW" not in out
    assert (project / ".claude" / "lessons-backlog").read_text().startswith("1 ")


def test_check_warns_only_when_the_backlog_grew(project):
    (project / ".claude" / "lessons-backlog").write_text("0\n")
    (project / "LESSONS.md").write_text("# LESSONS\n\n## [rule]\n" + LONG_9)
    rc, out = run(project, {}, mode="--check")
    assert rc == 0 and "GREW: 0 -> 1" in out
    assert (project / ".claude" / "lessons-backlog").read_text().startswith("0"), (
        "the baseline is never auto-raised — a grown count warns, it does not move the bar"
    )


def test_check_auto_lowers_the_baseline(project):
    (project / ".claude" / "lessons-backlog").write_text("5\n")
    rc, out = run(project, {}, mode="--check")
    assert rc == 0 and "shrank: 5 -> 0" in out
    assert (project / ".claude" / "lessons-backlog").read_text().startswith("0")
