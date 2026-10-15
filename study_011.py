#!/usr/bin/env python3
"""Study 011 — "The Shrinking Street": one-point perspective.

The queue's last open item, and the most mathematical study so far —
so this one is drawn from real projection, not eyeballed. A pinhole
camera: the viewer at the origin looking down +Z, the picture plane at
focal length F. A world point (X, Y, Z) lands at

    sx = VPX + F * X / Z
    sy = VPY - F * (Y - EYE) / Z

with EYE the viewer's eye height — which is why the horizon is always
your eye level, and why every receding edge aims at the one vanishing
point. The plate has three parts:

  I.   THE STREET — a street in true one-point perspective: building
       fronts (constant-Z planes stay rectangular, the one honest
       shortcut), receding side walls, lamps, and the same 1.75 m
       walker at 3.5 / 7 / 12 / 20 m. The construction is left in:
       dashed vermilion rails from the VP through every head and
       every foot — equal heights converge on one line each.
  II.  THE DIAGONAL METHOD — the student's depth ruler. The X of a
       receding ground tile crosses at the tile's true center
       (straight lines stay straight, so diagonals stay diagonals);
       a horizontal through it is the half-depth line, because
       constant-Z stays horizontal. Repeat in the far half for
       quarters. Three equal walkers stand in the bays, shrinking
       by the honest 1/z.
  III. THE LIES — three quick ways to break it: copy-paste figures
       that don't shrink, one street with three vanishing points,
       and rails meeting off the horizon.

Seeded 10011: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT, PAPER

SEED = 10011
W, H = 1500, 1020
OUT = "studies/study-011.svg"

pen = Pen(W, H, SEED)
rng = pen.rng

# ------------------------------------------------------------------ camera

VPX, VPY = 495, 345       # the one vanishing point (main panel)
FOCAL = 400.0             # px per world-unit at the picture plane
EYE = 1.7                 # viewer eye height, world units


def proj(X, Y, Z):
    """Pinhole projection into the main panel."""
    return (VPX + FOCAL * X / Z, VPY - FOCAL * (Y - EYE) / Z)


def walker(X, Z, phase, project=proj, color=INK, opacity=1.0,
           width_scale=1.0):
    """A simple mid-stride figure at world (X, Z), built from joints
    in world space and projected — so it shrinks by the honest 1/z.
    `phase` alternates the stride; `project` lets panel II reuse it."""
    w = max(0.9, min(2.8, 2.8 * 3.5 / Z)) * width_scale
    lean = 0.06 if phase % 2 == 0 else -0.04
    s = 0.30 if phase % 2 == 0 else -0.30    # stride, toward/away
    a = -0.22 if phase % 2 == 0 else 0.22    # arms swing opposite
    P = project
    hip = P(X, 0.95, Z)
    sho = P(X + lean, 1.42, Z)
    head = P(X + lean * 1.3, 1.62, Z)
    hr = FOCAL * 0.115 / Z if project is proj else 300 * 0.115 / Z
    f1, k1 = P(X, 0, Z - s), P(X, 0.48, Z - s * 0.55)
    f2, k2 = P(X, 0, Z + s), P(X, 0.48, Z + s * 0.55)
    h1, e1 = P(X + lean, 0.98, Z + a), P(X + lean, 1.20, Z + a * 0.5)
    h2, e2 = P(X + lean, 0.98, Z - a), P(X + lean, 1.20, Z - a * 0.5)
    pen.stroke([hip, sho], width=w, color=color, opacity=opacity)
    pen.stroke([hip, k1, f1], width=w * 0.9, color=color, opacity=opacity)
    pen.stroke([hip, k2, f2], width=w * 0.9, color=color, opacity=opacity)
    pen.stroke([sho, e1, h1], width=w * 0.8, color=color, opacity=opacity)
    pen.stroke([sho, e2, h2], width=w * 0.8, color=color, opacity=opacity)
    pen.disc(head[0], head[1], hr, width=w * 0.9, color=color,
             opacity=opacity)
    return P(X, 0, Z), P(X, 1.75, Z)   # foot, head-top (for the rails)


def dashed(p, q, color=INK, width=1.2, opacity=0.55, dash="7 6"):
    pen.stroke([p, q], width=width, color=color, opacity=opacity,
               dash=dash, amp=0.6)


def rect_d(corners, amp=1.2):
    """Honest wobbled rectangle path: jittered corners joined by STRAIGHT
    lines (M/L/L/L/Z).

    (pen.poly() smooths through midpoints and closes to the first
    midpoint — lovely for blobs, but it shears one edge of anything
    rectangular. Buildings get straight edges here.)
    """
    pts = [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp))
           for x, y in corners]
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f} {y:.1f}"
    return d + " Z"


def rect_outline(corners, width=2.0, opacity=0.9, amp=1.2):
    """Wobbled rectangle outline with straight edges."""
    pen._emit(
        f'<path d="{rect_d(corners, amp)}" fill="none" stroke="{INK}" '
        f'stroke-width="{width}" stroke-linecap="round" '
        f'stroke-linejoin="round" opacity="{opacity}"/>'
    )


# ------------------------------------------------------------------ title

pen.label(W / 2, 62, "STUDY 011 — THE SHRINKING STREET",
          size=26, anchor="middle")
pen.label(W / 2, 96,
          "one-point perspective: one VP on your eye level, figures shrinking by the honest 1/z — construction left in",
          size=14, opacity=0.6, anchor="middle")

# divider between the street and the lesson column
pen.stroke([(955, 130), (955, 830)], width=1.0, opacity=0.28, amp=1.0)

# ============================================================ I. STREET ==
# Skyline first (far), street furniture later (near): honest occlusion.

# distant towers at z=45, paper-thin — aerial perspective for free
for tx in (-10, -6, -2, 3, 7):
    x0, yb = VPX + FOCAL * tx / 45, VPY + FOCAL * EYE / 45
    x1, yt = VPX + FOCAL * (tx + 3) / 45, VPY - FOCAL * (5 - EYE) / 45
    rect_outline([(x0, yb), (x1, yb), (x1, yt), (x0, yt)],
                 amp=0.8, opacity=0.30, width=1.2)

# birds: two strokes each, high and unbothered
for bx, by, s in ((250, 185, 9), (305, 205, 7), (700, 165, 8)):
    pen.stroke([(bx - s, by + 3), (bx, by), (bx + s, by + 3)],
               width=1.4, opacity=0.6)
    pen.stroke([(bx + s, by + 3), (bx + 2 * s, by + 1), (bx + 3 * s, by + 4)],
               width=1.2, opacity=0.45)

# horizon: the whole drawing's spine
pen.stroke([(60, VPY), (930, VPY)], width=1.4, opacity=0.55, amp=0.8)
pen.label(912, VPY - 10, "horizon — your eye level, always",
          size=11, opacity=0.55, anchor="end")

# street base rails (X = ±4) and curb rails (X = ±3.4), VP to frame
for Xw, op in ((4.0, 0.75), (3.4, 0.5)):
    for side in (1, -1):
        px, py = proj(side * Xw, 0, 6)
        slope = (py - VPY) / (px - VPX)
        ex = 930 if side > 0 else 60
        ey = VPY + slope * (ex - VPX)
        pen.stroke([(VPX, VPY), (ex, ey)], width=1.6, opacity=op, amp=0.8)

# center dashes: equal world gaps, shrinking on the rails
for z in (3, 5, 7, 9, 12, 16, 21, 27):
    cx, cy = proj(0, 0, z)
    hw = FOCAL * 0.12 / z
    pen.stroke([(cx - hw, cy), (cx + hw, cy)],
               width=max(1.0, 2.0 * 6 / z), opacity=0.7, amp=0.5)

# ground tooth near the foreground: short horizontals
for _ in range(16):
    z = rng.uniform(2.2, 4.5)
    cx, cy = proj(rng.uniform(-3, 3), 0, z)
    hl = rng.uniform(10, 26)
    pen.stroke([(cx - hl, cy + rng.uniform(-2, 2)),
                (cx + hl, cy + rng.uniform(-2, 2))],
               width=1.1, opacity=0.30, amp=0.6)

# ---- building fronts: constant-Z planes stay rectangular ---------------
faces = [
    # (z, x0, x1, y_top, hatch_spacing, hatch_opacity)
    (8, -8.5, -4.0, 6.5, 9, 0.32),
    (11, 4.0, 9.0, 6.5, 11, 0.28),
    (17, -9.0, -4.0, 7.0, 13, 0.22),
    (23, 4.0, 9.5, 7.0, 15, 0.18),
]
for z, x0, x1, yt, sp, hop in faces:
    bl = proj(x0, 0, z)
    br = proj(x1, 0, z)
    tr = proj(x1, yt, z)
    tl = proj(x0, yt, z)
    corners = [bl, br, tr, tl]
    rect_outline(corners, amp=1.4, opacity=0.9)
    pen.hatch_region(rect_d(corners, amp=1.4), 45, sp, width=1.0,
                     opacity=hop)
    # cornice line under the top edge
    pen.stroke([proj(x0, yt - 0.35, z), proj(x1, yt - 0.35, z)],
               width=1.4, opacity=0.6)

# windows on the two nearest faces (rectangular — the honest shortcut)
for cx, ry in ((110, 150), (200, 150), (110, 250), (200, 250),
               (110, 350), (200, 350)):
    rect_outline([(cx, ry), (cx + 52, ry), (cx + 52, ry + 48), (cx, ry + 48)],
                 width=1.5, opacity=0.75, amp=0.6)
for cx, ry in ((668, 200), (742, 200), (668, 300), (742, 300)):
    rect_outline([(cx, ry), (cx + 46, ry), (cx + 46, ry + 52), (cx, ry + 52)],
                 width=1.4, opacity=0.7, amp=0.6)

# ---- side walls: top rail + vertical edges at honest depths ------------
for side in (1, -1):
    # top rail of the wall (Y = 5.5): VP to where it leaves the frame
    tx, ty = proj(side * 4, 5.5, 4)
    slope = (ty - VPY) / (tx - VPX)
    ex = 930 if side > 0 else 60
    ey = VPY + slope * (ex - VPX)
    pen.stroke([(VPX, VPY), (ex, min(ey, 132))],
               width=1.5, opacity=0.65, amp=0.8)
    for z in (6, 10, 15, 21):
        b = proj(side * 4, 0, z)
        t = proj(side * 4, 5.5, z)
        pen.stroke([b, t], width=max(1.0, 2.4 * 8 / z), opacity=0.7)

# doorway in the right wall: a quad receding from z=7.5 to z=9
dq = [proj(4, 0, 7.5), proj(4, 3.2, 7.5), proj(4, 3.2, 9), proj(4, 0, 9)]
rect_outline(dq, amp=1.0, opacity=0.9)
pen.stroke([dq[0], dq[1]], width=1.6, opacity=0.8)
pen.stroke([dq[3], dq[2]], width=1.4, opacity=0.7)
# its top corners aim at the VP — the construction, drawn in
dashed((VPX, VPY), dq[1], color=ACCENT, width=1.0, opacity=0.6)
dashed((VPX, VPY), dq[2], color=ACCENT, width=1.0, opacity=0.6)

# ---- lamps: pole, arm over the street, lamp head -----------------------
for side in (1, -1):
    for z in (6, 12, 20):
        bx, by = proj(side * 3.1, 0, z)
        tx, ty = proj(side * 3.1, 5.2, z)
        hx, hy = proj(side * 2.2, 5.2, z)
        w = max(1.0, 2.4 * 8 / z)
        pen.stroke([(bx, by), (tx, ty)], width=w, opacity=0.85)
        pen.stroke([(tx, ty),
                    ((tx + hx) / 2, (ty + hy) / 2 - 4),
                    (hx, hy)], width=w * 0.8, opacity=0.85)
        # lamp head: a small shade, not a saucer
        pen.ellipse(hx, hy + 2, 4.5 * 8 / z + 1.2, 2.8 * 8 / z + 0.8,
                    width=w * 0.7, opacity=0.85)

# ---- the walkers: one 1.75 m figure at 3.5 / 7 / 12 / 20 m -------------
feet, heads = [], []
for i, z in enumerate((3.5, 7, 12, 20)):
    f, h = walker(-1.3, z, phase=i)
    feet.append(f)
    heads.append(h)
# the construction, left in: heads ride one rail, feet ride one rail
dashed((VPX, VPY), heads[0], color=ACCENT, width=1.2, opacity=0.65)
dashed((VPX, VPY), feet[0], color=ACCENT, width=1.2, opacity=0.65)
pen.label(300, 640, "heads ride one rail to the VP", size=11,
          opacity=0.6, anchor="middle")
pen.label(315, 700, "feet ride another — same height, same eye level",
          size=11, opacity=0.6, anchor="middle")

# the VP itself, marked the way a student would
pen.stroke([(VPX - 9, VPY), (VPX + 9, VPY)], width=1.6, color=ACCENT)
pen.stroke([(VPX, VPY - 9), (VPX, VPY + 9)], width=1.6, color=ACCENT)
pen.label(VPX + 14, VPY + 4, "VP", size=13, opacity=0.85)

pen.label(495, 786, "I. THE STREET — every receding edge aims at the one VP",
          size=13, anchor="middle", opacity=0.75)
pen.label(495, 808,
          "the same walker at 3.5 / 7 / 12 / 20 m — shrunk by 1/z, never by copying",
          size=11, anchor="middle", opacity=0.5)

# ============================================ II. DIAGONAL METHOD =======
# own little camera for the diagram
VX2, VY2 = 1215, 250
F2 = 300.0


def proj2(X, Y, Z):
    return (VX2 + F2 * X / Z, VY2 - F2 * (Y - EYE) / Z)


pen.label(1215, 130, "II. THE DIAGONAL METHOD", size=15, anchor="middle",
          opacity=0.85)
pen.label(1215, 150, "equal depths without a ruler", size=11,
          anchor="middle", opacity=0.55)

# horizon for the diagram
pen.stroke([(990, VY2), (1440, VY2)], width=1.0, opacity=0.4, amp=0.6)

# the ground tile: X in [-1.9, 1.9], Z in [2.6, 10]
X1, X2, Z1, Z2 = -1.9, 1.9, 2.6, 10
nl, nr = proj2(X1, 0, Z1), proj2(X2, 0, Z1)
fl, fr = proj2(X1, 0, Z2), proj2(X2, 0, Z2)
pen.stroke([nl, nr], width=1.8, opacity=0.85)          # near edge
pen.stroke([fl, fr], width=1.5, opacity=0.75)          # far edge
for c in (nl, nr, fl, fr):                            # rails to the VP
    dashed((1400, VY2), c, width=1.0, opacity=0.45)
# the X: diagonals cross at the tile's true center
pen.stroke([nl, fr], width=1.3, opacity=0.8)
pen.stroke([nr, fl], width=1.3, opacity=0.8)
Mx = (nl[0] + nr[0]) / 2
# intersection of the diagonals (symmetric tile: x is the middle)
t = (Mx - nl[0]) / (fr[0] - nl[0])
My = nl[1] + t * (fr[1] - nl[1])
M = (Mx, My)
pen.disc(Mx, My, 4, width=1.6, color=ACCENT)
# half-depth line: horizontal through M (constant-Z stays horizontal)
# rail x at height My, both sides
rl = (nl[0] + (1400 - nl[0]) * (nl[1] - My) / (nl[1] - VY2), My)
rr = (nr[0] + (1400 - nr[0]) * (nr[1] - My) / (nr[1] - VY2), My)
dashed(rl, rr, color=ACCENT, width=1.3, opacity=0.7)
pen.label(1330, My - 14, "half the depth, for free", size=11,
          anchor="middle", opacity=0.8)

# three equal walkers in the bays: Z = 4.4, 8.2, 10
wheads = []
for Xw, Zw, ph in ((-1.15, 4.4, 0), (-0.2, 8.2, 1), (1.3, 10, 0)):
    f, h = walker(Xw, Zw, phase=ph, project=proj2)
    wheads.append(h)
dashed((1400, VY2), wheads[0], color=ACCENT, width=1.0, opacity=0.6)

pen.label(1215, 462, "the X finds the tile's center — diagonals stay diagonals",
          size=11, anchor="middle", opacity=0.6)
pen.label(1215, 480,
          "a horizontal through it is the half-depth line; repeat in the far half for quarters",
          size=11, anchor="middle", opacity=0.6)

# ===================================================== III. THE LIES ====
pen.label(1215, 500, "III. THE LIES — three ways to break it", size=15,
          anchor="middle", opacity=0.85)

# --- lie 1: copy-paste figures -----------------------------------------
ly = 545
pen.stroke([(1000, ly), (1430, ly)], width=1.0, opacity=0.4, amp=0.6)
dashed((1215, ly), (1000, 600), width=0.9, opacity=0.4)
dashed((1215, ly), (1430, 600), width=0.9, opacity=0.4)


def mini_walker(cx, base, h):
    w = 1.6
    pen.stroke([(cx, base), (cx, base - h * 0.55)], width=w)
    pen.stroke([(cx, base), (cx - h * 0.10, base - h * 0.28),
                (cx - h * 0.16, base)], width=w * 0.9)
    pen.stroke([(cx, base), (cx + h * 0.10, base - h * 0.28),
                (cx + h * 0.14, base)], width=w * 0.9)
    pen.stroke([(cx, base - h * 0.55), (cx - h * 0.12, base - h * 0.32)],
               width=w * 0.8)
    pen.stroke([(cx, base - h * 0.55), (cx + h * 0.12, base - h * 0.38)],
               width=w * 0.8)
    pen.disc(cx, base - h * 0.72, h * 0.09, width=w * 0.9)


for i, (cx, base) in enumerate(((1080, 592), (1180, 578), (1280, 566))):
    mini_walker(cx, base, 52)   # identical — the lie
pen.label(1215, 622, "LIE 1 — copy-paste figures: same size at every depth. depth dies.",
          size=11, anchor="middle", opacity=0.6)

# --- lie 2: three vanishing points --------------------------------------
ly = 668
pen.stroke([(1000, ly), (1430, ly)], width=1.0, opacity=0.4, amp=0.6)
vps = (1100, 1215, 1330)
for vx in vps:
    pen.disc(vx, ly, 3, width=1.2, color=ACCENT, opacity=0.8)
pen.stroke([(1000, 712), (1100, ly)], width=1.2, opacity=0.6)
pen.stroke([(1215, 712), (1215, ly)], width=1.2, opacity=0.6)
pen.stroke([(1430, 712), (1330, ly)], width=1.2, opacity=0.6)
pen.label(1215, 730, "LIE 2 — one street, three vanishing points. pick one.",
          size=11, anchor="middle", opacity=0.6)

# --- lie 3: rails meeting off the horizon --------------------------------
pen.stroke([(990, 752), (1440, 776)], width=1.0, opacity=0.4, amp=0.6)
pen.stroke([(1010, 812), (1215, 738)], width=1.2, opacity=0.6)
pen.stroke([(1420, 812), (1215, 738)], width=1.2, opacity=0.6)
pen.disc(1215, 738, 3.5, width=1.4, color=ACCENT)
pen.label(1215, 800, "rails meet here — but the horizon is down there",
          size=10.5, anchor="middle", opacity=0.6)
pen.label(1215, 838, "LIE 3 — rails must meet ON the horizon: it is your eye level.",
          size=11, anchor="middle", opacity=0.6)

# ------------------------------------------------------------------ footer

pen.label(W / 2, 940,
          "what it taught: one vanishing point on your eye level rules every receding edge — equal steps shrink by the honest 1/z, never by copying",
          size=13, opacity=0.55, anchor="middle")
pen.label(W / 2, 962,
          "leave the construction in — the X, the rails, the VP. students are told to, and it reads as confidence",
          size=13, opacity=0.55, anchor="middle")

pen.save(OUT)
print("wrote", OUT)
