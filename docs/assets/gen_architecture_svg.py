#!/usr/bin/env python3
"""Generate architecture.svg (this dir) — the colored tree + callout-card map of the
Keel repo shown in README.md. Data-driven: edit GROUPS below and re-run
(`python3 docs/assets/gen_architecture_svg.py`) when the layout changes — no manual
coordinate tweaking. Emits a self-contained SVG (own background, system fonts, no
external assets or scripts) so it renders in both GitHub light & dark themes."""
import html
import os

# ---- palette (Open Color, harmonized) ---------------------------------------
GROUND, BANDTOP = "#f4f6f9", "#eef1f6"
INK, MUTED, HAIR = "#212a35", "#5b6673", "#d7dde5"
CARD_BG = "#ffffff"

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
        ("skills/", "/keel-* workflows — handover · plan · audit"),
        ("agents/", "subagents — researcher · verifier · auditor"),
        ("rules/", "optional path-scoped rules"),
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


# layout pass (compute card bands + total height)
y, layout = START_Y, []
for label, accent, kids in GROUPS:
    ch = PAD_TOP + PILL_H + len(kids) * ROW_H + PAD_BOT
    layout.append((label, accent, kids, y, ch))
    y += ch + GAP
TOTAL_H = y + 66

p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{TOTAL_H}" '
         f'viewBox="0 0 {W} {TOTAL_H}" font-family="{SANS}" role="img" '
         f'aria-label="Keel repository structure map">')
p.append('<defs><filter id="sh" x="-8%" y="-8%" width="116%" height="130%">'
         '<feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#1b2a3f" flood-opacity="0.10"/>'
         '</filter></defs>')
p.append(f'<rect width="{W}" height="{TOTAL_H}" fill="{GROUND}"/>')
p.append(f'<rect width="{W}" height="{BAND_H}" fill="{BANDTOP}"/>')
p.append(f'<rect y="{BAND_H}" width="{W}" height="1" fill="{HAIR}"/>')
p.append(f'<text x="50" y="58" font-size="34" font-weight="800" letter-spacing="0.5" fill="{INK}">'
         f'KEEL<tspan font-weight="500" fill="{MUTED}"> — project structure</tspan></text>')
p.append(f'<text x="52" y="86" font-size="14.5" fill="{MUTED}">The discipline scaffold Claude Code reads '
         f'first — everything @-imported is re-injected after every compaction.</text>')
p.append(f'<rect x="{W-138}" y="34" width="88" height="26" rx="13" fill="{INK}"/>')
p.append(f'<text x="{W-94}" y="51.5" font-family="{MONO}" font-size="13" font-weight="700" fill="#fff" '
         f'text-anchor="middle">v0.8.0</text>')

root_y = START_Y - 8
p.append(f'<text x="{FICON_X}" y="{root_y}" font-family="{MONO}" font-size="15" font-weight="700" '
         f'fill="{INK}">claude-code-starter-kit/</text>')
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

fy = TOTAL_H - 34
p.append(f'<rect y="{fy-14}" width="{W}" height="1" fill="{HAIR}"/>')
p.append(f'<text x="50" y="{fy+8}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{INK}">keel</text>')
p.append(f'<text x="86" y="{fy+8}" font-size="12.5" fill="{MUTED}">clone = full kit + docs + permissions '
         f'&#8226; /plugin install keel@keel = the tooling layer, everywhere</text>')
p.append('</svg>')

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(p))
print(f"wrote {out}  ({TOTAL_H}px tall)")
