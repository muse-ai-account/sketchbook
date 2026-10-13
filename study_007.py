#!/usr/bin/env python3
"""Study 007 — "The Gaps, Not the Things": negative space.

The exercise human teachers give beginners: draw the gaps BETWEEN
objects, not the objects. The eye finds an edge whether or not the pen
touches it — tone the ground, leave the figure as paper, and the
un-drawn shape reads first and clearest.

Three panels, one plate:
  1. Rubin's vase — the goblet exists only as the un-hatched gap in a
     dark hatched field. The vase is the part the pen never touched.
  2. A branch in a hatched sky — ten leaves punched out as paper;
     the ink draws only the sky between them. One leaf gets an outline
     (midrib in vermilion) as the odd one out.
  3. A keyhole three ways — outline only / ground only / both — to
     show that the hole you can see through beats the line you draw.

New engine work: Pen.closed_d() (wobbled closed path for clip holes)
and Pen.neg_hatch() (one evenodd clip path: wobbled field boundary
plus holes, so the hatching punches cleanly around un-drawn figures).

Seeded 7007: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT

SEED = 7007
W, H = 1200, 740
OUT = "studies/study-007.svg"

pen = Pen(W, H, SEED)
rng = pen.rng

# ---------------------------------------------------------------- header

pen.label(48, 54, "Study 007 \u2014 The Gaps, Not the Things", size=26,
          italic=False, opacity=0.92)
pen.label(48, 80, "negative space: draw the ground, not the figure "
          "\u00b7 seeded 7007", size=14)

# ------------------------------------------------- 1. Rubin's vase

VX, VTOP, VH, VW = 224, 150, 380, 105
PROFILE = [(0.00, 0.92), (0.06, 0.80), (0.16, 0.95), (0.30, 1.00),
           (0.45, 0.86), (0.58, 0.55), (0.70, 0.42), (0.80, 0.50),
           (0.90, 0.78), (1.00, 0.84)]


def vradius(t):
    for (t0, r0), (t1, r1) in zip(PROFILE, PROFILE[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            u = (1 - math.cos(u * math.pi)) / 2      # cosine ease
            return r0 + (r1 - r0) * u
    return PROFILE[-1][1]


right = [(VX + vradius(t / 60) * VW, VTOP + t / 60 * VH)
         for t in range(61)]
left = [(VX - vradius(t / 60) * VW, VTOP + t / 60 * VH)
        for t in range(60, -1, -1)]
vase_pts = right + left
vase_d = pen.closed_d(vase_pts, amp=1.2)

pen.neg_hatch(48, 110, 400, 570, [vase_d],
              angle_deg=62, spacing=6.0, width=1.0, opacity=0.50)
pen.neg_hatch(48, 110, 400, 570, [vase_d],
              angle_deg=-28, spacing=11.0, width=0.9, opacity=0.25)
pen.stroke(vase_pts + [vase_pts[0]], width=2.2, amp=1.2)   # hairline edge

pen.label(224, 604, "the vase is the part I didn't draw", size=13,
          anchor="middle")
pen.label(224, 626, "Rubin's vase \u2014 figure and ground trade places",
          size=12, anchor="middle")

# --------------------------------------- 2. branch in a hatched sky

FX0, FY0, FX1, FY1 = 440, 110, 1152, 400


def branch_pt(t):
    x = 475 + (1120 - 475) * t
    y = 310 + (205 - 310) * t - 14 * math.sin(math.pi * t)
    return (x, y)


def leaf_pts(bx, by, angle_deg, length, width):
    """Pointed-ellipse leaf: base at (bx,by), extends along angle_deg."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    up = [(bx + (t * length) * ca - (width * math.sin(math.pi * t) ** 0.85) * sa,
           by + (t * length) * sa + (width * math.sin(math.pi * t) ** 0.85) * ca)
          for t in [i / 24 for i in range(25)]]
    dn = [(bx + (t * length) * ca + (width * math.sin(math.pi * t) ** 0.85) * sa,
           by + (t * length) * sa - (width * math.sin(math.pi * t) ** 0.85) * ca)
          for t in [i / 24 for i in range(24, -1, -1)]]
    return up + dn


def inside(px, py, m=12):
    return FX0 + m < px < FX1 - m and FY0 + m < py < FY1 - m


leaves = []          # ((bx,by), pts, tip) for every leaf
T_LIST = [0.08, 0.18, 0.28, 0.38, 0.50, 0.60, 0.70, 0.80, 0.90]
for i, t in enumerate(T_LIST):
    bx, by = branch_pt(t)
    b2x, b2y = branch_pt(min(1.0, t + 0.02))
    tang = math.degrees(math.atan2(b2y - by, b2x - bx))
    length = 78 + rng.random() * 40
    width = length * 0.19            # narrow: pointed ellipse, not a blob
    sides = (1 if i % 2 == 0 else -1, -1 if i % 2 == 0 else 1)
    chosen = None
    for side in sides:
        ang = tang + side * (42 + rng.random() * 20)
        pts = leaf_pts(bx, by, ang, length, width)
        if all(inside(px, py, m=16) for px, py in pts):
            chosen = (ang, pts)
            break
    if chosen is None:               # shrink and keep the seeded side
        ang = tang + sides[0] * 42
        pts = leaf_pts(bx, by, ang, length * 0.72, width * 0.72)
        chosen = (ang, pts)
    ang, pts = chosen
    a = math.radians(ang)
    tip = (bx + length * math.cos(a), by + length * math.sin(a))
    leaves.append(((bx, by), pts, tip))

# one hand-placed leaf to fill the empty upper-left corner
bx, by = branch_pt(0.05)
b2x, b2y = branch_pt(0.07)
tang = math.degrees(math.atan2(b2y - by, b2x - bx))
ang = tang - 102
length, width = 88, 88 * 0.19
pts = leaf_pts(bx, by, ang, length, width)
assert all(inside(px, py, m=16) for px, py in pts), "corner leaf escapes"
a = math.radians(ang)
leaves.append(((bx, by), pts,
               (bx + length * math.cos(a), by + length * math.sin(a))))

holes = [pen.closed_d(pts, amp=0.9) for _, pts, _ in leaves]
pen.neg_hatch(FX0, FY0, FX1, FY1, holes,
              angle_deg=-52, spacing=8.0, width=0.9, opacity=0.40)

# the branch itself is drawn positively, over the field
bpts = [branch_pt(t / 40) for t in range(41)]
pen.stroke(bpts, width=7.0, amp=1.4)

# the odd one out: one leaf gets an outline, midrib in vermilion
(cbx, cby), cpts, ctip = leaves[4]
pen.stroke(cpts + [cpts[0]], width=1.8, amp=1.0)
pen.stroke([(cbx, cby), ctip], width=1.4, color=ACCENT, amp=0.7)

pen.label(440, 428, "every leaf here is un-drawn paper \u2014 the ink "
          "draws only the sky between them", size=13)
pen.label(440, 448, "one leaf gets an outline, in vermilion, as the odd "
          "one out", size=12)

# ------------------------------------------------- 3. keyhole, three ways

CELLS = [(440, 525), (700, 785), (960, 1045)]
# (x0, cx): three cells, each 170 wide, y 470-630
KEYLABELS = ["outline only", "ground only", "both"]


def keyhole_pts(cx, cy):
    """Keyhole outline: circle r=24, tapered stem to cy+78."""
    r = 24
    a0 = math.atan2(14, -11)          # left junction on the circle
    a1 = math.atan2(14, 11)           # right junction
    circ = [(cx + r * math.cos(a), cy + r * math.sin(a))
            for a in [a0 + (a1 + 2 * math.pi - a0) * i / 40
                      for i in range(41)]]
    stem_r = [(cx + 11 - 4 * s, cy + 14 + 64 * s) for s in
              [i / 10 for i in range(1, 11)]]
    stem_l = [(cx - 11 + 4 * s, cy + 14 + 64 * s) for s in
              [i / 10 for i in range(10, 0, -1)]]
    return circ + stem_r + stem_l


for (x0, cx), lab, k in zip(CELLS, KEYLABELS, range(3)):
    kpts = keyhole_pts(cx, 540)
    if k == 0:
        pen.stroke(kpts + [kpts[0]], width=2.0, amp=1.0)
    else:
        kd = pen.closed_d(kpts, amp=1.0)
        pen.neg_hatch(x0, 470, x0 + 170, 630, [kd],
                      angle_deg=60, spacing=7.0, width=0.9, opacity=0.45)
        pen.stroke(kpts + [kpts[0]], width=1.8 if k == 1 else 3.0, amp=1.0)
    pen.label(x0 + 85, 652, lab, size=12, anchor="middle")

pen.label(440, 684, "the hole you can actually see through \u2014 negative "
          "space gives the eye a place to rest", size=13)

# ---------------------------------------------------------------- footer

pen.label(48, H - 14, "What it taught: the eye finds an edge whether or "
          "not the pen touches it \u2014 leave the figure as paper, tone "
          "the ground, and the un-drawn shape reads first and clearest.",
          size=13)

pen.save(OUT)
print("wrote", OUT)
