"""Regression matrix for the LESSONS per-entry line budget — rules.md §10.38 ("enforced beats
written") applied to memory bloat.

WHY THIS FILE EXISTS. Measured on a live project (2026-08-25): LESSONS grew 450 -> 1039
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
    # The banner names BOTH axes since the character budget landed (2026-09-06), so this
    # pins what the verdict MEANS — the LINE axis fired and named the count — instead of the
    # exact sentence. A cell that pins prose reddens on wording; this one reddens on behaviour.
    assert "TASKS entry budget (max 4 lines" in out
    assert "6 lines —" in out
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


# 2026-09-06: the CHARACTER axis. Its whole point is the case the LINE budget cannot see, so the
# fixture is deliberately 1 line — if this cell ever passes with a line-count message, the axis is dead.
TASK_LONG_ONE_LINER = "- [ ] T3: thing (@dev) — done-when: " + "y" * 500 + "\n"


def test_one_line_item_over_the_character_budget_is_blocked(board):
    rc, out = run(board, _board_edit(board, TASK_OK, TASK_OK + TASK_LONG_ONE_LINER))
    assert rc == BLOCK
    assert "characters —" in out          # the CHARACTER axis fired...
    assert "lines —" not in out           # ...and the line axis did NOT: 1 line is under the cap


def test_character_budget_is_tunable_via_keel_caps(board):
    (board / ".claude" / "keel-caps").write_text("TASKS_ENTRY_CHARS=9000\n", encoding="utf-8")
    rc, _ = run(board, _board_edit(board, TASK_OK, TASK_OK + TASK_LONG_ONE_LINER))
    assert rc == ALLOW


def test_shrinking_a_character_oversized_item_still_passes(board):
    """The cell that pins WHY sizes are kept per AXIS (2026-09-06).

    Measured with a mutation rather than reasoned: collapsing the two axes into one key does NOT
    let a growing character count hide (the first thing I wrote, and it was wrong in DIRECTION) --
    it breaks MONOTONE DESCENT, because the remembered LINE count is tiny next to any character
    count, so a SHRINKING entry compares against it and blocks. That turns the budget into the
    always-red gate this project refuses to build."""
    fat = "- [ ] T4: thing (@dev) — done-when: " + "z" * 900 + "\n"
    less = "- [ ] T4: thing (@dev) — done-when: " + "z" * 500 + "\n"
    (board / "TASKS.md").write_text("# TASKS\n\n## Now\n" + TASK_OK + fat, encoding="utf-8")
    rc, _ = run(board, _board_edit(board, fat, less))
    assert rc == ALLOW


# --------------------------------------------------------------------------
# Per-LINE cap on every always-loaded file (2026-09-25). The field case: HANDOVER at 146/150 lines —
# green on every line/entry cap — had grown to 244 KB because ONE line held 135 KB, and auto-compact
# fired three times in five minutes. None of the caps above could see a line's LENGTH.
# --------------------------------------------------------------------------

def _root_edit(root, name, old, new):
    return {"tool_input": {"file_path": str(root / name), "old_string": old, "new_string": new}}


@pytest.fixture
def handover(tmp_path):
    (tmp_path / ".claude").mkdir()
    (tmp_path / "HANDOVER.md").write_text("# HANDOVER\n\n### 2026-09-25 — x\n- (a) short fact\n")
    return tmp_path


def test_a_new_long_line_in_handover_is_blocked(handover):
    """The 135 KB line: HANDOVER has no entry profile, so before this axis nothing looked at it."""
    rc, out = run(handover, _root_edit(handover, "HANDOVER.md", "- (a) short fact\n",
                                       "- (a) short fact\n- (a) " + "narrative " * 60 + "\n"))
    assert rc == BLOCK
    assert "per-LINE cap EXCEEDED" in out and "One line = one fact" in out


def test_shortening_a_long_line_passes_and_lengthening_it_blocks(handover):
    """Monotone descent by DOMINANCE: a verbatim-only test blocked the SHORTENING edit (tried first)."""
    long = "- (a) " + "x" * 900
    (handover / "HANDOVER.md").write_text("# HANDOVER\n\n" + long + "\n")
    assert run(handover, _root_edit(handover, "HANDOVER.md", long, "- (a) " + "x" * 500))[0] == ALLOW
    assert run(handover, _root_edit(handover, "HANDOVER.md", long, "- (a) " + "x" * 950))[0] == BLOCK


def test_a_second_long_line_blocks_even_beside_a_longer_old_one(handover):
    """Dominance, not max: keeping the 900-char line and ADDING a 500-char one is worse, not equal."""
    long = "- (a) " + "x" * 900
    (handover / "HANDOVER.md").write_text("# HANDOVER\n\n" + long + "\n")
    rc, _ = run(handover, _root_edit(handover, "HANDOVER.md", long, long + "\n- (a) " + "y" * 500))
    assert rc == BLOCK


def test_line_cap_is_tunable_and_only_guards_the_project_root(handover):
    (handover / ".claude" / "keel-caps").write_text("HANDOVER_LINE_CHARS=2000\n")
    edit = _root_edit(handover, "HANDOVER.md", "- (a) short fact\n", "- (a) " + "z" * 900 + "\n")
    assert run(handover, edit)[0] == ALLOW
    (handover / "docs").mkdir()
    (handover / "docs" / "HANDOVER.md").write_text("- (a) short fact\n")
    nested = _root_edit(handover, "docs/HANDOVER.md", "- (a) short fact\n", "- " + "z" * 5000 + "\n")
    assert run(handover, nested)[0] == ALLOW, "a docs/ copy is not @-imported and is not guarded"


def test_rules_and_claude_md_are_guarded_too(handover):
    (handover / "rules.md").write_text("# rules\n1. short rule\n")
    rc, _ = run(handover, _root_edit(handover, "rules.md", "1. short rule\n", "1. " + "w" * 700 + "\n"))
    assert rc == BLOCK


# Pre-release review findings (2026-09-25), each pinned.

def _load_hook():
    import importlib.util
    spec = importlib.util.spec_from_file_location("entry_budget", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeEnc:
    """One token per character — lets the token axis be tested without tiktoken installed."""
    def encode(self, s):
        if "<|endoftext|>" in s:
            raise ValueError("special token")  # what tiktoken's encode() does
        return list(s)

    def encode_ordinary(self, s):
        return list(s)


def test_a_new_over_token_line_cannot_hide_behind_an_old_over_character_line():
    """In ONE sorted list the new over-TOKEN line 'replaced' the old over-CHARACTER one and passed."""
    eb = _load_hook()
    before = "x" * 500                       # over the 400-char cap
    after = "y" * 299                        # under 400 chars, but 299 tokens > a 100-token cap
    assert eb.long_new_lines(before, after, 400, 100, _FakeEnc()) == [(1, 299, "tokens")]


def test_hook_fails_open_on_a_malformed_payload(handover):
    proc = subprocess.run(["python3", str(HOOK), "--hook"], input=json.dumps([]),
                          capture_output=True, text=True, cwd=str(handover),
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(handover)))
    assert proc.returncode == ALLOW and "Traceback" not in proc.stderr


def test_a_relative_file_path_is_resolved_against_the_project_root(handover, tmp_path_factory):
    """With cwd != root, `before` used to be read as empty, so every OLD long line looked new."""
    long = "- (a) " + "x" * 900
    (handover / "HANDOVER.md").write_text("# HANDOVER\n\n" + long + "\n")
    elsewhere = tmp_path_factory.mktemp("cwd")
    payload = {"tool_input": {"file_path": "HANDOVER.md",
                              "content": "# HANDOVER\n\n" + long + "\n- (a) new short fact\n"}}
    proc = subprocess.run(["python3", str(HOOK), "--hook"], input=json.dumps(payload),
                          capture_output=True, text=True, cwd=str(elsewhere),
                          env=dict(os.environ, CLAUDE_PROJECT_DIR=str(handover)))
    assert proc.returncode == ALLOW, proc.stderr


# Post-release review of v0.8.37 (2026-09-26), each pinned.

def test_a_special_token_in_a_line_does_not_switch_the_gate_off():
    """tiktoken's encode() RAISES on <|endoftext|>; the fail-open wrapper then allowed everything."""
    eb = _load_hook()
    after = "short\n" + "<|endoftext|>" + "x" * 200 + "\n"
    assert eb.long_new_lines("short\n", after, 400, 100, _FakeEnc()) == [(2, 213, "tokens")]


def test_the_offender_named_is_the_line_that_changed():
    """Dominance is by rank: growing the SHORTER of two long lines used to name the untouched one."""
    eb = _load_hook()
    before = "a" * 900 + "\n" + "b" * 500 + "\n"
    after = "a" * 900 + "\n" + "b" * 950 + "\n"
    assert eb.long_new_lines(before, after, 400) == [(2, 950, "characters")]


def test_a_near_miss_cap_key_is_named_and_a_project_key_stays_silent(handover):
    (handover / ".claude").mkdir(exist_ok=True)
    (handover / ".claude" / "keel-caps").write_text("LESSON_KB=90\nMY_TOOL_LIMIT=3\n")
    eb = _load_hook()
    notes = eb.caps_notes(str(handover))
    assert len(notes) == 1 and "`LESSON_KB`" in notes[0] and "`LESSONS_KB`" in notes[0]


def test_a_token_cap_without_tiktoken_is_said_out_loud(handover, monkeypatch):
    (handover / ".claude").mkdir(exist_ok=True)
    (handover / ".claude" / "keel-caps").write_text("HANDOVER_LINE_TOKENS=120\n")
    eb = _load_hook()
    monkeypatch.setattr(eb, "_tokenizer", lambda: None)
    notes = eb.caps_notes(str(handover))
    assert len(notes) == 1 and "token axis is OFF" in notes[0]
    monkeypatch.setattr(eb, "_tokenizer", lambda: _FakeEnc())
    assert eb.caps_notes(str(handover)) == []


def test_an_undecodable_byte_in_keel_caps_does_not_silence_check(handover):
    """UnicodeDecodeError is a ValueError the reader did not catch; --check then printed nothing."""
    (handover / ".claude" / "keel-caps").write_bytes(b"LESSONS_ENTRY = 20  # r\xf6viewed\n")
    eb = _load_hook()
    assert eb.read_caps(str(handover)) == {"LESSONS_ENTRY": 20}
    assert eb.max_lines(str(handover), {"cap_key": "LESSONS_ENTRY", "default": 8}) == 20, \
        "one parser: spaces around '=' used to fall back to the default in the entry gate only"
