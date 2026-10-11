"""Study 003 — Blind Contour: the lagging hand.

The exercise: draw the subject without looking at the paper. The eye crawls
along the subject's edge; the hand follows behind, lagging and wandering.
Result: a wandering line that overshoots sharp corners, rounds detail away,
and hesitates in trembling clusters where the eye lingered.

The model in pen.blind_path(): the hand draws outline[i - lag_i], where the
lag wanders slowly; sharp corners emit overshoot hooks; a few seeded spots
get hesitation clusters.

Plate: a leaf warm-up, a teapot (the classic subject), and a diagram of the
lag model itself — the eye's path vs the hand's path with rubber bands
between them. Seeded 3003 — the same plate, every time.
"""

from __future__ import annotations

import math

from pen import Pen, INK

SEED = 3003
W, H = 1200, 920


def arc(cx, cy, r, a0_deg, a1_deg, step_deg=4.0, ry=None):
    """Dense polyline along an arc (degrees, CCW positive)."""
    pts = []
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    span = a1 - a0
    nsteps = max(2, int(abs(span) / math.radians(step_deg)) + 1)
    for i in range(nsteps + 1):
        a = a0 + span * i / nsteps
        pts.append((cx + r * math.cos(a), cy + (ry or r) * math.sin(a)))
    return pts


def line(x0, y0, x1, y1, step=6.0):
    """Dense polyline between two points."""
    d = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(d / step) + 1)
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n)
            for i in range(n + 1)]


def bez(c0, c1, c2, c3, step=6.0):
    """Dense polyline along a cubic bezier."""
    x0, y0 = c0
    x1, y1 = c1
    x2, y2 = c2
    x3, y3 = c3
    approx = (math.hypot(x1 - x0, y1 - y0) + math.hypot(x2 - x1, y2 - y1)
              + math.hypot(x3 - x2, y3 - y2))
    n = max(4, int(approx / step) + 1)
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3 * x0 + 3 * mt**2 * t * x1 + 3 * mt * t**2 * x2 + t**3 * x3)
        y = (mt**3 * y0 + 3 * mt**2 * t * y1 + 3 * mt * t**2 * y2 + t**3 * y3)
        pts.append((x, y))
    return pts


def chain(*segs):
    """Join polyline segments, dropping duplicate joints."""
    out = []
    for s in segs:
        if out and s:
            s = s[1:]
        out.extend(s)
    return out


# ---------------------------------------------------------------- leaf

def leaf_outline():
    """Almond leaf, tip at right. Ordered: top edge out, tip, bottom edge back."""
    cx, cy = 300, 330
    top, bot = [], []
    n = 40
    for i in range(n + 1):
        t = i / n
        x = 150 + 300 * t
        w = 78 * (math.sin(math.pi * t) ** 0.75)
        top.append((x, cy - w))
        bot.append((x, cy + w))
    return chain(top, list(reversed(bot)))


def leaf_midrib_and_veins():
    """Midrib out-and-back, then vein spurs out-and-back (retracing doubles the line)."""
    path = []
    path += line(155, 330, 448, 330)          # midrib out
    path += list(reversed(line(150, 332, 448, 330)))  # midrib back, slight drift
    for vx in (225, 300, 375):
        up = line(vx, 330, vx + 42, 330 - 46)     # vein out
        path += up + list(reversed(up[1:]))        # vein back (retrace)
        dn = line(vx, 330, vx + 42, 330 + 46)
        path += dn + list(reversed(dn[1:]))
    return path


# -------------------------------------------------------------- teapot

def teapot_outline():
    """One unbroken eye's path: knob -> lid -> body -> travel -> spout ->
    travel -> handle. Travel strokes stay in the drawing — that's the
    blind-contour look. Kept deliberately simple: one long travel line,
    no cramped loops."""
    path = []
    # knob: single arc over the top, starting at its crown
    path += chain(arc(900, 224, 15, -90, 90))
    # lid, right side: out to the lid edge (corner)
    path += chain(bez((915, 224), (936, 244), (952, 262), (968, 284)))
    # body right: shoulder -> belly -> base right (corner)
    path += chain(bez((968, 284), (1000, 320), (1022, 355), (1022, 398)))
    path += chain(bez((1022, 398), (1022, 445), (1000, 470), (972, 488)))
    # base: across to the left (corners at both ends)
    path += chain(bez((972, 488), (930, 496), (870, 496), (828, 488)))
    # body left: up to the lid edge (corner)
    path += chain(bez((828, 488), (800, 470), (778, 445), (778, 398)))
    path += chain(bez((778, 398), (778, 355), (800, 320), (832, 284)))
    # lid left: back to the knob's left base
    path += chain(bez((832, 284), (850, 262), (866, 246), (885, 224)))
    # travel stroke to the spout tip
    path += chain(line(885, 224, 748, 252))
    # spout: sharp tip (corner), outer edge down, base curve, inner edge
    # back up to the tip — one clean loop, no fiddly lip
    path += chain(bez((748, 252), (766, 292), (788, 332), (808, 368)))
    path += chain(bez((808, 368), (818, 380), (830, 386), (844, 388)))
    path += chain(bez((844, 388), (828, 370), (796, 322), (772, 276)))
    path += chain(line(772, 276, 748, 252))
    # one long travel stroke across the top to the handle
    path += chain(line(748, 252, 1006, 310))
    # handle: outer bow down to the lower attach (corners at both)
    path += chain(bez((1006, 310), (1056, 318), (1094, 348), (1098, 394)))
    path += chain(bez((1098, 394), (1098, 426), (1050, 442), (1002, 446)))
    # inner edge back up to the top attach
    path += chain(bez((1002, 446), (1040, 434), (1054, 400), (1050, 356)))
    path += chain(bez((1050, 356), (1048, 330), (1028, 316), (1006, 310)))
    return path


# ------------------------------------------------------- lag diagram

def diagram_curve():
    """An S with one sharp corner — shows what lag does to a turn."""
    return chain(
        bez((90, 700), (200, 660), (300, 660), (380, 700)),
        line(380, 700, 470, 760),
        line(470, 760, 560, 700),   # the sharp corner at (470, 760)
        bez((560, 700), (660, 640), (760, 700), (860, 700)),
        bez((860, 700), (960, 700), (1040, 660), (1110, 700)),
    )


# ---------------------------------------------------------------- plate

def main():
    pen = Pen(W, H, SEED)

    pen.label(40, 58, "Study 003 — Blind Contour: the lagging hand", size=24)
    pen.label(40, 84, "one line, eyes on the subject, never on the paper",
              size=15, opacity=0.55)

    # -- panel A: leaf warm-up --------------------------------------
    pen.label(40, 128, "warm-up: a leaf", size=16)
    pen.blind_path(leaf_outline(), width=2.0, lag_base=5.0, lag_wander=3.5,
                   tremor=0.9, drift=2.0, overshoot=12.0, hesitate=2, seed=31)
    pen.blind_path(leaf_midrib_and_veins(), width=1.7, lag_base=4.0,
                   lag_wander=3.0, tremor=0.8, drift=1.6, overshoot=8.0,
                   hesitate=1, seed=32)

    # -- panel B: teapot --------------------------------------------
    pen.label(640, 128, "the teapot", size=16)
    pen.blind_path(teapot_outline(), width=2.1, lag_base=7.0, lag_wander=5.0,
                   tremor=1.1, drift=2.6, overshoot=12.0, corner_deg=45.0,
                   hesitate=2, hesitate_len=12, seed=33)

    # -- panel C: the lag model, diagrammed --------------------------
    pen.label(40, 648, "how the line is made", size=16)
    eye = diagram_curve()
    pen.stroke(eye, width=1.4, color=INK, opacity=0.35, amp=0.4, dash="7 5")
    pen.label(90, 690, "the eye's path — where the eye actually goes", size=13,
              opacity=0.5)
    hand = pen.blind_path([(x, y + 110) for x, y in eye], width=2.0,
                          lag_base=7.0, lag_wander=5.0, tremor=1.1, drift=2.4,
                          overshoot=16.0, hesitate=2, seed=34)
    pen.label(90, 836, "the hand's path — 7 samples behind, wandering",
              size=13, opacity=0.5)
    # rubber bands: each hand sample remembers which eye sample it drew,
    # so we can join a few of them directly.
    by_walk = {}
    for x, y, wi in hand:
        by_walk.setdefault(wi, (x, y))
    for i in range(0, len(eye), 16):
        j = int(i - 7.0)  # ~ the lag at that point
        if j in by_walk:
            x0, y0 = eye[i]
            x1, y1 = by_walk[j]
            pen.stroke([(x0, y0), (x1, y1)], width=0.7, opacity=0.25, amp=0.0)
    pen.label(40, 892, "seeded 3003 — the same plate, every time", size=13,
              opacity=0.45)

    pen.save("studies/study-003.svg")
    print("wrote studies/study-003.svg")


if __name__ == "__main__":
    main()
