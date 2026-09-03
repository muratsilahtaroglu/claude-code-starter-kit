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
HOOK = REPO / ".claude" / "hooks" / "entry-budget.py"

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


# --------------------------------------------------------------------------
# TASKS.md — the same mechanism over the board (rules §10.40 "TASKS stays LEAN")
# --------------------------------------------------------------------------
# Measured 2026-09-03 on a live 5-agent project: `## Review` held 12 items in 211 lines — ~18 lines
# per board item, where the rule says id · @owner · due · done-when · evidence path. The board had
# become the place solution notes were written, and TASKS.md is @-imported IN FULL by every lane.

TASK_OK = "- [ ] T1: thing (@dev) — due: 2026-09-10 — done-when: the probe passes\n"
TASK_FAT = "- [ ] T2: thing (@dev) — done-when: x\n" + "  narrative line\n" * 5   # 6 > 4


@pytest.fixture
def board(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / "TASKS.md").write_text(
        "# TASKS\n\n> - doctrine bullet in the header, not an entry\n\n## Now\n" + TASK_OK)
    return tmp_path


def _board_edit(board, old, new):
    return {"tool_input": {"file_path": str(board / "TASKS.md"),
                           "old_string": old, "new_string": new}}


def test_lean_board_item_passes(board):
    rc, _ = run(board, _board_edit(board, TASK_OK, TASK_OK + "- [ ] T3: x (@dev) — done-when: y\n"))
    assert rc == ALLOW


def test_board_item_carrying_a_solution_note_is_blocked(board):
    rc, out = run(board, _board_edit(board, TASK_OK, TASK_OK + TASK_FAT))
    assert rc == BLOCK
    assert "TASKS entry budget (max 4 lines)" in out
    assert "SPEC file" in out, "the message must name where the detail belongs"


def test_lane_heading_ends_a_board_entry(board):
    """`### <lane>` is a write boundary; without it the last item of a lane would swallow the next
    heading and every item under it, and one fat lane would report as one giant entry."""
    rc, _ = run(board, _board_edit(
        board, TASK_OK, TASK_OK + "\n### frontend\n- [ ] F1: x (@fe) — done-when: y\n"))
    assert rc == ALLOW


def test_board_budget_is_tunable(board):
    (board / ".claude" / "keel-caps").write_text("TASKS_ENTRY=20\n")
    rc, _ = run(board, _board_edit(board, TASK_OK, TASK_OK + TASK_FAT))
    assert rc == ALLOW


def test_board_and_lessons_keep_separate_baselines(board):
    """A backlog on one file must not silence or inflate the other's counter."""
    (board / "TASKS.md").write_text("# TASKS\n\n## Now\n" + TASK_FAT)
    rc, out = run(board, {}, mode="--check")
    assert rc == 0
    assert (board / ".claude" / "tasks-backlog").exists()
    assert not (board / ".claude" / "lessons-backlog").exists(), "no LESSONS.md here to account for"


def test_fenced_code_is_neither_an_entry_nor_padding(board):
    """A `- [ ]` inside a code fence (a spec snippet, the doctrine header's example) is quoted text.
    Measured 2026-09-03 before the fix: it became a phantom entry AND the real item before it grew by
    the fence lines — a false BLOCK on an unrelated edit, the gate-with-false-positives class."""
    fence = "```md\n- [ ] example item\n  a\n  b\n  c\n  d\n  e\n```\n"
    rc, _ = run(board, _board_edit(board, TASK_OK, TASK_OK + fence + "- [ ] T9: x (@dev) — done-when: y\n"))
    assert rc == ALLOW
