#!/usr/bin/env python3
"""Study 006 — "Following the Surface": cross-contour lines.

The classic form-reading device: lines that travel *over* a surface,
bending with its curvature, tell the eye a form is round — before any
shading is drawn. No hatching this week, no value at all: form from
line alone.

Three lathe-friendly forms, one plate:
  1. sphere — latitude rings + vertical meridians, plus a "the lie"
     inset: straight lines across a disc flatten it; wrapped rings
     round it.
  2. pear — rings at even vertical steps, widening with the belly and
     crowding where the surface turns under.
  3. vase — a lathe profile whose ring spacing reads the turning:
     wide on the belly, pinched at the neck, lip and foot ellipses
     closing the form.

Rules used: a ring is an ellipse whose width is the form's width at
that height (squish 0.30-0.34 — the viewer's elevation); rings crowd
where the surface turns away from the eye; silhouettes are drawn
heavier than the lines that live on the surface.

Seeded 6006: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT

SEED = 6006
W, H = 1200, 690
OUT = "studies/study-006.svg"
SQUISH = 0.32          # ellipse squish = viewer's elevation

pen = Pen(W, H, SEED)

# ---------------------------------------------------------------- header

pen.label(48, 54, "Study 006 \u2014 Following the Surface", size=26,
          italic=False, opacity=0.92)
pen.label(48, 80, "cross-contour lines: lines that travel over a form tell "
          "the eye it's round \u2014 before any shading does \u00b7 seeded 6006",
          size=14)

CX = (200, 600, 1000)

# ---------------------------------------------------------- 1. the sphere

sx, sy, R = CX[0], 292, 150
pen.disc(sx, sy, R, width=2.8, amp=1.4)

for deg in (24, 46, 68, 90, 112, 134, 156):
    th = math.radians(deg)
    rx = R * math.sin(th)
    if rx < 10:
        continue
    pen.ellipse(sx, sy - R * math.cos(th) * 0.95, rx, rx * SQUISH,
                width=1.5, amp=1.2)

for adeg in (-60, -30, 0, 30, 60):
    a = math.radians(adeg)
    pts = [(sx + R * math.sin(math.radians(t)) * math.sin(a),
            sy - R * math.cos(math.radians(t)))
           for t in range(-80, 81, 4)]
    pen.stroke(pts, width=1.8 if adeg == 0 else 1.4, amp=1.0)

# "the lie" inset: straight lines flatten, wrapped lines round
ix, iy, ir = 118, 560, 38
pen.disc(ix, iy, ir, width=1.6, amp=1.0)
for k in (-2, -1, 0, 1, 2):
    y = iy + k * ir * 0.42
    dx = math.sqrt(max(ir * ir - (y - iy) ** 2, 1))
    pen.stroke([(ix - dx, y), (ix + dx, y)], width=1.3,
               color=ACCENT, amp=0.8)
pen.label(ix, iy + ir + 20, "straight lines flatten", size=12,
          anchor="middle")

jx = 282
pen.disc(jx, iy, ir, width=1.6, amp=1.0)
for f in (-0.55, 0.0, 0.55):
    rr = ir * math.cos(f * 1.2)
    pen.ellipse(jx, iy + ir * math.sin(f) * 0.9, rr, rr * SQUISH,
                width=1.3, amp=0.9)
pen.label(jx, iy + ir + 20, "wrapped lines round", size=12,
          anchor="middle")

pen.label(sx, 648, "sphere \u2014 rings + meridians follow the surface",
          size=13, anchor="middle")

# ------------------------------------------------------------- 2. the pear

px, py, PR = CX[1], 282, 118


def pear_point(phi):
    """Polar pear: phi=0 is straight down (the wide end)."""
    r = PR * (1 + 0.40 * math.cos(phi))
    return (px + r * math.sin(phi) * 0.94,
            py + r * math.cos(phi) * 1.18)


sil = [pear_point(2 * math.pi * i / 160) for i in range(161)]
pen.stroke(sil, width=2.8, amp=1.3)

top = py - 0.60 * PR * 1.18
pen.stroke([(px - 3, top + 4), (px + 2, top - 14), (px + 15, top - 28)],
           width=2.2, amp=0.8)                                   # the stem

pen.stroke([(px, top + 14), (px, py + 1.40 * PR * 1.18 - 16)],
           width=1.2, opacity=0.5, amp=1.0)                      # axis

for y in range(int(top) + 34, int(py + 1.40 * PR * 1.18) - 16, 26):
    xs = [x for x, yy in sil if abs(yy - y) < 2.0]
    if len(xs) < 2:
        continue
    lo, hi = min(xs), max(xs)
    rx = (hi - lo) / 2
    if rx < 8:
        continue
    pen.ellipse((lo + hi) / 2, y, rx, rx * 0.30, width=1.4, amp=1.1)

pen.label(px, 648, "pear \u2014 rings widen with the belly",
          size=13, anchor="middle")

# ------------------------------------------------------------- 3. the vase

vx, vtop, VH = CX[2], 152, 330

PROFILE = [(0.00, 26), (0.06, 40), (0.18, 78), (0.32, 96), (0.45, 92),
           (0.58, 72), (0.70, 52), (0.80, 36), (0.88, 34), (0.94, 40),
           (1.00, 46)]


def vradius(t):
    for (t0, r0), (t1, r1) in zip(PROFILE, PROFILE[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            u = (1 - math.cos(u * math.pi)) / 2      # cosine ease
            return r0 + (r1 - r0) * u
    return PROFILE[-1][1]


right = [(vx + vradius(t / 60), vtop + t / 60 * VH) for t in range(61)]
left = [(vx - vradius(t / 60), vtop + t / 60 * VH)
        for t in range(60, -1, -1)]
pen.stroke(right + left + [right[0]], width=2.8, amp=1.3)   # silhouette

for k in range(11):
    t = 0.08 + 0.88 * k / 10
    rx = vradius(t)
    pen.ellipse(vx, vtop + t * VH, rx, rx * 0.30, width=1.4, amp=1.1)

pen.ellipse(vx, vtop, 46, 46 * 0.30, width=2.2, amp=1.1)     # lip
pen.ellipse(vx, vtop - 5, 37, 37 * 0.27, width=1.1, opacity=0.6,
            amp=1.0)                                        # inner back lip
pen.ellipse(vx, vtop + VH, 26, 26 * 0.30, width=1.8, amp=1.0)  # foot

pen.label(vx, 648, "vase \u2014 ring spacing reads the lathe",
          size=13, anchor="middle")

# ---------------------------------------------------------------- footer

pen.label(48, H - 12, "What it taught: contours must bend with the surface "
          "and crowd where it turns away from the eye \u2014 draw straight "
          "lines across a form and you flatten it back into a picture.",
          size=13)

pen.save(OUT)
print("wrote", OUT)
