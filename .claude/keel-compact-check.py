#!/usr/bin/env python3
"""The MECHANICAL half of /keel-compact's freshness gate — ONE call, ONE verdict block.

WHY (measured on a live 5-agent project, 2026-09-08): the ritual's last three runs took 17 / 25 / 59
tool turns, and it runs exactly when the context is FULLEST — 59 turns x ~626k tokens is ~37M cache
reads for one ritual. The caps limit what gets WRITTEN, not how many turns the check costs. Every
item below used to be re-derived by hand, one tool call at a time; this script does them in one.

NOT A SECOND SOURCE OF TRUTH: caps are READ from `.claude/keel-caps` (defaults below only when a key
is absent — the same defaults as session-start-reground.sh, pinned equal by a test), per-line caps
come from `entry-budget.py`, the citation verdict from `citation-gate.py` itself. No new criterion
is defined here.

NOT THE HUMAN HALF: "is an agreement from this conversation still unwritten?" (rules §9.31) cannot
be measured, so the script does not pretend to — it PRINTS it as the one step left to you.

Usage:  python3 .claude/keel-compact-check.py
rc 0 = every mechanical gate passed · 1 = at least one RED · 2 = the instrument itself failed
(fail-closed: a check that cannot run never reports green).
"""
import datetime
import importlib.util
import os
import re
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
HERE = os.path.dirname(os.path.abspath(__file__))

# Defaults when `.claude/keel-caps` has no such key — MUST equal session-start-reground.sh
# (tests/unit/test_keel_compact_check.py pins it).
LINE_DEFAULTS = {"HANDOVER": 150, "LESSONS": 250, "TASKS": 100, "RULES": 400, "HANDOVER_BLOCKS": 3}
KB_DEFAULTS = {"HANDOVER_KB": 24, "LESSONS_KB": 40, "TASKS_KB": 16, "RULES_KB": 48,
               "CLAUDE_KB": 16, "CONTEXT_KB": 120}
FILES = (("CLAUDE.md", "CLAUDE"), ("rules.md", "RULES"), ("HANDOVER.md", "HANDOVER"),
         ("LESSONS.md", "LESSONS"), ("TASKS.md", "TASKS"))

OUT, RED = [], [0]


def say(s=""):
    OUT.append(s)


def gate(name, ok, detail):
    if not ok:
        RED[0] += 1
    say("  %s %-22s %s" % ("PASS" if ok else "RED ", name, detail))


def info(name, detail):
    say("  info %-22s %s" % (name, detail))


def load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def read(name):
    p = os.path.join(ROOT, name)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def kb_default(caps, key):
    """The KB cap for one file. An explicit `<KEY>_KB` wins. Without one, the default SCALES with a
    RAISED line cap, in the same proportion: a project whose owner chose LESSONS=1000 must not meet
    a second, hidden 40 KB limit (found in review against a live project). A line cap at or below
    its default leaves the KB default alone. Mirrors session-start-reground.sh — pinned by a test."""
    if key + "_KB" in caps:
        return caps[key + "_KB"]
    base = KB_DEFAULTS[key + "_KB"]
    lines, dflt = caps.get(key), LINE_DEFAULTS.get(key)
    if lines and dflt and lines > dflt:
        return -(-base * lines // dflt)
    return base


LINE_CHARS_DEFAULT = 400      # MUST equal entry-budget.py's (pinned by a test)


def read_caps(root):
    """{KEY: int} from `.claude/keel-caps`, parsed HERE — never imported from the hook module: a
    project that kept its own `entry-budget.py` through `/keel-update` would otherwise make this
    script an instrument fault on every run (found in review against a live project)."""
    out = {}
    try:
        with open(os.path.join(root, ".claude", "keel-caps"), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                k, sep, v = line.partition("=")
                # Leading digits, exactly like the bash reader (`50KB` -> 50, `abc` -> ignored).
                m = re.match(r"\s*(\d+)", v)
                if sep and m:
                    out[k.strip()] = int(m.group(1))
    except OSError:
        pass
    return out


def line_char_cap(caps, name, key):
    if key + "_LINE_CHARS" in caps:
        return caps[key + "_LINE_CHARS"]
    if name == "TASKS.md":      # the line cap never undercuts the board-item character budget
        return max(LINE_CHARS_DEFAULT, caps.get("TASKS_ENTRY_CHARS", 400))
    return LINE_CHARS_DEFAULT


def caps_section(caps):
    say("SIZE (caps from .claude/keel-caps; defaults where a key is absent)")
    total = 0
    for name, key in FILES:
        text = read(name)
        if text is None:
            continue
        lines = text.splitlines()
        size = len(text.encode("utf-8"))
        total += size
        line_cap = caps.get(key, LINE_DEFAULTS.get(key))
        kb_cap = kb_default(caps, key)
        char_cap = line_char_cap(caps, name, key)
        long = [(i, len(l)) for i, l in enumerate(lines, 1) if char_cap and len(l) > char_cap]
        parts = ["%d lines%s" % (len(lines), "/%d" % line_cap if line_cap else ""),
                 "%.1f/%d KB" % (size / 1024, kb_cap)]
        ok = (not line_cap or len(lines) <= line_cap) and size <= kb_cap * 1024
        gate(name, ok, " · ".join(parts))
        if long:
            # INFO, not RED: the write gate lets an EXISTING long line stay (it only blocks new or
            # longer ones), so a RED here would be a permanently-red check on inherited text. A
            # pathological line still turns the KB gate above RED.
            i, n = max(long, key=lambda x: x[1])
            info(name + " long lines", "%d over %d chars, longest line %d = %d chars — split into "
                 "one fact each when you next touch them" % (len(long), char_cap, i, n))
    cap_all = caps["CONTEXT_KB"] if "CONTEXT_KB" in caps else max(
        KB_DEFAULTS["CONTEXT_KB"], sum(kb_default(caps, k) for _, k in FILES) * 5 // 6)
    gate("always-loaded total", total <= cap_all * 1024, "%.1f/%d KB" % (total / 1024, cap_all))


def handover_section(caps, today):
    say("HANDOVER")
    text = read("HANDOVER.md")
    if text is None:
        info("HANDOVER.md", "absent — not a Keel project, nothing to check")
        return
    heads = re.findall(r"^### (\d{4}-\d\d-\d\d)", text, re.M)
    top = re.search(r"^### \d{4}-\d\d-\d\d.*$", text, re.M)
    maxb = caps.get("HANDOVER_BLOCKS", LINE_DEFAULTS["HANDOVER_BLOCKS"])
    gate("session blocks", len(heads) <= maxb, "%d/%d dated blocks" % (len(heads), maxb))
    # A block may span days ("### 2026-09-24 → 2026-09-25 — ..."): today anywhere in the heading counts.
    gate("top block date", bool(top) and today in top.group(0),
         "top block heading carries %s" % today if top and today in top.group(0)
         else "top block is %s, today is %s" % (heads[0] if heads else "missing", today))
    dirty = git("status", "--porcelain", "--", "HANDOVER.md")
    ct = git("log", "-1", "--format=%ct", "--", "HANDOVER.md")
    fresh_commit = bool(ct) and (datetime.datetime.now().timestamp() - int(ct)) <= 1800
    # A HEURISTIC (touched recently), not proof of THIS session — same-day is not same-session, and
    # that judgment stays in the HUMAN section below.
    gate("HANDOVER touched", bool(dirty) or fresh_commit,
         "modified in the tree" if dirty else ("committed <=30 min ago" if fresh_commit
                                               else "not modified, last commit older than 30 min"))
    log = read(".claude/ritual-log") or ""
    def worker(tag):
        p = os.path.join(ROOT, ".claude", "agents", "team-%s.md" % tag)
        try:
            with open(p, encoding="utf-8") as fh:
                return any(l.startswith("Role: worker") for l in fh)
        except OSError:
            return False
    # /keel-compact is the orchestrator's / a solo session's ritual, so only markers that are
    # settled in HANDOVER count here; a worker's tagged marker is settled in its own board.
    sd = []
    for l in log.splitlines():
        if " STALE-DISK" not in l:
            continue
        m = re.search(r" STALE-DISK @([^:]+):", l)
        if m and worker(m.group(1)):
            continue
        sd.append(l[:19])
    if sd:
        try:
            sd_s = datetime.datetime.strptime(sd[-1], "%Y-%m-%d %H:%M:%S").timestamp()
        except ValueError:          # an unreadable marker is not a settled one — fail closed
            sd_s = float("inf")
        h_s = os.path.getmtime(os.path.join(ROOT, "HANDOVER.md"))
        gate("STALE-DISK debt", sd_s <= h_s,
             "settled (HANDOVER newer than %s)" % sd[-1] if sd_s <= h_s
             else "compaction at %s crossed a dirty tree before HANDOVER was written" % sd[-1])
    else:
        gate("STALE-DISK debt", True, "none recorded")


def board_section():
    say("BOARD")
    text = read("TASKS.md")
    if text is None:
        info("TASKS.md", "absent")
        return

    def section(title):
        m = re.search(r"^## %s\b.*?(?=^## |\Z)" % title, text, re.S | re.M)
        return m.group(0) if m else ""
    # On a team board `## Now` holds one `### <lane>` per worker: the 3-5 limit is PER LANE there.
    lanes = re.split(r"^### +(.+)$", section("Now"), flags=re.M)
    groups = [("", lanes[0])] + list(zip(lanes[1::2], lanes[2::2]))
    counts = [(lane.strip() or "(board)", len(re.findall(r"^\s*- \[ \]", body, re.M)))
              for lane, body in groups]
    counts = [c for c in counts if c[1] or c[0] == "(board)"]
    over = [c for c in counts if c[1] > 5]
    gate("## Now open items", not over,
         " · ".join("%s %d" % c for c in counts) + " (max 3-5 per lane, rules §9.32)")
    review = [l for l in section("Review").splitlines() if re.match(r"^\s*- \[[ x]\]", l)]
    # The SessionStart hook's criterion, not a new one: an `evidence:` link, and EVERY
    # `reports/…md` path on the line exists (one existing path must not vouch for a missing one).
    missing = []
    for l in review:
        paths = re.findall(r"reports/[A-Za-z0-9_./@-]+\.md", l)
        if "evidence:" not in l or not paths or not all(os.path.exists(os.path.join(ROOT, p))
                                                        for p in paths):
            missing.append(l.strip()[:70])
    gate("## Review evidence", not missing,
         "%d item(s), all with an existing note" % len(review) if not missing
         else "%d without an existing note file: %s" % (len(missing), missing[0]))


def citation_section():
    say("CITATIONS")
    if git("rev-parse", "--is-inside-work-tree") != "true":
        info("ghost citations", "not a git repo — NOT measured (HEAD is the reference)")
        return
    path = os.path.join(HERE, "hooks", "citation-gate.py")
    report = None
    if os.path.isfile(path):
        # A gate that is PRESENT but crashes on load propagates -> rc=2 (fail closed). Only an absent
        # file, or a project's own gate without report(), is "not measured" — never a silent pass.
        try:
            report = getattr(load("citation_gate", path), "report", None)
        except SystemExit as exc:   # a script-style gate exits at import: never let it set OUR rc
            raise RuntimeError("citation-gate.py exited on import (%s) — not a library" % exc.code)
    if report is None:
        info("ghost citations", "NOT measured — no kit citation-gate.py with report() here "
             "(a project may run its own gate; run it by hand)")
        return
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = report(ROOT)
    if rc == 2:
        raise RuntimeError("citation-gate reports itself BROKEN: " + buf.getvalue().strip()[:200])
    first = next((l for l in buf.getvalue().splitlines() if l.strip()), "")
    gate("ghost citations", rc == 0, "clean" if rc == 0 else first[:150])


def plan_and_push_section(today):
    say("CONTEXT")
    plan = read("PLAN.md")
    if plan is not None:
        m = re.search(r"_Current focus[^\n]*", plan)
        d = re.search(r"\d{4}-\d\d-\d\d", m.group(0)) if m else None
        info("PLAN current focus", ("dated %s" % d.group(0)) if d else "no dated _Current focus_ line")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if ahead is None:
        info("push boundary", "no upstream configured")
    elif ahead == "0":
        info("push boundary", "in sync with upstream — nothing to push")
    else:
        info("push boundary", "%s commit(s) ahead of upstream — offer ONE batched push" % ahead)
    agents = os.path.join(ROOT, ".claude", "agents")
    if os.path.isdir(agents):
        ch = [(f, os.path.getsize(os.path.join(agents, f))) for f in sorted(os.listdir(agents))
              if f.startswith("team-") and f.endswith(".md")]
        if ch:
            big = max(ch, key=lambda x: x[1])
            info("charters", "%d, %.1f KB total, largest %s %.1f KB — a charter is read by its "
                 "session every start; it grows like LESSONS if nothing drains it"
                 % (len(ch), sum(s for _, s in ch) / 1024, big[0], big[1] / 1024))


def main():
    today = datetime.date.today().isoformat()
    try:
        caps = read_caps(ROOT)
        caps_section(caps)
        handover_section(caps, today)
        board_section()
        citation_section()
        plan_and_push_section(today)
    except (Exception, SystemExit) as exc:   # fail-CLOSED: a check that could not run is not a pass
        print("\n".join(OUT))
        print("INSTRUMENT FAULT (rc=2): %s — fall back to the checklist in /keel-compact by hand." % exc)
        return 2
    say("HUMAN (not measurable — yours)")
    say("  todo §9.31 sweep: is any agreement, gotcha or failed approach from THIS conversation")
    say("       still unwritten? Write it to LESSONS/HANDOVER before compacting.")
    say("  todo Does the top HANDOVER block describe THIS session? Same-day is not same-session —")
    say("       another session's block from today is still stale for you (add or update your own).")
    say("VERDICT: %s" % ("PASS — mechanical gates green" if not RED[0]
                         else "%d RED — fix before /compact" % RED[0]))
    print("\n".join(OUT))
    return 1 if RED[0] else 0


if __name__ == "__main__":
    sys.exit(main())
