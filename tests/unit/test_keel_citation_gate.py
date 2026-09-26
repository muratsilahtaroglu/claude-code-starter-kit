"""Regression matrix for `.claude/hooks/citation-gate.py` — the provenance gate.

WHY THIS FILE EXISTS. `git commit -- <pathspec>` does not pick up an untracked file and does not
error, so a permanent record can cite an artefact that never landed: file status looks right,
provenance is gone. Measured on a live project where the class repeated three times in ONE day
under a written rule (§6.18), which is why it became a gate (§10.38). Keel already assumes
citations resolve — §3.10 keeps a probe alive because a record NAMES it, §10.40 calls reports the
artefacts others cite, `/keel-distill` rewrites citations when it sweeps into `done/`.

The cases below pin the parts the source tool learned the hard way: the lookbehind, `..`
normalisation, the `done/` variant, gitignored paths as a THIRD class rather than a ghost, and the
positive control that makes a broken tool say so instead of reporting "clean".

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / ".claude" / "hooks" / "citation-gate.py"


def sh(*args, cwd):
    subprocess.run(args, cwd=str(cwd), check=True, capture_output=True)


def run(root):
    p = subprocess.run(["python3", str(GATE)], cwd=str(root), capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=str(root)))
    return p.returncode, p.stdout + p.stderr


@pytest.fixture
def repo(tmp_path):
    """A committed repo with one report and one record citing it — the healthy baseline."""
    (tmp_path / "reports").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "reports" / "note.md").write_text("evidence\n")
    (tmp_path / "docs" / "rec.md").write_text("see `reports/note.md`\n")
    sh("git", "init", "-q", ".", cwd=tmp_path)
    sh("git", "config", "user.name", "t", cwd=tmp_path)
    sh("git", "config", "user.email", "t@e.com", cwd=tmp_path)
    sh("git", "add", "-A", cwd=tmp_path)
    sh("git", "commit", "-qm", "base", cwd=tmp_path)
    return tmp_path


def test_committed_citation_is_clean(repo):
    rc, out = run(repo)
    assert rc == 0 and "NOT in HEAD" not in out


def test_cited_but_never_committed_is_a_ghost(repo):
    """The whole reason the gate exists: the note is on disk, the record points at it, HEAD has
    neither — because `git commit -- <path>` skipped it silently."""
    (repo / "reports" / "ghost.md").write_text("never staged\n")
    (repo / "docs" / "rec.md").write_text("see `reports/ghost.md`\n")
    rc, out = run(repo)
    assert rc == 1
    assert "reports/ghost.md" in out and "NOT in HEAD" in out
    assert "docs/rec.md" in out, "a finding must name WHO cites it, or it cannot be fixed"


def test_swept_report_still_resolves_through_its_done_variant(repo):
    """/keel-distill moves a closed task's files into `done/`, and some citing files are FROZEN
    (docs/handover-archive.md, §1.4) so their paths can never be rewritten."""
    (repo / "reports" / "done").mkdir()
    sh("git", "mv", "reports/note.md", "reports/done/note.md", cwd=repo)
    sh("git", "commit", "-qm", "sweep", cwd=repo)
    rc, out = run(repo)
    assert rc == 0 and "NOT in HEAD" not in out


def test_dotdot_is_normalised_before_git_is_asked(repo):
    """os.path.exists('docs/../reports/note.md') is True but git rejects `..` in a tree path —
    without normalisation every such citation is an unfixable permanent red."""
    (repo / "docs" / "rec.md").write_text("see `docs/../reports/note.md`\n")
    sh("git", "commit", "-aqm", "cite via ..", cwd=repo)
    rc, out = run(repo)
    assert rc == 0, out


def _with_ignored(repo):
    """A doc that legitimately tells the reader to create a file nobody commits."""
    (repo / ".gitignore").write_text("config/secret.yaml\n")
    (repo / "config").mkdir()
    (repo / "config" / "secret.yaml").write_text("local\n")
    sh("git", "add", ".gitignore", cwd=repo)


def test_gitignored_path_is_never_a_ghost_and_is_silent_on_its_own(repo):
    """The third class exists so an ignored path is not silently DROPPED — but announcing it when
    there is nothing else to say is noise on every run forever, which is the failure this gate's own
    docstring names. So: never a ghost, and quiet when it is the only thing to report."""
    _with_ignored(repo)
    (repo / "docs" / "rec.md").write_text("create `config/secret.yaml`\n")
    sh("git", "commit", "-aqm", "ignore", cwd=repo)
    rc, out = run(repo)
    assert rc == 0
    assert "NOT in HEAD" not in out
    assert out.strip() == "", "an ignored-by-design path alone is not news"


def test_gitignored_paths_ride_along_as_context_when_there_IS_a_finding(repo):
    """Alongside a real ghost they are printed — that is what keeps them from being dropped."""
    _with_ignored(repo)
    (repo / "reports" / "ghost.md").write_text("never staged\n")
    (repo / "docs" / "rec.md").write_text(
        "see `reports/ghost.md`, and create `config/secret.yaml`\n")
    sh("git", "commit", "-aqm", "ignore+ghost", cwd=repo)
    rc, out = run(repo)
    assert rc == 1
    assert "BY DESIGN" in out and "config/secret.yaml" in out


def test_a_foreign_paths_tail_is_not_read_as_a_repo_path(repo):
    """The lookbehind, pinned by the case that actually discriminates. An earlier version of this
    test used `/usr/lib/.../site-packages/reports/note.md`, which `repo_roots()` rejects on its own:
    deleting the lookbehind left all nine cases green (mutation-tested 2026-09-03 — a test named for
    a guard that cannot detect its absence). The real exposure is a LEADING separator: `~/reports/…`
    and `/reports/…` are a home path and a container path, and without the lookbehind both are read
    as this repo's `reports/…`, inventing a ghost or falsely resolving a citation."""
    (repo / "reports" / "ghost.md").write_text("exists on disk, never committed\n")
    (repo / "docs" / "rec.md").write_text(
        "my copy is at ~/reports/ghost.md and the container mounts /reports/ghost.md\n")
    sh("git", "commit", "-aqm", "foreign", cwd=repo)
    rc, out = run(repo)
    assert rc == 0, "neither is a repo path, so neither is a ghost"
    assert "reports/ghost.md" not in out


def test_the_same_name_without_a_leading_separator_IS_a_repo_path(repo):
    """The other half of the pair — otherwise the guard above could pass by matching nothing at all."""
    (repo / "reports" / "ghost.md").write_text("exists on disk, never committed\n")
    (repo / "docs" / "rec.md").write_text("see `reports/ghost.md`\n")
    sh("git", "commit", "-aqm", "local", cwd=repo)
    rc, out = run(repo)
    assert rc == 1 and "reports/ghost.md" in out


def test_unresolvable_path_is_counted_not_dropped(repo):
    """Silence about what the tool could not resolve is how a checker lies about its coverage."""
    (repo / "docs" / "rec.md").write_text("see `reports/nowhere.md`\n")
    sh("git", "commit", "-aqm", "dangle", cwd=repo)
    rc, out = run(repo)
    assert "found NOWHERE" in out and "reports/nowhere.md" in out


def test_allowlist_silences_a_deliberate_absence(repo):
    (repo / "reports" / "ghost.md").write_text("x\n")
    (repo / "docs" / "rec.md").write_text("see `reports/ghost.md`\n")
    (repo / ".claude").mkdir()
    (repo / ".claude" / "citation-allow").write_text(
        "reports/ghost.md   # deliberately not committed: raw PII extract\n")
    rc, _ = run(repo)
    assert rc == 0


def test_non_repo_directory_is_a_silent_noop(tmp_path):
    rc, out = run(tmp_path)
    assert rc == 0 and out == ""


# --------------------------------------------------------------------------
# 2026-09-06 — two classes ported from a live project's gate (`citation_head_check.py`)
# --------------------------------------------------------------------------

def test_recorded_absent_marker_keeps_a_measured_absence_out_of_the_ghost_list(repo):
    """A record that MEASURED a file is gone cites a path that must not exist. Without the marker the
    gate punishes the most valuable record type; with it the path is counted, never a ghost. The
    marker is per LINE — a second, unmarked citation of a real ghost on another line still fires."""
    # The probe copy existed during the run and was deleted afterwards — so it is NOT on disk now.
    (repo / "reports" / "gone.md").write_text("probe copy, deleted after the run\n")
    (repo / "reports" / "gone.md").unlink()
    (repo / "docs" / "rec.md").write_text(
        "the probe `reports/gone.md` was removed after the run (RECORDED-ABSENT)\n")
    rc, out = run(repo)
    assert rc == 0 and "NOT in HEAD" not in out
    # Not an exemption: beside a REAL ghost the count of marked paths is printed, so the marker
    # cannot become the quiet way to make a ghost disappear.
    (repo / "reports" / "ghost.md").write_text("never staged\n")
    (repo / "docs" / "rec.md").write_text(
        "the probe `reports/gone.md` was removed (RECORDED-ABSENT)\nsee `reports/ghost.md`\n")
    rc, out = run(repo)
    assert rc == 1 and "reports/ghost.md" in out
    assert "RECORDED-ABSENT" in out and "reports/gone.md" in out


def test_recorded_absent_marker_does_not_cover_a_file_that_is_still_on_disk(repo):
    """Found by the pre-delivery reviewer: a marker on the ONLY ghost made the gate silent. The marker
    means 'gone'; a marked path that still exists on disk is a ghost wearing the marker."""
    (repo / "reports" / "still_here.md").write_text("never staged, never deleted\n")
    (repo / "docs" / "rec.md").write_text("see `reports/still_here.md` (RECORDED-ABSENT)\n")
    rc, out = run(repo)
    assert rc == 1 and "reports/still_here.md" in out and "NOT in HEAD" in out


def test_line_anchor_into_a_rotating_board_is_warned_but_does_not_fail(repo):
    """`board.md:NNN` is right the day it is written and stale by the next round — and it pins the
    board against rotation because the lane may not rewrite the surface carrying it (a lane measured
    3 of its 4 anchors on other surfaces, 2026-09-06). A warning class of its own; exit stays 0."""
    (repo / "docs" / "rec.md").write_text(
        "see `reports/note.md` and reports/team/fe/board.md:1589 and TASKS.md:334\n")
    rc, out = run(repo)
    assert rc == 0
    assert "line-number anchor" in out
    assert "reports/team/fe/board.md:1589" in out and "TASKS.md:334" in out
    assert "docs/rec.md" in out, "the citing file must be named or nobody can fix the anchor"


def test_a_long_extension_is_not_truncated_into_a_ghost_path():
    """`.claude/keel-caps.example` was read as `.claude/keel-caps.exampl` and reported NOWHERE."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cg", REPO / ".claude" / "hooks" / "citation-gate.py")
    cg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cg)
    assert cg.PAT.findall("see .claude/keel-caps.example and docs/a.md") == ["docs/a.md"]
