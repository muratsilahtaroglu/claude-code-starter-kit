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
* Lookbehind. Without it a LONGER foreign path's tail matches as a local path, and it is harmful
  both ways: absent from HEAD it invents a ghost, present it declares a real citation resolved.
  Measured there as 56% of the standing debt.
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


def cited_paths(root, files):
    """{path: [citing files]} for every token whose first segment is a real top-level entry."""
    roots = repo_roots(root)
    out = {}
    for f in files:
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for m in PAT.finditer(text):
            p = m.group(1)
            if p.split("/", 1)[0] in roots:
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
    for p, citers in sorted(cited_paths(root, files).items()):
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
    if ignored:
        print("[citation-gate] %d cited path(s) are .gitignore'd BY DESIGN (a doc may legitimately "
              "name a file nobody commits) — listed, not counted: %s"
              % (len(ignored), ", ".join(ignored[:5])))
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
