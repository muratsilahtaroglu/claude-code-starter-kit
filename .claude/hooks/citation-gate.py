#!/usr/bin/env python3
"""Do the artefacts our PERMANENT records cite actually exist in HEAD? — the provenance gate.

WHY (measured on a live project, backported 2026-09-03 with its two blind axes CLOSED):
`git commit -- <pathspec>` does NOT pick up an untracked file and does NOT error. So a solution
note gets written, cited from TASKS/LESSONS/an ADR/the reports index — and never lands. File
STATUS looks right while PROVENANCE quietly disappears. That class repeated THREE times in one day
there before the written rule (§6.18 "review what you stage") was promoted to a gate (§10.38:
enforced beats written). Keel already depends on citations resolving: §3.10 keeps a probe alive
because a permanent record NAMES it, §10.40 calls reports the permanent artefacts others cite, and
`/keel-distill`'s sweep into `done/` rewrites every citation "in the same pass" — nothing checked.

WHAT IT REPORTS, in three separate classes — a path is never silently dropped:
  GHOST        cited, exists on disk, NOT in HEAD  -> the real finding: commit it or stop citing it
  UNRESOLVED   cited, found nowhere                -> counted, not assumed innocent
  BY DESIGN    matched by .gitignore               -> a doc may legitimately say "create .env"
The third class exists because the source tool learned that a permanently-red gate trains its
operator to walk past it: "a gate with false positives is worse than no gate". It is a
CLASSIFICATION, not an exemption — the paths are still listed.

TWO BLIND AXES THIS PORT REMOVES. The source matched a hand-written list of trees and a
hand-written list of extensions, and each list was itself the bug — twice: a `.claude/` citation
read CLEAN for days because that tree was simply not in the list. Here the first path segment is
tested against the repo's ACTUAL top-level entries and the extension is not enumerated at all, so
a new tree or file type is covered the day it is created, with no list to forget.

INHERITED, HARD-WON, DO NOT SIMPLIFY:
* Lookbehind. Without it, a path whose TAIL begins with a real top-level name is read as a repo
  path: `~/reports/note.md` or `/reports/note.md` become `reports/note.md`, inventing a ghost when
  HEAD lacks it and declaring a real citation resolved when it has one. NOTE, measured 2026-09-03
  rather than inherited: the source tool called this 56% of its standing debt, but there the tree
  list was hand-written; HERE `repo_roots()` already rejects the common `/usr/lib/.../reports/x.md`
  shape, so the lookbehind's remaining job is only the leading-separator case above. The number does
  not transfer — the mechanism does (§10.37: re-derive the reference, do not import the figure).
* `os.path.normpath` before asking git. `os.path.exists("docs/../rules.md")` is True (the OS
  resolves it) but git rejects `..` inside a tree path, so every citation carrying `..` was
  reported as "on disk, not in HEAD" forever — an unfixable red.
* The `done/` variant. `/keel-distill` moves a closed task's files into the author's `done/`, but
  some citing files CANNOT be rewritten — `docs/handover-archive.md` is frozen verbatim by §1.4.
  So a citation resolves against its own path OR that path's `done/` sibling. ONE level, under the
  LAST directory component only: sprinkled deeper, the resolver would find a right-named file in
  the wrong place and call the citation sound, making the gate its own blind spot.
* Positive control. The pattern is exercised against a path known to be in HEAD; if that does not
  resolve, the tool is BROKEN (exit 2) and its silence means nothing. A checker that cannot fail
  loudly reports "clean" when it has stopped working.

exit 0 = clean · 1 = ghost citation(s) · 2 = the tool itself is broken.
Stdlib only, no network. Run: `python3 .claude/hooks/citation-gate.py [--stop]`
"""
import os
import re
import subprocess
import sys

# A path-like token: <segment>/<...>.<ext>. The lookbehind is load-bearing (see header).
PAT = re.compile(r"(?<![A-Za-z0-9_@./-])"
                 r"([A-Za-z0-9_@.-]+(?:/[A-Za-z0-9_@.-]+)+\.[A-Za-z0-9]{1,6})")
STATE = ".claude/.citation-gate-last"
ALLOW = ".claude/citation-allow"          # one path per line; reasons as # comments
# A record that MEASURED an absence (a deleted file, a probe copy removed after the run, "no such
# test was ever written") cites a path that must NOT exist — that citation IS the record, not a
# defect. Without a marker the gate discourages the most valuable record type there is. Writer's
# job, on the citing LINE: `... scratch/probe.py (RECORDED-ABSENT)`. Counted, never a ghost.
ABSENCE_MARK = "(RECORDED-ABSENT)"
# Line-number anchors into files that are CURATED or ROTATED by design rot structurally: the board
# is rewritten each round, a worker board is frozen to `board-<YYYY-MM>.md` when it grows. Measured
# 2026-08-27: 254 anchors into permanent files — 0 out of range; 50 into live memory — 14 (28%)
# out of range. And on 2026-09-06 a lane could not rotate its own board because 3 of 4
# `board.md:NNN` anchors lived on surfaces it may not edit. Cite the item id / section instead.
LIVE_ANCHOR = re.compile(r"(?<![A-Za-z0-9_/.-])((?:[A-Za-z0-9_@.-]+/)*"
                         r"(?:board|TASKS|HANDOVER|LESSONS|PLAN)\.md):(\d+)")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)


def repo_roots(root):
    """The repo's ACTUAL top-level entries — the membership test that replaces a hand-written list."""
    try:
        return {n for n in os.listdir(root) if not n.startswith(".git")} | {".claude", ".github"}
    except OSError:
        return set()


def md_files(root):
    """Every markdown file git knows about, tracked or not — a permanent record is still a record
    before it is committed, and the untracked ones are exactly where a dangling citation is born."""
    out = []
    for args in (("ls-files", "--", "*.md"), ("ls-files", "--others", "--exclude-standard", "--", "*.md")):
        r = git(root, *args)
        if r.returncode == 0:
            out += [l for l in r.stdout.splitlines() if l]
    return sorted(set(out))


def in_head(root, p):
    return git(root, "cat-file", "-e", "HEAD:" + os.path.normpath(p)).returncode == 0


def done_variant(p):
    """`<dir>/<name>` -> `<dir>/done/<name>`; one level, last component only (see header)."""
    d, n = os.path.split(p)
    if not d or os.path.basename(d) == "done":
        return None
    return os.path.join(d, "done", n)


def ignored_by_design(root, p):
    """Judged by PATTERN, never by existence — otherwise the same path would change class the day
    the file appears or is deleted, and the classification would drift with the working tree."""
    return git(root, "check-ignore", "-q", os.path.normpath(p)).returncode == 0


def classify(root, path):
    """-> 'ok' | 'ghost' | 'ignored' | 'unresolved'."""
    for cand in (path, done_variant(path)):
        if cand and in_head(root, cand):
            return "ok"
    if ignored_by_design(root, path):
        return "ignored"
    for cand in (path, done_variant(path)):
        if cand and os.path.exists(os.path.join(root, cand)):
            return "ghost"
    return "unresolved"


def cited_paths(root, files, recorded_absent=None, live_anchors=None):
    """{path: [citing files]} for every token whose first segment is a real top-level entry.

    A line carrying ABSENCE_MARK is skipped here and its paths are appended to `recorded_absent`
    (a list, if given) — the record SAYS the file is gone, so "not in HEAD" is the expected reading.
    Line-number anchors into live/rotating files go to `live_anchors` as (citing file, anchor)."""
    roots = repo_roots(root)
    out = {}
    for f in files:
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for line in text.splitlines():
            if live_anchors is not None:
                for m in LIVE_ANCHOR.finditer(line):
                    live_anchors.append((f, "%s:%s" % (m.group(1), m.group(2))))
            marked = ABSENCE_MARK in line
            for m in PAT.finditer(line):
                p = m.group(1)
                if p.split("/", 1)[0] not in roots:
                    continue
                # The marker says the file is GONE. A marked path that is still on disk is not a
                # measured absence — it is a ghost wearing the marker, so it falls through and is
                # reported like any other (the reviewer's refutation, 2026-09-06).
                if marked and not os.path.exists(os.path.join(root, p)):
                    if recorded_absent is not None:
                        recorded_absent.append(p)
                    continue
                out.setdefault(p, []).append(f)
    return out


def self_test(root):
    """Positive control: a path we KNOW is in HEAD must classify 'ok'. Otherwise the tool is broken
    and its 'clean' means nothing."""
    r = git(root, "ls-files", "--", "*/*.md")
    for cand in r.stdout.splitlines():
        if PAT.fullmatch(cand) and cand.split("/", 1)[0] in repo_roots(root):
            return classify(root, cand) == "ok", cand
    return True, None            # nothing shaped like the pattern is tracked — nothing to prove


def report(root):
    files = md_files(root)
    if not files:
        return 0
    ok, probe = self_test(root)
    if not ok:
        print("[citation-gate] BROKEN: the pattern does not resolve a path that IS in HEAD (%s) — "
              "a 'clean' result from this run means nothing. Fix the tool before trusting it."
              % probe, file=sys.stderr)
        return 2
    allow = set()
    ap = os.path.join(root, ALLOW)
    if os.path.exists(ap):
        with open(ap, encoding="utf-8") as fh:
            allow = {l.split("#")[0].strip() for l in fh if l.split("#")[0].strip()}
    ghosts, unresolved, ignored = {}, [], []
    absent, anchors = [], []
    for p, citers in sorted(cited_paths(root, files, absent, anchors).items()):
        if p in allow:
            continue
        kind = classify(root, p)
        if kind == "ghost":
            ghosts[p] = citers
        elif kind == "unresolved":
            unresolved.append(p)
        elif kind == "ignored":
            ignored.append(p)
    if ghosts:
        print("[citation-gate] %d citation(s) point at files that exist on disk but NOT in HEAD — "
              "`git commit -- <path>` skips an untracked file WITHOUT erroring, so the record kept "
              "the reference and the artefact never landed (rules §6.18/§10.40):" % len(ghosts))
        for p, citers in ghosts.items():
            print("    %s   ← cited by %s" % (p, ", ".join(sorted(set(citers))[:3])))
        print("    Fix: commit the artefact, or remove the citation. Deliberately-absent paths go "
              "in %s with a reason." % ALLOW)
    if unresolved:
        print("[citation-gate] %d cited path(s) found NOWHERE (not on disk, not in HEAD, not "
              "ignored) — counted, not assumed harmless: %s" % (len(unresolved), ", ".join(unresolved[:8])))
    # The BY DESIGN class exists so an ignored path is never SILENTLY dropped — but printing it when
    # there is nothing else to say is the noise this gate warns about, every run, forever. It is
    # context for a real finding, so it rides along with one and stays quiet on its own.
    if ignored and (ghosts or unresolved):
        print("[citation-gate] (context) %d other cited path(s) are .gitignore'd BY DESIGN — a doc may "
              "legitimately name a file nobody commits; listed, not counted: %s"
              % (len(ignored), ", ".join(ignored[:5])))
    # RECORDED-ABSENT is a class, not an exemption: the count is printed so a marker cannot become
    # the quiet way to make a ghost disappear — but only beside a real finding (no standing noise).
    if absent and (ghosts or unresolved):
        print("[citation-gate] (context) %d cited path(s) are marked %s by their record — measured "
              "absences, not checked against HEAD: %s"
              % (len(set(absent)), ABSENCE_MARK, ", ".join(sorted(set(absent))[:5])))
    # Line anchors into curated/rotating files are a WARNING class of their own (exit stays 0 for
    # them): the anchor was right the day it was written and rots by design — and it blocks the
    # cited board's rotation, because the lane may not rewrite the surface that carries it.
    if anchors:
        shown = sorted(set("%s ← %s" % (a, f) for f, a in anchors))
        print("[citation-gate] %d line-number anchor(s) into files that are curated or rotated by "
              "design (`board.md:N`, TASKS/HANDOVER/LESSONS/PLAN) — an anchor there is stale by the "
              "next round and pins the file against rotation (§10.42); cite the item id or section "
              "instead: %s" % (len(shown), "; ".join(shown[:6])))
    return 1 if ghosts else 0


def stop_hook(root):
    """Stop-hook mode: only when the candidate .md set CHANGED. An untracked record sitting in the
    tree would otherwise re-fire every single turn, and an always-red gate teaches its operator to
    ignore it — the exact failure this gate exists to avoid. Never blocks: prints and exits 0."""
    files = md_files(root)
    fp = str(sorted((f, os.path.getmtime(os.path.join(root, f)))
                    for f in files if os.path.exists(os.path.join(root, f))))
    sp = os.path.join(root, STATE)
    try:
        with open(sp, encoding="utf-8") as fh:
            if fh.read() == fp:
                return 0
    except OSError:
        pass
    try:
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        with open(sp, "w", encoding="utf-8") as fh:
            fh.write(fp)
    except OSError:
        pass
    report(root)
    return 0


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not os.path.isdir(os.path.join(root, ".git")):
        return 0
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--stop":
            return stop_hook(root)
        return report(root)
    except Exception as exc:                      # fail-open: a reminder must never break a session
        print("[citation-gate] skipped (%s)" % exc, file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
