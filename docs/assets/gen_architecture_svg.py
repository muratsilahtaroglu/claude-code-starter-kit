#!/usr/bin/env python3
"""Generate the README's data-driven diagrams (this dir) — same visual language, three maps:
  architecture.svg  — the colored tree + callout-card map of the Keel repo
  code-layout.svg   — "where your code lives": discipline / support / YOUR src tree
  what-keel-fixes.svg — the problem → mechanism ladder (rose problem box → emerald mechanism box)
Edit the GROUPS/FIXES lists below and re-run (`python3 docs/assets/gen_architecture_svg.py`) when
the content changes — no manual coordinate tweaking. Emits self-contained SVGs (own background,
system fonts, no external assets or scripts) so they render in both GitHub light & dark themes."""
import html
import os

# ---- palette (Open Color, harmonized) ---------------------------------------
GROUND, BANDTOP = "#f4f6f9", "#eef1f6"
INK, MUTED, HAIR = "#212a35", "#5b6673", "#d7dde5"
CARD_BG = "#ffffff"
VERSION = "v0.8.8"

# ---- data: each group -> (pill label, accent, [(name, desc), ...]) ----------
GROUPS = [
    ("constitution + memory", "#d6336c", [
        ("CLAUDE.md", "read first — @-imports the 4 memory files"),
        ("rules.md", "working discipline: docs·tests·security·git"),
        ("HANDOVER · LESSONS · TASKS", "session memory — survives every compaction"),
        ("PLAN.md", "phase map: status table + Mermaid DAG"),
    ]),
    (".claude/", "#1c7ed6", [
        ("settings.json", "permissions — deny secrets · ask before push"),
        ("hooks/", "deterministic guards — block-dangerous · nudges"),
        ("skills/", "12 /keel-* workflows — handover · plan · pilot · autopilot"),
        ("agents/", "subagents — researcher · verifier · auditor"),
        ("rules/", "optional path-scoped rules"),
        ("snapshots/ · last-audit · ritual-log", "runtime state — appears as you work"),
    ]),
    (".claude-plugin/", "#7048e8", [
        ("plugin.json", "bundles skills·agents·hooks as the “keel” plugin"),
        ("marketplace.json", "self-hosted — /plugin marketplace add"),
    ]),
    ("docs/", "#0ca678", [
        ("architecture.md", "live module map — updated on every change"),
        ("security.md", "supply-chain: pin · hash · non-root · CI"),
        ("layouts.md · steering.md", "layout profiles · mechanism guide"),
        ("adr/", "architecture decision records"),
    ]),
    ("requirements/", "#e8590c", [
        ("base.txt · base.lock", "runtime deps — pinned (==) + hash-locked"),
        ("dev.txt · dev.lock", "dev tooling — never enters the prod image"),
    ]),
    ("project scaffold", "#0c8599", [
        ("config/ · tests/ · research/", "params · unit·integration·e2e · findings"),
        (".github/", "CI — hash-verify · pip-audit · .pth scan"),
        ("Dockerfile · Makefile", "multi-stage non-root build · make targets"),
    ]),
]

CODE_GROUPS = [
    ("discipline — fixed, at root", "#d6336c", [
        ("CLAUDE.md · rules.md", "constitution — read first, always loaded"),
        ("HANDOVER · LESSONS · TASKS", "session memory — travels through git"),
        ("PLAN.md", "phase map — gates flip only at rituals"),
    ]),
    ("support — fixed", "#1c7ed6", [
        (".claude/", "skills · hooks · agents · permissions"),
        ("docs/ · tests/", "architecture + ADRs · unit/integration/e2e"),
        ("config/ · requirements/", "env params · pinned + hash-locked deps"),
        ("scratch/ · reports/ · research/", "experiments · generated reports · findings"),
    ]),
    ("src/ — YOUR CODE", "#0ca678", [
        ("src/<app-or-package>/", "created at bootstrap from a docs/layouts.md profile"),
        ("data/ · entrypoint/ · notebooks/", "ML-profile extras — only if your project needs them"),
        ("prompts as versioned files", "LLM apps: runtime prompts live under src/, read from disk"),
    ]),
]

# ---- data: problem -> mechanism ladder (title, body) pairs ------------------
FIXES = [
    (("Volatile memory",
      "Context fills → lossy compaction; decisions, verbal agreements and warnings vanish — every session restarts half-blind."),
     ("Repo = durable disk",
      "Critical facts hit HANDOVER / LESSONS / TASKS the moment they appear and auto-reload every session; a stale manual /compact is blocked outright (compact-gate).")),
    (("Repeated mistakes",
      "Failed approaches aren't remembered — the same dead end is re-entered, burning time and tokens."),
     ("Permanent “tried, didn't work” record",
      "HANDOVER (b) + LESSONS [fail] load automatically every session — a dead end is entered once.")),
    (("A free hand",
      "A model slip or prompt injection becomes rm -rf, a committed secret, a force-push. Writing “don't” is not a guarantee."),
     ("Enforcement layer",
      "Hooks reject the command before it runs; permissions make secrets unreadable; push waits for approval. Text advises — hooks and permissions guarantee.")),
    (("Dependency + supply-chain chaos",
      "Scattered manifests, open ranges (>=) — one poisoned release away from an incident."),
     ("One home + five barriers",
      "requirements/ with == pins + hashed lock + pip-audit + .pth scan + non-root container + security CI on every PR.")),
    (("File sprawl",
      "The agent invents files ad hoc; the root fills with mystery files; the architecture drifts."),
     ("Layout contract",
      "Code only under src/; every structural change lands in architecture.md; no unexplained file survives a session — drift hunted by hooks + auditor.")),
    (("Scattered throwaway code & prompts",
      "Experiments and one-off scripts leak into the main tree; the same prompt is improvised again and again."),
     ("Quarantine + promotion",
      "Experiments only in scratch/ (1-line purpose header); runtime prompts versioned under src/; the SECOND similar ad-hoc prompt is promoted to a skill.")),
    (("Unproven “it works”",
      "Tests postponed, claims not backed by a run, bulk outputs shipped blind."),
     ("Test contract + pilot gate",
      "Tests written + run per change; e2e evidence at phase gates; bulk jobs pass /keel-pilot: smoke → gold set → staged ramp → acceptance sample.")),
    (("Plan-free drift",
      "Phases skipped, five things in flight, “done” claimed without proof."),
     ("Gated phase map + single-task flow",
      "PLAN.md DAG with verifiable gates; work only from TASKS ## Now (max 3–5); done flips only via /keel-phase-review — a Stop hook catches skipped flips.")),
    (("Person-dependent knowledge",
      "The project lives in one head / one machine; a departure resets it."),
     ("Memory in the repo",
      "Travels through git; a new person or session loads the same five files and is oriented in minutes — even with no AI access at all.")),
    (("No trail",
      "“Why did we build it this way?” has no answer; there is nothing to audit."),
     ("Audit-ready trail",
      "Every decision an ADR, every session a HANDOVER block, every phase in PLAN.md + its fix log.")),
    (("Unmeasurable discipline",
      "Rules exist on paper; nobody knows whether they actually run."),
     ("Enforce + measure",
      "Telemetry logs every skill/command/compact/BLOCK; /keel-stats renders it visually; /keel-audit samples commit ranges against the rules.")),
    (("One-size-fits-all templates",
      "Starter kits dump their full structure onto every project."),
     ("Prune-to-fit bootstrap",
      "The first session tailors the kit to THIS project (remove · add · layout) with approval; /keel-adopt overlays existing projects non-destructively.")),
]

# ---- geometry ---------------------------------------------------------------
W = 1200
BAND_H, START_Y = 108, 150
SPINE_X, FICON_X, FNAME_X = 62, 74, 94
CHILD_VX, CHILD_TX = 88, 104
CARD_X, CARD_W = 486, 664
PILL_H, ROW_H = 30, 23
PAD_TOP, PAD_BOT, GAP = 14, 16, 20

MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"


def esc(s):
    return html.escape(s, quote=False)


def darken(hexc, f=0.72):
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    return f"#{int(r*f):02x}{int(g*f):02x}{int(b*f):02x}"


def emit(groups, title_thin, subtitle, root_label, footer_text, aria, outfile):
    # layout pass (compute card bands + total height)
    y, layout = START_Y, []
    for label, accent, kids in groups:
        ch = PAD_TOP + PILL_H + len(kids) * ROW_H + PAD_BOT
        layout.append((label, accent, kids, y, ch))
        y += ch + GAP
    total_h = y + 66

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h}" '
             f'viewBox="0 0 {W} {total_h}" font-family="{SANS}" role="img" '
             f'aria-label="{aria}">')
    p.append('<defs><filter id="sh" x="-8%" y="-8%" width="116%" height="130%">'
             '<feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#1b2a3f" flood-opacity="0.10"/>'
             '</filter></defs>')
    p.append(f'<rect width="{W}" height="{total_h}" fill="{GROUND}"/>')
    p.append(f'<rect width="{W}" height="{BAND_H}" fill="{BANDTOP}"/>')
    p.append(f'<rect y="{BAND_H}" width="{W}" height="1" fill="{HAIR}"/>')
    p.append(f'<text x="50" y="58" font-size="34" font-weight="800" letter-spacing="0.5" fill="{INK}">'
             f'KEEL<tspan font-weight="500" fill="{MUTED}"> — {esc(title_thin)}</tspan></text>')
    p.append(f'<text x="52" y="86" font-size="14.5" fill="{MUTED}">{esc(subtitle)}</text>')
    p.append(f'<rect x="{W-138}" y="34" width="88" height="26" rx="13" fill="{INK}"/>')
    p.append(f'<text x="{W-94}" y="51.5" font-family="{MONO}" font-size="13" font-weight="700" fill="#fff" '
             f'text-anchor="middle">{VERSION}</text>')

    root_y = START_Y - 8
    p.append(f'<text x="{FICON_X}" y="{root_y}" font-family="{MONO}" font-size="15" font-weight="700" '
             f'fill="{INK}">{esc(root_label)}</text>')
    last_folder_y = layout[-1][3] + PAD_TOP + PILL_H / 2
    p.append(f'<path d="M{SPINE_X} {root_y+8} V{last_folder_y}" stroke="{HAIR}" stroke-width="1.6" fill="none"/>')

    for label, accent, kids, gy, ch in layout:
        accent_d = darken(accent)
        folder_cy = gy + PAD_TOP + PILL_H / 2
        p.append(f'<path d="M{SPINE_X} {folder_cy} H{FICON_X-4}" stroke="{accent}" stroke-width="1.8" fill="none"/>')
        fg = FICON_X - 2
        p.append(f'<path d="M{fg} {folder_cy-6} h6 l2 3 h7 v9 a1.5 1.5 0 0 1 -1.5 1.5 h-19 a1.5 1.5 0 0 1 -1.5 -1.5 '
                 f'v-11 a1.5 1.5 0 0 1 1.5 -1.5 z" fill="{accent}" opacity="0.92"/>')
        p.append(f'<text x="{FNAME_X}" y="{folder_cy+5}" font-family="{MONO}" font-size="14.5" font-weight="700" '
                 f'fill="{accent_d}">{esc(label)}</text>')
        by0 = gy + PAD_TOP + PILL_H + 10
        n = len(kids)
        p.append(f'<path d="M{CHILD_VX} {folder_cy+10} V{by0+(n-1)*ROW_H+4}" stroke="{accent}" stroke-width="1.4" '
                 f'fill="none" opacity="0.45"/>')
        for k, (name, _d) in enumerate(kids):
            ry = by0 + k * ROW_H + 4
            p.append(f'<path d="M{CHILD_VX} {ry} H{CHILD_TX-4}" stroke="{accent}" stroke-width="1.4" fill="none" opacity="0.45"/>')
            p.append(f'<text x="{CHILD_TX}" y="{ry+4.5}" font-family="{MONO}" font-size="13" fill="{INK}">{esc(name)}</text>')
        p.append(f'<path d="M410 {folder_cy} C440 {folder_cy}, 452 {folder_cy}, {CARD_X-2} {folder_cy}" '
                 f'stroke="{accent}" stroke-width="2" fill="none" opacity="0.55"/>')
        p.append(f'<circle cx="412" cy="{folder_cy}" r="2.6" fill="{accent}"/>')
        p.append(f'<rect x="{CARD_X}" y="{gy}" width="{CARD_W}" height="{ch}" rx="12" fill="{CARD_BG}" '
                 f'stroke="{accent}" stroke-width="1.4" filter="url(#sh)"/>')
        pill_w = int(18 + len(label) * 9.3 + 18)
        p.append(f'<rect x="{CARD_X+16}" y="{gy+PAD_TOP}" width="{pill_w}" height="{PILL_H}" rx="8" fill="{accent}"/>')
        p.append(f'<text x="{CARD_X+16+pill_w/2}" y="{gy+PAD_TOP+PILL_H/2+5}" font-family="{MONO}" font-size="14.5" '
                 f'font-weight="700" fill="#fff" text-anchor="middle">{esc(label)}</text>')
        for k, (name, desc) in enumerate(kids):
            ry = by0 + k * ROW_H + 4
            p.append(f'<circle cx="{CARD_X+26}" cy="{ry}" r="3" fill="{accent}"/>')
            p.append(f'<text x="{CARD_X+40}" y="{ry+4.5}" font-size="13.5">'
                     f'<tspan font-family="{MONO}" font-weight="700" fill="{accent_d}">{esc(name)}</tspan>'
                     f'<tspan font-family="{SANS}" fill="{MUTED}">  {esc(desc)}</tspan></text>')

    fy = total_h - 34
    p.append(f'<rect y="{fy-14}" width="{W}" height="1" fill="{HAIR}"/>')
    p.append(f'<text x="50" y="{fy+8}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{INK}">keel</text>')
    p.append(f'<text x="86" y="{fy+8}" font-size="12.5" fill="{MUTED}">{footer_text}</text>')
    p.append('</svg>')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), outfile)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    print(f"wrote {out}  ({total_h}px tall)")


def wrap(text, limit):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        cand = (cur + " " + w_).strip()
        if len(cand) <= limit:
            cur = cand
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def emit_fixes(rows, outfile):
    ROSE, EMER = "#d6336c", "#0ca678"
    ROSE_S, EMER_S = "#fdf0f5", "#ecfaf5"
    COLW, ARROW_W, MX = 532, 56, 30          # column width, arrow gap, side margin
    PADX, LINE_H, CHARS = 16, 17, 68
    lx, rx = MX, MX + COLW + ARROW_W
    ax = MX + COLW + ARROW_W / 2

    # layout pass
    y0, rows_l = START_Y - 24, []
    y = y0
    for (pt, pb), (mt, mb) in rows:
        pl, ml = wrap(pb, CHARS), wrap(mb, CHARS)
        n = max(len(pl), len(ml))
        bh = 12 + 15 + 8 + n * LINE_H + 10   # pad + title + gap + body + pad
        rows_l.append((pt, pl, mt, ml, y, bh))
        y += bh + 12
    total_h = y + 54

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h}" '
             f'viewBox="0 0 {W} {total_h}" font-family="{SANS}" role="img" '
             f'aria-label="What Keel fixes: each problem of undisciplined AI-assisted work paired with the Keel mechanism that closes it">')
    p.append(f'<rect width="{W}" height="{total_h}" fill="{GROUND}"/>')
    p.append(f'<rect width="{W}" height="{BAND_H}" fill="{BANDTOP}"/>')
    p.append(f'<rect y="{BAND_H}" width="{W}" height="1" fill="{HAIR}"/>')
    p.append(f'<text x="50" y="58" font-size="34" font-weight="800" letter-spacing="0.5" fill="{INK}">'
             f'KEEL<tspan font-weight="500" fill="{MUTED}"> — what it fixes</tspan></text>')
    p.append(f'<text x="52" y="86" font-size="14.5" fill="{MUTED}">'
             f'<tspan font-weight="700" fill="{darken(ROSE)}">left:</tspan> what goes wrong without discipline'
             f'   <tspan font-weight="700" fill="{darken(EMER)}">right:</tspan> the mechanism that closes it</text>')
    p.append(f'<rect x="{W-138}" y="34" width="88" height="26" rx="13" fill="{INK}"/>')
    p.append(f'<text x="{W-94}" y="51.5" font-family="{MONO}" font-size="13" font-weight="700" fill="#fff" '
             f'text-anchor="middle">{VERSION}</text>')

    for pt, pl, mt, ml, ry, bh in rows_l:
        for bx, bt, bl, acc, fill in ((lx, pt, pl, ROSE, ROSE_S), (rx, mt, ml, EMER, EMER_S)):
            p.append(f'<rect x="{bx}" y="{ry}" width="{COLW}" height="{bh}" rx="11" fill="{fill}" '
                     f'stroke="{acc}" stroke-width="1.4" opacity="0.97"/>')
            p.append(f'<text x="{bx+PADX}" y="{ry+24}" font-size="14" font-weight="750" '
                     f'fill="{darken(acc)}">{esc(bt)}</text>')
            for i, ln in enumerate(bl):
                p.append(f'<text x="{bx+PADX}" y="{ry+24+8+ (i+1)*LINE_H}" font-size="13" '
                         f'fill="{INK}" opacity="0.82">{esc(ln)}</text>')
        p.append(f'<text x="{ax}" y="{ry+bh/2+7}" font-size="20" font-weight="800" fill="{MUTED}" '
                 f'text-anchor="middle">→</text>')

    fy = total_h - 30
    p.append(f'<rect y="{fy-14}" width="{W}" height="1" fill="{HAIR}"/>')
    p.append(f'<text x="50" y="{fy+8}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{INK}">keel</text>')
    p.append(f'<text x="86" y="{fy+8}" font-size="12.5" fill="{MUTED}">text advises &#8226; hooks and permissions guarantee &#8226; telemetry proves it ran</text>')
    p.append('</svg>')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), outfile)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(p) + "\n")
    print(f"wrote {out}  ({total_h}px tall)")


emit(GROUPS,
     "project structure",
     "The discipline scaffold Claude Code reads first — everything @-imported is re-injected after every compaction.",
     "claude-code-starter-kit/",
     'clone = full kit + docs + permissions &#8226; /plugin install keel@keel = the tooling layer, everywhere',
     "Keel repository structure map",
     "architecture.svg")

emit(CODE_GROUPS,
     "where your code lives",
     "Discipline at the root, support beside it, YOUR code in its own tree — a shell around the project, not a mold.",
     "your-project/",
     'the kit ships no src/ &#8226; the bootstrap creates it from a docs/layouts.md profile, with your approval',
     "Where your code lives: discipline and support at the root, application code under src/",
     "code-layout.svg")

emit_fixes(FIXES, "what-keel-fixes.svg")
