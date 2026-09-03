"""Regression matrix for `.claude/claude-launch-wrapper.sh` — the resume-keeps-its-name launcher.

WHY THIS FILE EXISTS. Measured 2026-09-03 on a live 5-agent team: `/rename` lands in the session
TRANSCRIPT (an `agent-name` record), but a process started with `--resume <sid>` does not carry it
into the per-process messaging record — it comes up `nameSource=derived` as `<repo>-xx`, so every
IDE reopen or Remote-SSH reconnect silently un-names the agent and peers lose its address until a
human retypes `/rename`. `claude --name` at launch DOES set it: VERIFIED end-to-end 2026-09-03 —
with the wrapper installed behind `claudeCode.claudeProcessWrapper`, three reopened IDE tabs came
up `nameSource=user` under their own agent names (the IDE resumes with the `--resume=<sid>` form).
The wrapper injects that flag from the kit's identity map (or the transcript's own record); this
matrix pins the routing, the opt-in trace that made the above measurable at all (the `exec` is
transparent — a wrapped launch and a direct one have identical /proc cmdlines), and, above all,
the FAIL-OPEN contract — a launcher that can break a session start is worse than no launcher.

KIT-OWNED FILE (`/keel-update` TOOLING exception, `tests/unit/test_keel_*.py`).
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WRAPPER = REPO / ".claude" / "claude-launch-wrapper.sh"

SID = "7d057b03-a749-4ede-8d2c-cb07a73f2225"


@pytest.fixture
def world(tmp_path):
    """A fake `claude` that dumps its argv, a project dir, and an isolated CLAUDE_CONFIG_DIR."""
    fake = tmp_path / "bin" / "claude"
    fake.parent.mkdir()
    fake.write_text("#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > \"$FAKE_OUT\"\n")
    fake.chmod(0o755)
    project = tmp_path / "proj"
    (project / ".claude").mkdir(parents=True)
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    return {"fake": fake, "project": project, "cfg": cfg, "out": tmp_path / "argv.txt"}


def launch(world, *args, cwd=None):
    env = dict(os.environ, KEEL_CLAUDE_BIN=str(world["fake"]), FAKE_OUT=str(world["out"]),
               CLAUDE_CONFIG_DIR=str(world["cfg"]))
    proc = subprocess.run(["bash", str(WRAPPER), *args], cwd=str(cwd or world["project"]),
                          env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == "", "the wrapper must never write to stdout — the IDE speaks stream-json on it"
    return world["out"].read_text().splitlines()


def transcript_with_name(world, name):
    proj = "".join(c if c.isalnum() else "-" for c in str(world["project"]))
    d = world["cfg"] / "projects" / proj
    d.mkdir(parents=True)
    rec = {"type": "agent-name", "agentName": name, "sessionId": SID}
    # real transcripts are compact JSON (no spaces) — write the real shape, not a pretty one
    (d / f"{SID}.jsonl").write_text('{"type":"user","message":"x"}\n'
                                    + json.dumps(rec, separators=(",", ":")) + "\n")


# --------------------------------------------------------------------------
# Routing
# --------------------------------------------------------------------------

def test_identity_map_names_a_resumed_session(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-09-03\n")
    argv = launch(world, f"--resume={SID}", "--output-format", "stream-json")
    assert argv[:2] == ["--name", "frontend"]
    assert argv[2:] == [f"--resume={SID}", "--output-format", "stream-json"], "original args intact"


def test_separate_arg_resume_form(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} provider 2026-09-03\n")
    argv = launch(world, "--resume", SID)
    assert argv == ["--name", "provider", "--resume", SID]


def test_transcript_record_is_the_fallback(world):
    """No kit map (a non-team project): the user's own /rename still comes back."""
    transcript_with_name(world, "my-refactor")
    argv = launch(world, f"--resume={SID}")
    assert argv[:2] == ["--name", "my-refactor"]


def test_identity_map_wins_over_transcript(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-09-03\n")
    transcript_with_name(world, "stale-old-name")
    assert launch(world, f"--resume={SID}")[:2] == ["--name", "frontend"]


# --------------------------------------------------------------------------
# Pass-through — the launcher must be invisible whenever it has nothing to add
# --------------------------------------------------------------------------

def test_new_session_passes_through_untouched(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-09-03\n")
    argv = launch(world, "--output-format", "stream-json", "--verbose")
    assert argv == ["--output-format", "stream-json", "--verbose"]


def test_explicit_name_is_never_overridden(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} frontend 2026-09-03\n")
    argv = launch(world, "--name", "chosen", f"--resume={SID}")
    assert argv == ["--name", "chosen", f"--resume={SID}"]


def test_unknown_sid_passes_through(world):
    (world["project"] / ".claude" / "agent-team-sessions").write_text("other-sid orchestrator 2026-09-03\n")
    argv = launch(world, f"--resume={SID}")
    assert argv == [f"--resume={SID}"]


def test_unsafe_name_in_map_is_not_injected(world):
    """A corrupted map line must not become a shell-shaped argument."""
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} bad;name 2026-09-03\n")
    assert launch(world, f"--resume={SID}") == [f"--resume={SID}"]


def test_fails_open_when_config_dir_is_missing(world):
    """Nothing readable anywhere → the original launch proceeds, no error."""
    world["cfg"] = world["cfg"] / "does-not-exist"
    assert launch(world, f"--resume={SID}") == [f"--resume={SID}"]


def test_wrapper_is_executable_and_bash(tmp_path):
    assert os.access(WRAPPER, os.X_OK), "install step copies it as-is; it must ship executable"
    assert WRAPPER.read_text().startswith("#!/usr/bin/env bash")


# --------------------------------------------------------------------------
# the opt-in trace — the only way to prove the IDE setting actually took effect
# --------------------------------------------------------------------------

def test_trace_is_written_only_when_the_owner_created_the_file(world):
    """`touch ~/.claude/keel-launch-wrapper.log` arms it; both branches are recorded."""
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} review 2026-09-03\n")
    log = world["cfg"] / "keel-launch-wrapper.log"
    log.write_text("")
    launch(world, f"--resume={SID}")
    launch(world, "--continue")
    lines = log.read_text().splitlines()
    assert len(lines) == 2
    assert f"named --name=review sid={SID}" in lines[0]
    assert "passthrough sid=none" in lines[1]


def test_trace_file_is_never_created_by_the_wrapper(world):
    """Silence is the default: an unarmed machine gets no new file and no stray output."""
    (world["project"] / ".claude" / "agent-team-sessions").write_text(f"{SID} review 2026-09-03\n")
    argv = launch(world, f"--resume={SID}")   # launch() already asserts stdout stayed empty
    assert not (world["cfg"] / "keel-launch-wrapper.log").exists()
    assert argv[:2] == ["--name", "review"], "an unarmed trace must not change the launch"
