#!/usr/bin/env python3
"""LESSONS.md per-ENTRY line budget — the anti-bloat valve that raising the file cap cannot be.

WHY (measured on a live project, alice_v2 2026-08-25, backported with its blind spot FIXED):
LESSONS was distilled to 450 lines and stood at 1039 five days later. Entry COUNT grew 1.5x but
LINES grew 2.5x — the overflow came from entries GETTING LONGER (avg 6.3 -> 10.2 lines), not from
new lessons. The owner's own words: "I keep raising the cap and it is never enough" — raising the
cap makes room for the tendency, and the tendency fills the room. So the limit moved from the FILE
cap to the WRITE moment (rules §10.38: enforced beats written).

CONTRACT: one LESSONS entry is at most MAX_LINES lines (default 8; override with a
`LESSONS_ENTRY=<n>` line in `.claude/keel-caps`) and has the shape
    RULE (1 sentence) · MECHANISM (1-2 sentences) · CHECK (how it is verified) · permanent-record path
Case narrative, number tables and round-by-round story go to a report/docs — LESSONS is read IN
FULL every session; a report only when needed.

THE BLIND SPOT THIS VERSION CLOSES: the original checked only the WRITTEN FRAGMENT, so an Edit that
folded new material INTO an existing entry (no dated first line in new_string) passed unseen — and
"fold it into an existing entry" was exactly the habit the cap pressure produced (its backlog
counter rose 41 -> 43 in three days). This version SIMULATES the post-edit file: it applies the
replacement to the on-disk content and blocks when the edit makes any entry newly oversized or an
oversized entry LONGER. Shrinking or restructuring an oversized entry always passes.

Registrations: PreToolUse (Write|Edit; exit 2 = block, fail-open on anything unexpected) +
SessionStart --check (advisory: prints only when the standing backlog GREW — a gate that is always
red trains its operator to walk past it; the measure is monotone descent, not zero).
Baseline: `.claude/lessons-backlog` (git-tracked so raises are visible in review). It auto-lowers;
it is never auto-raised — a grown count only warns, pointing at the entries to split.
"""
import json
import os
import re
import sys

DEFAULT_MAX = 8
ENTRY_RE = re.compile(r"^- 20\d\d-\d\d-\d\d")
# Index lines and header/doctrine blocks are not entries (they carry no leading date).
BASELINE = ".claude/lessons-backlog"


def max_lines(root):
    try:
        with open(os.path.join(root, ".claude", "keel-caps"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("LESSONS_ENTRY="):
                    return int(line.split("=", 1)[1].split("#")[0].strip())
    except (OSError, ValueError):
        pass
    return DEFAULT_MAX


def entries(text):
    """[(first_line, n_lines)] for every dated entry in the text."""
    out = []
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if ENTRY_RE.match(line):
            if start is not None:
                out.append((lines[start], i - start))
            start = i
        elif line.startswith("## ") and start is not None:
            out.append((lines[start], i - start))
            start = None
    if start is not None:
        out.append((lines[start], len(lines) - start))
    return out


def oversized(text, cap):
    return [(head[:100], n) for head, n in entries(text) if n > cap]


def _msg(bad, cap):
    parts = ["LESSONS entry budget (max %d lines) EXCEEDED:" % cap]
    for head, n in bad:
        parts.append("  %d lines — %s" % (n, head))
    parts.append("")
    parts.append("Entry shape: RULE · MECHANISM · CHECK · permanent-record path. Case narrative")
    parts.append("and number tables go to a report or docs/ — LESSONS is read IN FULL every")
    parts.append("session. Raising the file cap is not the valve; splitting the entry is.")
    return "\n".join(parts)


def check(root):
    """SessionStart advisory: report only when the oversized-entry count GREW past the recorded
    baseline; auto-lower the baseline when it shrank. Never blocks, always exits 0."""
    path = os.path.join(root, "LESSONS.md")
    if not os.path.exists(path):
        return 0
    cap = max_lines(root)
    with open(path, encoding="utf-8") as fh:
        bad = oversized(fh.read(), cap)
    n = len(bad)
    bp = os.path.join(root, BASELINE)
    prev = None
    if os.path.exists(bp):
        try:
            with open(bp, encoding="utf-8") as fh:
                prev = int((fh.read().split("#")[0] or "0").strip())
        except (OSError, ValueError):
            prev = None
    if prev is None or n < prev:
        try:
            with open(bp, "w", encoding="utf-8") as fh:
                fh.write("%d  # entries over the LESSONS per-entry budget; this number only goes"
                         " DOWN (auto-lowered; a raise means split the new oversized entries)\n" % n)
        except OSError:
            pass
        if prev is not None:
            print("[keel] LESSONS entry backlog shrank: %d -> %d (budget %d lines/entry)."
                  % (prev, n, cap))
        return 0
    if n > prev:
        print("[keel] LESSONS entry backlog GREW: %d -> %d entries over the %d-line budget — the"
              " newest oversized entries should be split (narrative -> report/docs, entry keeps"
              " RULE·MECHANISM·CHECK·path). The per-entry budget exists because raising the file"
              " cap only makes room for the tendency." % (prev, n, cap))
    return 0


def hook():
    """PreToolUse gate for Write|Edit on LESSONS.md. FAIL-OPEN on anything unexpected."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    ti = payload.get("tool_input") or {}
    fp = ti.get("file_path") or ""
    if os.path.basename(fp) != "LESSONS.md":
        return 0
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cap = max_lines(root)
    try:
        with open(fp, encoding="utf-8") as fh:
            before = fh.read()
    except OSError:
        before = ""

    content = ti.get("content")
    if content is not None:                      # Write: full replacement
        after = content
    else:                                        # Edit: simulate the post-edit file
        old = ti.get("old_string") or ""
        new = ti.get("new_string") or ""
        if not old or old not in before:
            return 0                             # unmatched edit will fail anyway — not our call
        after = before.replace(old, new, len(before.split(old)) - 1
                               if ti.get("replace_all") else 1)

    grew = []
    before_sizes = {}
    for head, n in entries(before):
        key = head[:100]
        before_sizes[key] = max(n, before_sizes.get(key, 0))
    for head, n in oversized(after, cap):
        prev_n = before_sizes.get(head)
        if prev_n is None or n > prev_n:         # newly oversized, or an oversized entry grew
            grew.append((head, n))
    if not grew:
        return 0                                 # shrinking/restructuring an oversized entry passes
    sys.stderr.write(_msg(grew, cap) + "\n")
    return 2


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "--check"
    if arg == "--hook":
        return hook()
    return check(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


if __name__ == "__main__":
    sys.exit(main())
