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


def test_gitignored_path_is_a_third_class_not_a_ghost(repo):
    """A doc may legitimately tell the reader to create a file nobody commits."""
    (repo / ".gitignore").write_text("config/secret.yaml\n")
    (repo / "config").mkdir()
    (repo / "config" / "secret.yaml").write_text("local\n")
    (repo / "docs" / "rec.md").write_text("create `config/secret.yaml`\n")
    sh("git", "add", ".gitignore", cwd=repo)
    sh("git", "commit", "-aqm", "ignore", cwd=repo)
    rc, out = run(repo)
    assert rc == 0
    assert "BY DESIGN" in out and "config/secret.yaml" in out
    assert "NOT in HEAD" not in out


def test_foreign_paths_tail_is_not_read_as_a_local_path(repo):
    """The lookbehind: without it, a longer foreign path's tail matches — inventing a ghost when
    HEAD lacks it and, worse, declaring a citation resolved when HEAD happens to have it."""
    (repo / "docs" / "rec.md").write_text(
        "traceback from /usr/lib/python3.10/site-packages/reports/note.md\n")
    sh("git", "commit", "-aqm", "foreign", cwd=repo)
    rc, out = run(repo)
    assert rc == 0 and "site-packages" not in out


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
