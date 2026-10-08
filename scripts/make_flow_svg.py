#!/usr/bin/env python3
"""Generate docs/flow.svg — the animated diagram of one feature going through /fe:run.

    python3 scripts/make_flow_svg.py

Pure SVG + SMIL, no scripts: GitHub renders README images through an image proxy that
strips JavaScript but keeps SMIL animation. The first frame is a complete static diagram,
so a viewer that does not animate still shows the whole flow.

Edit the STAGES / timing below and re-run; never hand-edit the SVG.
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "flow.svg"

W, H = 1200, 760
ROW1, ROW2 = 230, 435
TICKET_Y = 132
SPEED = 300.0          # px per second for the moving token
LOOP_R = 30            # radius of the build loop
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

C = {
    "bg": "#ffffff", "border": "#e5e7eb", "ink": "#111827", "muted": "#6b7280",
    "node": "#f8fafc", "nodeStroke": "#cbd5e1", "teal": "#0f766e", "tealSoft": "#ccfbf1",
    "amber": "#b45309", "amberSoft": "#fef3c7", "violet": "#6d28d9", "violetSoft": "#ede9fe",
    "line": "#94a3b8",
}

# kind: stage | gate | loop | handoff | done
# (key, kind, x, y, title, agent, subtitle, hold seconds)
STAGES = [
    ("ticket", "ticket", 95, TICKET_Y, "Ticket", "", "find it, or draft one", 0.9),
    ("spec", "stage", 95, ROW1, "Spec", "fe-spec", "UI plan, questions", 0.9),
    ("g1", "gate", 225, ROW1, "You approve", "", "the spec", 1.6),
    ("plan", "stage", 355, ROW1, "Plan", "fe-plan", "file-level steps", 0.7),
    ("g2", "gate", 485, ROW1, "You approve", "", "the plan", 1.6),
    ("test", "stage", 615, ROW1, "Test plan", "fe-test", "cases + library", 0.8),
    ("branch", "stage", 790, ROW1, "Branch", "fe-git", "from the ticket", 0.5),
    ("build", "loop", 1050, ROW1, "Build", "", "", 0.3),
    ("verify", "stage", 1050, ROW2, "Verify", "fe-verify", "all gates, DoD", 0.6),
    ("audit", "stage", 870, ROW2, "Audit", "fe-audit", "security, perf, UI", 0.6),
    ("e2e", "stage", 690, ROW2, "Browser run", "fe-e2e", "as each role", 0.9),
    ("handoff", "handoff", 440, ROW2, "Handoff", "", "", 3.0),
    ("done", "done", 150, ROW2, "Done", "", "", 1.4),
]
NODE_W, NODE_H = 140, 84
HANDOFF_CHIPS = ["Library", "Commit", "PR", "Jira"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=15, weight=400, fill=None, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill or C["ink"]}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


# ---------- the token's path and its timing ----------

def build_motion():
    """Path data, keyPoints, keyTimes, total duration, and each stage's active window."""
    segs = []      # (svg path fragment, length)
    marks = []     # (stage key, distance at arrival, hold)
    pos = (STAGES[0][2], STAGES[0][3])
    d = f"M{pos[0]},{pos[1]}"
    dist = 0.0
    marks.append((STAGES[0][0], 0.0, STAGES[0][-1]))
    for key, kind, x, y, *_rest, hold in STAGES[1:]:
        seg = math.dist(pos, (x, y))
        d += f" L{x},{y}"
        dist += seg
        pos = (x, y)
        if kind == "loop":
            # Twice round the build loop: build -> verify -> step check, per plan step.
            r = LOOP_R
            d += f" L{x - r},{y}"
            dist += r
            for _ in range(2):
                d += f" A{r},{r} 0 1,1 {x + r},{y} A{r},{r} 0 1,1 {x - r},{y}"
                dist += 2 * math.pi * r
            d += f" L{x},{y}"
            dist += r
        marks.append((key, dist, hold))
    total_len = dist

    # Time: movement at SPEED, plus holds at each mark.
    times, points = [0.0], [0.0]
    t = 0.0
    windows = {}
    prev_dist = 0.0
    for key, at, hold in marks:
        t += (at - prev_dist) / SPEED
        arrive = t
        times.append(t); points.append(at / total_len)
        t += hold
        times.append(t); points.append(at / total_len)
        windows[key] = (arrive, t)
        prev_dist = at
    rest = 0.8
    total = t + rest
    times.append(total); points.append(1.0)
    # keyTimes must start at 0 and end at 1, strictly non-decreasing.
    key_times = ";".join(f"{x / total:.4f}" for x in times)
    key_points = ";".join(f"{p:.4f}" for p in points)
    return d, key_points, key_times, total, windows


def window_anim(attr, on, off, start, end, total, fade=0.15):
    """values/keyTimes that switch `attr` from off to on between start and end."""
    a = max(0.0, start - fade) / total
    b = start / total
    c = min(end, total) / total
    e = min(end + fade, total) / total
    kt = [0.0, a, b, c, e, 1.0]
    for i in range(1, len(kt)):
        kt[i] = max(kt[i], kt[i - 1])
    vals = [off, off, on, on, off, off]
    return (f'<animate attributeName="{attr}" dur="{total:.2f}s" repeatCount="indefinite" '
            f'calcMode="linear" keyTimes="{";".join(f"{k:.4f}" for k in kt)}" '
            f'values="{";".join(vals)}"/>')


# ---------- drawing ----------

def node_box(cx, cy, w, h, title, sub, key, windows, total, stroke=None, agent=""):
    x, y = cx - w / 2, cy - h / 2
    start, end = windows[key]
    out = [f'<g>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["node"]}" '
           f'stroke="{stroke or C["nodeStroke"]}" stroke-width="1.5"/>',
           # highlight overlay
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["tealSoft"]}" '
           f'stroke="{C["teal"]}" stroke-width="2.5" opacity="0">'
           + window_anim("opacity", "1", "0", start, end, total) + '</rect>',
           text(cx, cy - (8 if agent else 4), title, 18, 700),
           (text(cx, cy + 12, agent, 12, 600, C["teal"],
                 extra='font-family="ui-monospace, SFMono-Regular, Menlo, monospace"') if agent else ""),
           text(cx, cy + (30 if agent else 18), sub, 12.5, 400, C["muted"]),
           '</g>']
    return "\n".join(out)


def gate(cx, cy, title, sub, key, windows, total):
    s = 30
    pts = f"{cx},{cy - s} {cx + s},{cy} {cx},{cy + s} {cx - s},{cy}"
    start, end = windows[key]
    return "\n".join([
        f'<polygon points="{pts}" fill="{C["amberSoft"]}" stroke="{C["amber"]}" stroke-width="2"/>',
        f'<polygon points="{pts}" fill="{C["amber"]}" opacity="0">'
        + window_anim("opacity", "1", "0", start, end, total) + '</polygon>',
        # pause glyph
        f'<g fill="{C["amber"]}"><rect x="{cx - 7}" y="{cy - 9}" width="5" height="18" rx="1"/>'
        f'<rect x="{cx + 2}" y="{cy - 9}" width="5" height="18" rx="1"/></g>',
        f'<g fill="#ffffff" opacity="0">'
        + window_anim("opacity", "1", "0", start, end, total)
        + f'<rect x="{cx - 7}" y="{cy - 9}" width="5" height="18" rx="1"/>'
        f'<rect x="{cx + 2}" y="{cy - 9}" width="5" height="18" rx="1"/></g>',
        text(cx, cy + s + 22, title, 14, 700, C["amber"]),
        text(cx, cy + s + 40, sub, 12.5, 400, C["muted"]),
    ])


def build_loop(cx, cy, key, windows, total):
    w, h = 190, 150
    x, y = cx - w / 2, cy - h / 2
    start, end = windows[key]
    # The loop is visited during travel, not during the hold: light it for the whole loop.
    loop_time = (2 * 2 * math.pi * LOOP_R + 2 * LOOP_R) / SPEED
    start = start - loop_time
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["node"]}" '
        f'stroke="{C["nodeStroke"]}" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["tealSoft"]}" '
        f'stroke="{C["teal"]}" stroke-width="2.5" opacity="0">'
        + window_anim("opacity", "1", "0", start, end, total) + '</rect>',
        text(cx, y + 26, "Build", 18, 700),
        f'<circle cx="{cx}" cy="{cy}" r="{LOOP_R}" fill="none" stroke="{C["line"]}" '
        f'stroke-width="1.5" stroke-dasharray="4 4"/>',
        text(cx, cy + 4, "×N", 13, 700, C["muted"]),
        text(cx, y + h - 30, "fe-build → fe-verify", 12.5, 400, C["muted"]),
        text(cx, y + h - 13, "→ browser step check", 12.5, 400, C["muted"]),
    ])


def handoff(cx, cy, key, windows, total):
    w, h = 340, 120
    x, y = cx - w / 2, cy - h / 2
    start, end = windows[key]
    out = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["node"]}" '
        f'stroke="{C["nodeStroke"]}" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{C["tealSoft"]}" '
        f'stroke="{C["teal"]}" stroke-width="2.5" opacity="0">'
        + window_anim("opacity", "1", "0", start, end, total) + '</rect>',
        text(cx, y + 28, "Handoff", 18, 700),
        text(cx, y + 47, "each draft waits for your yes", 12.5, 400, C["muted"]),
    ]
    cw, gap = 74, 8
    total_w = len(HANDOFF_CHIPS) * cw + (len(HANDOFF_CHIPS) - 1) * gap
    step = (end - start) / len(HANDOFF_CHIPS)
    for i, label in enumerate(HANDOFF_CHIPS):
        chx = cx - total_w / 2 + i * (cw + gap)
        chy = y + 68
        on = start + step * (i + 0.6)
        out += [
            f'<rect x="{chx}" y="{chy}" width="{cw}" height="30" rx="15" fill="{C["amberSoft"]}" '
            f'stroke="{C["amber"]}" stroke-width="1.2"/>',
            f'<rect x="{chx}" y="{chy}" width="{cw}" height="30" rx="15" fill="{C["teal"]}" opacity="0">'
            + window_anim("opacity", "1", "0", on, end, total, fade=0.1) + '</rect>',
            f'<g opacity="1">' + window_anim("opacity", "0", "1", on, end, total, fade=0.1)
            + text(chx + cw / 2, chy + 20, label, 13, 600, C["amber"]) + '</g>',
            f'<g opacity="0">' + window_anim("opacity", "1", "0", on, end, total, fade=0.1)
            + text(chx + cw / 2, chy + 20, label + " ✓", 13, 700, "#ffffff") + '</g>',
        ]
    return "\n".join(out)


def ticket(cx, cy, key, windows, total):
    """The ticket step: a pill above Spec, since everything after keys off it."""
    w, h = 360, 46
    x, y = cx - 30, cy - h / 2
    start, end = windows[key]
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="23" fill="{C["node"]}" '
        f'stroke="{C["nodeStroke"]}" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="23" fill="{C["tealSoft"]}" '
        f'stroke="{C["teal"]}" stroke-width="2.5" opacity="0">'
        + window_anim("opacity", "1", "0", start, end, total) + '</rect>',
        text(cx + 18, cy + 6, "Ticket", 17, 700, anchor="start"),
        text(cx + 82, cy + 5, "AR key given, found, or drafted", 12.5, 400, C["muted"], anchor="start"),
        f'<g><rect x="{x + w + 12}" y="{cy - 14}" width="196" height="28" rx="14" fill="{C["amberSoft"]}" '
        f'stroke="{C["amber"]}" stroke-width="1.2"/>'
        + text(x + w + 110, cy + 5, "you approve a new ticket", 12.5, 600, C["amber"]) + '</g>',
    ])


def done(cx, cy, key, windows, total):
    return node_box(cx, cy, 150, 70, "Done ✓", "spec Status: Done", key, windows, total)


def arrow(x1, y1, x2, y2, dashed=False, color=None, marker="arrow"):
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["line"]}" '
            f'stroke-width="2"{dash} marker-end="url(#{marker})"/>')


def main():
    d, key_points, key_times, total, windows = build_motion()
    S = {s[0]: s for s in STAGES}
    parts = []

    # Frame and titles.
    parts.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" '
                 f'fill="{C["bg"]}" stroke="{C["border"]}"/>')
    parts.append(text(40, 52, "frontend-flow — one feature, start to finish", 24, 700, anchor="start"))
    parts.append(text(40, 80, "/fe:run does one move at a time through the agent that owns it. "
                      "Amber gates wait for you; the spec file remembers where it stands.",
                      14.5, 400, C["muted"], anchor="start"))

    # Connectors between stages (drawn under the nodes).
    edges = [("spec", "g1"), ("g1", "plan"), ("plan", "g2"), ("g2", "test"), ("test", "branch"),
             ("branch", "build")]
    half = {"stage": NODE_W / 2, "gate": 32, "loop": 95, "handoff": 170, "done": 75}
    parts.append(arrow(S["ticket"][2], TICKET_Y + 23, S["spec"][2], S["spec"][3] - NODE_H / 2 - 6))
    for a, b in edges:
        _, ka, xa, ya, *_ = S[a]
        _, kb, xb, yb, *_ = S[b]
        parts.append(arrow(xa + half[ka], ya, xb - half[kb] - 6, yb))
    parts.append(arrow(S["build"][2], S["build"][3] + 75, S["verify"][2], S["verify"][3] - NODE_H / 2 - 6))
    row2 = [("verify", "audit"), ("audit", "e2e"), ("e2e", "handoff"), ("handoff", "done")]
    for a, b in row2:
        _, ka, xa, ya, *_ = S[a]
        _, kb, xb, yb, *_ = S[b]
        parts.append(arrow(xa - half[ka], ya, xb + half[kb] + 6, yb))

    # Nodes.
    for key, kind, x, y, title, agent, sub, _hold in STAGES:
        if kind == "stage":
            parts.append(node_box(x, y, NODE_W, NODE_H, title, sub, key, windows, total, agent=agent))
        elif kind == "gate":
            parts.append(gate(x, y, title, sub, key, windows, total))
        elif kind == "loop":
            parts.append(build_loop(x, y, key, windows, total))
        elif kind == "handoff":
            parts.append(handoff(x, y, key, windows, total))
        elif kind == "done":
            parts.append(done(x, y, key, windows, total))
        elif kind == "ticket":
            parts.append(ticket(x, y, key, windows, total))

    # The two stores: the spec file and the test-case library.
    lane_y = 585
    parts.append(f'<rect x="40" y="{lane_y}" width="640" height="96" rx="12" fill="{C["violetSoft"]}" '
                 f'stroke="{C["violet"]}" stroke-width="1.5"/>')
    parts.append(text(60, lane_y + 30, "The spec file — every stage writes here", 16, 700, C["violet"], anchor="start"))
    parts.append(text(60, lane_y + 55, "Flow status · UI plan · Plan · Test plan · Library changes · "
                      "Decisions · Log", 13.5, 400, C["ink"], anchor="start"))
    parts.append(text(60, lane_y + 78, "A new session reads it and resumes; the start-up hook lists "
                      "features in progress.", 13, 400, C["muted"], anchor="start"))
    parts.append(f'<rect x="720" y="{lane_y}" width="440" height="96" rx="12" fill="{C["tealSoft"]}" '
                 f'stroke="{C["teal"]}" stroke-width="1.5"/>')
    parts.append(text(740, lane_y + 30, "Test-case library — what must keep working", 16, 700, C["teal"], anchor="start"))
    parts.append(text(740, lane_y + 55, "Use cases + test cases per area · Smoke · Permission", 13.5, 400, C["ink"], anchor="start"))
    parts.append(text(740, lane_y + 78, "Milestone run reports, with the environment tested", 13, 400, C["muted"], anchor="start"))

    # Dashed links into the library: the browser run writes milestone reports; handoff
    # promotes approved cases. Every stage writes the spec file, said in its own box.
    hx, hy = S["handoff"][2], S["handoff"][3]
    ex, ey = S["e2e"][2], S["e2e"][3]
    parts.append(arrow(ex + 30, ey + NODE_H / 2, 860, lane_y - 6, dashed=True, color=C["teal"], marker="arrowTeal"))
    parts.append(arrow(hx + 120, hy + 61, 780, lane_y - 6, dashed=True, color=C["teal"], marker="arrowTeal"))
    parts.append(text(548, 540, "promotes approved cases", 12, 400, C["teal"], anchor="end"))
    parts.append(text(868, 518, "milestone report", 12, 400, C["teal"], anchor="start"))

    # Legend.
    ly = 722
    parts.append(f'<circle cx="52" cy="{ly - 5}" r="7" fill="{C["teal"]}"/>')
    parts.append(text(66, ly, "current move", 13, 400, C["muted"], anchor="start"))
    parts.append(f'<polygon points="190,{ly - 14} 199,{ly - 5} 190,{ly + 4} 181,{ly - 5}" '
                 f'fill="{C["amberSoft"]}" stroke="{C["amber"]}" stroke-width="1.5"/>')
    parts.append(text(208, ly, "waits for your approval", 13, 400, C["muted"], anchor="start"))
    parts.append(f'<line x1="390" y1="{ly - 5}" x2="430" y2="{ly - 5}" stroke="{C["teal"]}" '
                 f'stroke-width="2" stroke-dasharray="5 5"/>')
    parts.append(text(440, ly, "writes to", 13, 400, C["muted"], anchor="start"))
    parts.append(text(W - 40, ly, "Nothing is committed, pushed or posted without a yes.",
                      13, 600, C["ink"], anchor="end"))

    # The moving token (drawn last, on top).
    parts.append(
        f'<g><circle r="11" fill="{C["teal"]}" opacity="0.25"><animate attributeName="r" '
        f'values="9;15;9" dur="1.2s" repeatCount="indefinite"/></circle>'
        f'<circle r="7" fill="{C["teal"]}" stroke="#ffffff" stroke-width="2"/>'
        f'<animateMotion dur="{total:.2f}s" repeatCount="indefinite" calcMode="linear" '
        f'keyPoints="{key_points}" keyTimes="{key_times}" path="{d}"/></g>')

    defs = (
        "<defs>"
        + "".join(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>'
            for mid, col in (("arrow", C["line"]), ("arrowViolet", C["violet"]), ("arrowTeal", C["teal"])))
        + "</defs>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
           f'font-family="{FONT}" role="img" aria-labelledby="t d">'
           f'<title id="t">frontend-flow: one feature from spec to handoff</title>'
           f'<desc id="d">Ticket found or drafted (a new one needs your approval), spec, you approve, plan, you approve, test plan, branch, build loop per plan '
           f'step with gates and browser step checks, verify, audit, browser run as each role, handoff '
           f'with library, commit, PR and Jira drafts each approved, done. The spec file holds the state; '
           f'the test-case library holds the regression cases and milestone run reports.</desc>'
           + defs + "\n" + "\n".join(parts) + "\n</svg>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT.relative_to(OUT.parent.parent)} — {total:.1f}s loop, {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
