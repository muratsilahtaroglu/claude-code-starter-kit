#!/usr/bin/env python3
"""Per-ENTRY line budget for the always-imported memory files — the valve a file cap cannot be.

GUARDS TWO FILES, one mechanism (rules §10.39 — fix the class, not the instance):
  LESSONS.md  entry = a dated `- 20xx-xx-xx` line and its continuation  (LESSONS_ENTRY, default 8)
  TASKS.md    entry = a `- [ ]`/`- [x]` board item and its continuation (TASKS_ENTRY, default 4)

WHY (measured on a live project, alice_v2 2026-08-25, backported with its blind spot FIXED):
LESSONS was distilled to 450 lines and stood at 1039 five days later. Entry COUNT grew 1.5x but
LINES grew 2.5x — the overflow came from entries GETTING LONGER (avg 6.3 -> 10.2 lines), not from
new lessons. The owner's own words: "I keep raising the cap and it is never enough" — raising the
cap makes room for the tendency, and the tendency fills the room. So the limit moved from the FILE
cap to the WRITE moment (rules §10.38: enforced beats written).

CONTRACT: an entry fits its budget (override per file with a `<KEY>=<n>` line in
`.claude/keel-caps`) and keeps its shape:
    LESSONS — RULE (1 sentence) · MECHANISM (1-2) · CHECK (how verified) · permanent-record path
    TASKS   — id · @owner · due: · done-when · evidence path (rules §10.40 "TASKS stays LEAN")
Case narrative, number tables and round-by-round story go to a report/docs; the SPEC and the
solution note carry a task's detail. Both files are read IN FULL every session, by every session —
on an agent team that is the same prose paid five or six times a day.

WHY TASKS TOO (measured on the same project, 2026-09-03): its `## Review` section held 12 items in
211 lines — ~18 lines per board item, where the rule says a line. The board had become the place
where solution notes were written, and it is @-imported in full by every lane.

THE BLIND SPOT THIS VERSION CLOSES: the original checked only the WRITTEN FRAGMENT, so an Edit that
folded new material INTO an existing entry (no dated first line in new_string) passed unseen — and
"fold it into an existing entry" was exactly the habit the cap pressure produced (its backlog
counter rose 41 -> 43 in three days). This version SIMULATES the post-edit file: it applies the
replacement to the on-disk content and blocks when the edit makes any entry newly oversized or an
oversized entry LONGER. Shrinking or restructuring an oversized entry always passes.

THE SECOND BLIND SPOT — LINE LENGTH (measured on the same project, 2026-09-24/25): every cap above
counts LINES or ENTRIES, and none of them sees how LONG a line is. HANDOVER sat at 146/150 lines —
green — while it had grown to 244 KB, because ONE line held 135 KB; auto-compact then fired three
times in five minutes. So every ALWAYS-LOADED file (CLAUDE.md · rules.md · HANDOVER.md · LESSONS.md
· TASKS.md, at the project root) also carries a per-LINE character cap (`<FILE>_LINE_CHARS`,
default 400): a write that ADDS a line over the cap is blocked; a line already in the file verbatim
never is (monotone descent again — cleanup must never be punished). Characters, not bytes, so a
Turkish or emoji line is not penalised twice. Tokens are the real cost, but counting them needs a
tokenizer: when `tiktoken` is importable, an optional `<FILE>_LINE_TOKENS` key adds a token axis
(approximate — OpenAI's cl100k, not Claude's tokenizer); without it that axis is skipped, never
guessed from a made-up ratio.

Registrations: PreToolUse (Write|Edit; exit 2 = block, fail-open on anything unexpected) +
SessionStart --check (advisory: prints only when the standing backlog GREW — a gate that is always
red trains its operator to walk past it; the measure is monotone descent, not zero).
Baselines: `.claude/lessons-backlog` and `.claude/tasks-backlog` (git-tracked so raises are visible
in review). Each auto-lowers; neither is ever auto-raised — a grown count only warns, pointing at
the entries to split.
"""
import json
import os
import re
import sys

# One profile per guarded file. `entry_re` recognises an entry's FIRST line; anything else is a
# continuation of the current entry, and any `## `/`### ` heading ends it (TASKS lanes are `### `).
PROFILES = {
    "LESSONS.md": {
        "cap_key": "LESSONS_ENTRY", "default": 8, "baseline": ".claude/lessons-backlog",
        # Index lines and header/doctrine blocks are not entries (they carry no leading date).
        "entry_re": re.compile(r"^- 20\d\d-\d\d-\d\d"),
        "shape": ("Entry shape: RULE · MECHANISM · CHECK · permanent-record path. Case narrative\n"
                  "and number tables go to a report or docs/ — LESSONS is read IN FULL every\n"
                  "session. Raising the file cap is not the valve; splitting the entry is."),
    },
    "TASKS.md": {
        "cap_key": "TASKS_ENTRY", "default": 4, "baseline": ".claude/tasks-backlog",
        # the char-axis addition (audit 2026-09-05, owner-approved 2026-09-06): a board item is capped in CHARACTERS too,
        # because our lines run long — 4 lines x ~180 chars is 720, so the LINE budget alone let an
        # item stay a solution note with hard wraps. MEASURED the day it landed: 0 of 27 items
        # complied, median 1287, max 4795 ⇒ real work, not a formatting tidy-up. Enforced with the
        # SAME monotone-descent semantics as the line budget (only NEWLY-over or GROWN entries block;
        # shrinking always passes), because a gate red on every item trains its operator to walk past
        # it. Its legitimate destination is the SPEC file — rules §10.40's EPIC layer landed alongside it.
        "char_cap_key": "TASKS_ENTRY_CHARS", "char_default": 400,
        # A board item; the doctrine header's bullets carry no checkbox, so they are not entries.
        "entry_re": re.compile(r"^\s*- \[[ x]\]"),
        "shape": ("Item shape: id · @owner · due: · done-when · evidence path (rules §10.40).\n"
                  "Requirements and manual test scripts belong in the SPEC file; the problem →\n"
                  "root cause → fix story belongs in the solution note. TASKS.md is @-imported in\n"
                  "FULL by every session — a board item is a POINTER, not the delivery."),
    },
}


# Per-LINE caps for every always-loaded file (see header: THE SECOND BLIND SPOT). Keyed by the file
# name AT THE PROJECT ROOT — a `docs/x/TASKS.md` is not @-imported and is not guarded here.
LINE_CAPS = {"CLAUDE.md": "CLAUDE", "rules.md": "RULES", "HANDOVER.md": "HANDOVER",
             "LESSONS.md": "LESSONS", "TASKS.md": "TASKS"}
LINE_CHARS_DEFAULT = 400


def read_caps(root):
    """{KEY: int} from `.claude/keel-caps`; comment lines and unparseable values are ignored."""
    out = {}
    try:
        with open(os.path.join(root, ".claude", "keel-caps"), encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#")[0].strip()
                if "=" not in line:
                    continue
                k, _, v = line.partition("=")
                try:
                    out[k.strip()] = int(v.strip())
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def _tokenizer():
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def long_new_lines(before, after, char_cap, token_cap=None, enc=None):
    """[(line_no, measure, unit)] for over-cap lines of `after` that make the file WORSE.

    Monotone descent on this axis, by DOMINANCE: the over-cap measures of `after`, sorted longest
    first, must each be <= the matching one of `before`, and there may not be more of them. So a
    long line may stay, move or shrink; a NEW long line, or one made LONGER, blocks. (A plain
    "is it verbatim in before?" test was tried first and blocks a line that is being SHORTENED —
    cleanup must never be punished.)"""
    def measures(text):
        out = []
        for i, line in enumerate(text.splitlines(), 1):
            if char_cap and len(line) > char_cap:
                out.append((len(line), i, "characters"))
            elif token_cap and enc is not None:
                n = len(enc.encode(line))
                if n > token_cap:
                    out.append((n, i, "tokens"))
        return sorted(out, reverse=True)
    worse = []
    # Each UNIT is compared on its own: in one sorted list a new over-TOKEN line could "replace" an
    # old over-CHARACTER line and pass (found by the pre-release review).
    for unit in ("characters", "tokens"):
        old = [m for m in measures(before) if m[2] == unit]
        new = [m for m in measures(after) if m[2] == unit]
        worse += [m for k, m in enumerate(new) if k >= len(old) or m[0] > old[k][0]]
    return [(i, n, unit) for n, i, unit in sorted(worse, key=lambda m: m[1])]


def line_caps_for(root, name):
    """(char_cap, token_cap) for an always-loaded file; token_cap is None unless configured."""
    caps = read_caps(root)
    key = LINE_CAPS[name]
    default = LINE_CHARS_DEFAULT
    if name == "TASKS.md":
        # A board item already has its own CHARACTER budget; the line cap never undercuts it, or a
        # project that raised TASKS_ENTRY_CHARS would be blocked by a second, silent number.
        default = max(default, caps.get("TASKS_ENTRY_CHARS", 400))
    return caps.get(key + "_LINE_CHARS", default), caps.get(key + "_LINE_TOKENS")


def max_lines(root, prof, cap_key="cap_key", default_key="default"):
    """Cap for one axis, read from `.claude/keel-caps`. Returns None when the profile declares no
    such axis (only TASKS carries a character cap), so callers can skip it."""
    key = prof.get(cap_key)
    if key is None:
        return None
    try:
        with open(os.path.join(root, ".claude", "keel-caps"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith(key + "="):
                    return int(line.split("=", 1)[1].split("#")[0].strip())
    except (OSError, ValueError):
        pass
    return prof.get(default_key)


def entries(text, prof):
    """[(first_line, n_lines, n_chars)] for every entry in the text, per the file's profile.

    Lines inside a ``` fence are quoted text — a `- [ ]` example in a spec snippet or the doctrine
    header — and are neither an entry nor padding for the one before it (measured 2026-09-03: an
    index-difference count made them both). A `## `/`### ` heading ends the current entry."""
    out = []
    head, n, chars, fenced = None, 0, 0, False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if prof["entry_re"].match(line):
            if head is not None:
                out.append((head, n, chars))
            head, n, chars = line, 1, len(line.strip())
        elif line.startswith(("## ", "### ")):
            if head is not None:
                out.append((head, n, chars))
            head = None
        elif head is not None:
            n += 1
            chars += len(line.strip())
    if head is not None:
        out.append((head, n, chars))
    return out


def oversized(text, cap, prof, char_cap=None):
    """[(head, measure, unit)] — the LINE and CHARACTER axes are reported SEPARATELY, because a
    single number cannot say which axis was exceeded (the mutation-matrix lesson, one layer out)."""
    out = []
    for head, n, chars in entries(text, prof):
        if n > cap:
            out.append((head[:100], n, "lines"))
        elif char_cap and chars > char_cap:
            out.append((head[:100], chars, "characters"))
    return out


def _msg(bad, cap, name, prof, char_cap=None):
    limit = "max %d lines" % cap
    if char_cap:
        limit += " / %d characters" % char_cap
    parts = ["%s entry budget (%s) EXCEEDED:" % (name.replace(".md", ""), limit)]
    for head, n, unit in bad:
        parts.append("  %d %s — %s" % (n, unit, head))
    parts.append("")
    parts.append(prof["shape"])
    return "\n".join(parts)


def check(root):
    """SessionStart advisory, per guarded file: report only when the oversized-entry count GREW past
    the recorded baseline; auto-lower the baseline when it shrank. Never blocks, always exits 0."""
    for name, prof in PROFILES.items():
        path = os.path.join(root, name)
        if not os.path.exists(path):
            continue
        cap = max_lines(root, prof)
        char_cap = max_lines(root, prof, "char_cap_key", "char_default")
        try:
            with open(path, encoding="utf-8") as fh:
                bad = oversized(fh.read(), cap, prof, char_cap)
        except OSError:
            continue
        n = len(bad)
        bp = os.path.join(root, prof["baseline"])
        prev = None
        if os.path.exists(bp):
            try:
                with open(bp, encoding="utf-8") as fh:
                    prev = int((fh.read().split("#")[0] or "0").strip())
            except (OSError, ValueError):
                prev = None
        label = name.replace(".md", "")
        if prev is None or n < prev:
            try:
                with open(bp, "w", encoding="utf-8") as fh:
                    fh.write("%d  # entries over the %s per-entry budget; this number only goes"
                             " DOWN (auto-lowered; a raise means split the new oversized"
                             " entries)\n" % (n, label))
            except OSError:
                pass
            if prev is not None:
                print("[keel] %s entry backlog shrank: %d -> %d (budget %d lines/entry)."
                      % (label, prev, n, cap))
        elif n > prev:
            print("[keel] %s entry backlog GREW: %d -> %d entries over the %d-line budget — the"
                  " newest oversized entries should be split (detail -> report/docs/spec, the entry"
                  " keeps its shape). The per-entry budget exists because raising the FILE cap only"
                  " makes room for the tendency." % (label, prev, n, cap))
    return 0


def hook():
    """PreToolUse gate for Write|Edit on any guarded file. FAIL-OPEN on anything unexpected."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0
    ti = payload.get("tool_input") or {}
    fp = ti.get("file_path") or ""
    name = os.path.basename(fp)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if fp and not os.path.isabs(fp):
        fp = os.path.join(root, fp)   # else `before` is read from the cwd and every old line looks new
    at_root = os.path.abspath(os.path.dirname(fp) or root) == os.path.abspath(root)
    prof = PROFILES.get(name)
    if prof is None and not (at_root and name in LINE_CAPS):
        return 0
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

    # The entry budget speaks first (its message names the entry and its shape); the per-LINE cap
    # is the backstop that also covers the files without an entry profile (CLAUDE.md, rules.md,
    # HANDOVER.md).
    if prof is not None:
        rc = _entry_gate(root, fp, prof, before, after)
        if rc:
            return rc
    return _line_gate(root, name, at_root, before, after)


def _line_gate(root, name, at_root, before, after):
    if not (at_root and name in LINE_CAPS):
        return 0
    char_cap, token_cap = line_caps_for(root, name)
    enc = _tokenizer() if token_cap else None
    long = long_new_lines(before, after, char_cap, token_cap, enc)
    if not long:
        return 0
    sys.stderr.write(
        "%s per-LINE cap EXCEEDED (%d characters%s): %s\n"
        "One line = one fact. A narrative, a table or a round-by-round story goes to a report\n"
        "or docs/ and the line keeps a pointer to it — this file is loaded IN FULL by every\n"
        "session, and a line cap alone let one line reach 135 KB on a live project.\n"
        % (name, char_cap, (" / %d tokens" % token_cap) if token_cap and enc else "",
           ", ".join("line %d: %d %s" % x for x in long[:5])))
    return 2


def _entry_gate(root, fp, prof, before, after):
    cap = max_lines(root, prof)
    char_cap = max_lines(root, prof, "char_cap_key", "char_default")

    # Sizes are tracked PER AXIS: a line count and a character count are not comparable, and
    # keying them together would let a growing character count hide behind a steady line count.
    grew = []
    before_sizes = {}
    for head, n, chars in entries(before, prof):
        key = head[:100]
        prev = before_sizes.get(key, (0, 0))
        before_sizes[key] = (max(n, prev[0]), max(chars, prev[1]))
    for head, n, unit in oversized(after, cap, prof, char_cap):
        prev = before_sizes.get(head)
        prev_n = None if prev is None else (prev[0] if unit == "lines" else prev[1])
        if prev_n is None or n > prev_n:         # newly oversized, or an oversized entry grew
            grew.append((head, n, unit))
    if not grew:
        return 0                                 # shrinking/restructuring an oversized entry passes
    sys.stderr.write(_msg(grew, cap, os.path.basename(fp), prof, char_cap) + "\n")
    return 2


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "--check"
    try:
        if arg == "--hook":
            return hook()
        return check(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    except Exception:
        # FAIL-OPEN, always: a budget reminder must never break a write or a session start (an
        # odd payload, a non-UTF-8 file, a tokenizer that rejects special tokens).
        return 0


if __name__ == "__main__":
    sys.exit(main())
