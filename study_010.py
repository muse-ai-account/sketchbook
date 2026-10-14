#!/usr/bin/env python3
"""Study 010 — "Three Material Languages": texture in ink.

Every drawing teacher's version of the same lesson: texture is not
detail, it is *rhythm* — stroke direction, spacing, and weight. Bark,
water, and cloth each get their own language from the same pen:

  BARK  — short choppy strokes, mostly vertical, clustered into ridges;
          crevices as dark tapering wedges; a knot as broken rings.
  WATER — long horizontal strokes in one breath, sine rhythm; ripples
          around a floating leaf; broken reflection dashes.
  CLOTH — folds read from nested shadow bands; the lit ridges carry a
          tiny weave (8px crosses) and the deep valleys take stipple.

One plate, three panels, then "the stroke alphabet": each language's
signature stroke enlarged, the way a primer shows you the letterforms.

Seeded 10010: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT, PAPER

SEED = 10010
W, H = 1500, 1020
OUT = "studies/study-010.svg"

pen = Pen(W, H, SEED)
rng = pen.rng

# ------------------------------------------------------------------ helpers

def vline(x, y0, y1, n=14):
    return [(x, y0 + (y1 - y0) * i / (n - 1)) for i in range(n)]


def hline(y, x0, x1, n=14):
    return [(x0 + (x1 - x0) * i / (n - 1), y) for i in range(n)]


def chop(cx, cy, length, angle_deg=90.0, width=2.2, opacity=0.8):
    """One short bark stroke: mostly vertical, slightly off-axis."""
    a = math.radians(angle_deg + rng.uniform(-12, 12))
    dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
    mid = (cx + rng.uniform(-3, 3), cy + rng.uniform(-3, 3))
    pen.stroke([(cx - dx, cy - dy), mid, (cx + dx, cy + dy)],
               width=width, opacity=opacity, amp=1.2)


def flow_line(y, x0, x1, amp, wavelength, phase, width=1.8, opacity=0.7,
              gap=None):
    """One long water stroke: a sine in a single breath. `gap` is an
    optional (gx0, gx1) interval to skip — a broken reflection."""
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, y + amp * math.sin(2 * math.pi * (x - x0) / wavelength + phase)))
        x += 18
    if gap is None:
        pen.stroke(pts, width=width, opacity=opacity, amp=1.0)
    else:
        gx0, gx1 = gap
        pen.stroke([p for p in pts if p[0] < gx0], width=width, opacity=opacity, amp=1.0)
        pen.stroke([p for p in pts if p[0] > gx1], width=width, opacity=opacity, amp=1.0)


def cross(cx, cy, r=4, width=1.3, opacity=0.75):
    """One weave tick: a tiny + mark."""
    pen.stroke([(cx - r, cy), (cx + r, cy)], width=width, opacity=opacity, amp=0.4)
    pen.stroke([(cx, cy - r), (cx, cy + r)], width=width, opacity=opacity, amp=0.4)


# ------------------------------------------------------------------ title

pen.label(W / 2, 62, "STUDY 010 — THREE MATERIAL LANGUAGES",
          size=26, anchor="middle")
pen.label(W / 2, 96, "texture in ink: bark, water, cloth — one pen, three languages",
          size=14, opacity=0.6, anchor="middle")

# panel dividers
for dx in (510, 990):
    pen.stroke([(dx, 140), (dx, 812)], width=1.0, opacity=0.28, amp=1.0)

# ============================================================ I. BARK ====
# A trunk segment. The language: short choppy vertical strokes.

bx = 270  # trunk center
# edges: slight taper, wobbled
pen.stroke([(bx - 88, 200), (bx - 84, 400), (bx - 78, 600), (bx - 74, 730)],
           width=2.6, amp=1.6)
pen.stroke([(bx + 88, 200), (bx + 84, 400), (bx + 78, 600), (bx + 74, 730)],
           width=2.6, amp=1.6)
# jagged cut at top
pen.stroke([(bx - 88, 200), (bx - 40, 192), (bx + 10, 204), (bx + 60, 194),
            (bx + 88, 202)], width=2.0, amp=1.2)
# root flare at the base + a ground gesture
pen.stroke([(bx - 74, 730), (bx - 95, 756), (bx - 120, 768)], width=2.2)
pen.stroke([(bx + 74, 730), (bx + 95, 756), (bx + 120, 768)], width=2.2)
for gx in (-150, -105, -60, 60, 105, 150):
    pen.stroke([(bx + gx - 18, 770), (bx + gx + 18, 768)],
               width=1.4, opacity=0.5)

# crevices first (the dark wedges the chops hang between)
crevice_x = [bx - 62, bx - 28, bx + 8, bx + 44, bx + 68]
for cx0 in crevice_x:
    y0 = rng.uniform(230, 420)
    clen = rng.uniform(110, 210)
    # tapering dark wedge: three stacked strokes, shrinking width
    for k, w in enumerate((7.5, 5.0, 3.0)):
        seg0 = y0 + k * clen / 3
        seg1 = y0 + (k + 1) * clen / 3
        pen.stroke(vline(cx0 + rng.uniform(-2, 2), seg0, seg1),
                   width=w, opacity=0.72, amp=1.0)
    # plate ticks breaking the crevice edges — bark comes in plates
    for _ in range(7):
        ty = rng.uniform(y0, y0 + clen)
        side = rng.choice((-1, 1))
        tl = rng.uniform(8, 17)
        pen.stroke([(cx0, ty), (cx0 + side * tl, ty + rng.uniform(-3, 3))],
                   width=1.2, opacity=0.6)

# the chops: ~150 short strokes, biased to the shadow (right) side
for _ in range(150):
    if rng.random() < 0.62:
        cx0 = rng.uniform(bx - 10, bx + 70)   # shadow side
    else:
        cx0 = rng.uniform(bx - 80, bx - 10)   # lit side
    cy0 = rng.uniform(205, 725)
    chop(cx0, cy0, rng.uniform(15, 45),
         width=1.4 + rng.random() * 1.8,
         opacity=0.5 + rng.random() * 0.45)

# a few horizontal plate seams
for _ in range(11):
    sy = rng.uniform(240, 700)
    sx = rng.uniform(bx - 70, bx + 40)
    pen.stroke([(sx, sy), (sx + rng.uniform(22, 52), sy + rng.uniform(-4, 4))],
               width=1.2, opacity=0.55)

# the knot: broken concentric rings
kx, ky = bx + 30, 430
for kr in (8, 14, 21, 29):
    pen.ellipse(kx, ky, kr, kr * 0.78, width=1.8, opacity=0.8,
                dash=f"{rng.uniform(8, 14):.0f} {rng.uniform(5, 9):.0f}")
pen.disc(kx, ky, 4, width=2.0)

pen.label(bx, 800, "I. BARK — chop: short strokes, off-vertical, clustered",
          size=13, anchor="middle", opacity=0.75)
pen.label(bx, 822, "crevices are dark wedges; plates break horizontally",
          size=11, anchor="middle", opacity=0.5)

# ============================================================ II. WATER ==
# A pond patch. The language: long horizontals in one breath.

# 38 flow lines, amplitude and wavelength wandering per line
for i in range(38):
    y = 212 + i * 13.8 + rng.uniform(-3, 3)
    amp = rng.uniform(4, 11)
    wl = rng.uniform(180, 320)
    ph = rng.uniform(0, 2 * math.pi)
    gap = None
    if rng.random() < 0.28:
        gx = rng.uniform(640, 860)
        gap = (gx, gx + rng.uniform(30, 60))
    flow_line(y, 590, 910, amp, wl, ph,
              width=rng.uniform(1.2, 2.4),
              opacity=rng.uniform(0.45, 0.85), gap=gap)

# the floating leaf + its ripple rings
lx, ly = 745, 470
pen.stroke([(lx - 24, ly), (lx - 8, ly - 11), (lx + 10, ly - 9),
            (lx + 24, ly), (lx + 8, ly + 10), (lx - 10, ly + 9), (lx - 24, ly)],
           width=2.0)
pen.stroke([(lx - 20, ly), (lx + 20, ly)], width=1.2, color=ACCENT)  # the vein
pen.stroke([(lx + 24, ly + 2), (lx + 34, ly + 8)], width=1.4)
for k, rr in enumerate((40, 66, 94, 128)):
    pen.ellipse(lx, ly + 3, rr, rr * 0.32, width=1.4,
                opacity=0.72 - k * 0.13)

# reflection streaks: stacks of broken dashes, lower in the panel
for sx in (640, 712, 852):
    sy = rng.uniform(596, 620)
    for k in range(rng.randint(4, 6)):
        dl = rng.uniform(16, 42)
        pen.stroke([(sx - dl / 2, sy + k * 15), (sx + dl / 2, sy + k * 15)],
                   width=rng.uniform(2.0, 3.0), opacity=0.5)

# two drops with a single ring each — small enough to read as drops, not eyes
for dx0, dy0 in ((660, 330), (830, 380)):
    pen.disc(dx0, dy0, 2.5, width=1.4)
    pen.ellipse(dx0, dy0 + 2, 12, 4.5, width=1.0, opacity=0.55)

pen.label(750, 800, "II. WATER — flow: one breath, sine rhythm, broken dashes",
          size=13, anchor="middle", opacity=0.75)
pen.label(750, 822, "amplitude 4–11px · the leaf is the only thing allowed a curve",
          size=11, anchor="middle", opacity=0.5)

# ============================================================ III. CLOTH =
# A draped swatch. The language: fold shadow bands, weave on the light.

peaks = [1125, 1230, 1335]
valleys = [1177, 1282]

def fold_curve(x, y0=225, y1=715, sway=14):
    """A vertical fold line with a gentle S sway."""
    pts = []
    n = 26
    for i in range(n):
        t = i / (n - 1)
        pts.append((x + sway * math.sin(t * math.pi * 1.2 + x),
                    y0 + (y1 - y0) * t))
    return pts

# swatch outline: wavy top, tapering sides, wavy hem
pen.stroke([(1080, 218), (1125, 208), (1177, 220), (1230, 208),
            (1282, 220), (1335, 208), (1380, 218)], width=2.4)
pen.stroke([(1080, 218), (1076, 460), (1074, 720)], width=2.4)
pen.stroke([(1380, 218), (1384, 460), (1386, 720)], width=2.4)
pen.stroke([(1074, 720), (1130, 732), (1190, 722), (1250, 734),
            (1310, 722), (1386, 730)], width=2.2)
# hem shadow ticks
for hx in range(1090, 1380, 26):
    pen.stroke([(hx, 736), (hx + 6, 748)], width=1.2, opacity=0.5)

# fold shadow bands: nested curves hugging each valley
for vx in valleys:
    for k, off in enumerate((26, 18, 11, 5)):
        for side in (-1, 1):
            pts = [(x + side * off, y) for x, y in fold_curve(vx)]
            pen.stroke(pts, width=2.2 - k * 0.35,
                       opacity=0.62 - k * 0.09, amp=1.0)
    # deepest dark: stipple in the valley throat
    clip = pen.closed_d([(x - 7, y) for x, y in fold_curve(vx)] +
                        [(x + 7, y) for x, y in reversed(fold_curve(vx))])
    pen.stipple(clip, (vx - 10, 260, vx + 10, 690), n=130, size=2.6,
                opacity=0.8)

# weave on the lit ridges: tiny crosses, paper breathing between them
for px in peaks:
    for _ in range(46):
        cx0 = px + rng.uniform(-30, 30)
        cy0 = rng.uniform(250, 690)
        cross(cx0, cy0, r=rng.uniform(3, 5), opacity=rng.uniform(0.5, 0.8))

# one fold turning over at the top-left: a small flap
pen.stroke([(1080, 218), (1108, 250), (1116, 292)], width=2.0)
pen.stroke([(1108, 250), (1140, 262), (1160, 292)], width=1.6, opacity=0.7)
for k in range(4):
    pen.stroke([(1112 + k * 9, 256 + k * 3), (1118 + k * 9, 284 + k * 3)],
               width=1.2, opacity=0.6)

pen.label(1230, 800, "III. CLOTH — weave: fold bands, 8px crosses, valley stipple",
          size=13, anchor="middle", opacity=0.75)
pen.label(1230, 822, "light is just paper left alone — ink only describes the dark",
          size=11, anchor="middle", opacity=0.5)

# ============================================ the stroke alphabet ========
pen.stroke([(90, 866), (1410, 866)], width=1.0, opacity=0.3, amp=0.8)
pen.label(W / 2, 892, "the stroke alphabet — each language's signature stroke, enlarged",
          size=13, anchor="middle", opacity=0.6)

# bark alphabet: five chops + one wedge
for i, (cx0, ln, w) in enumerate([(150, 34, 2.4), (196, 52, 3.0),
                                  (242, 28, 2.2), (288, 62, 3.4),
                                  (334, 40, 2.6)]):
    chop(cx0, 928, ln, width=w, opacity=0.9)
# one wedge: stacked dark strokes
for k, w in enumerate((7.5, 5.0, 3.0)):
    pen.stroke(vline(398, 906 + k * 14, 920 + k * 14), width=w,
               opacity=0.72, amp=0.8)
pen.label(270, 972, "chop · 15–45px, off-vertical, clustered — wedges go dark",
          size=11.5, anchor="middle", opacity=0.6)

# water alphabet: three sines + one broken pair
flow_line(906, 600, 900, 5, 300, 0.4, width=2.0, opacity=0.85)
flow_line(926, 600, 900, 9, 260, 2.1, width=2.2, opacity=0.85)
flow_line(946, 600, 900, 14, 220, 4.0, width=2.4, opacity=0.85)
pen.label(750, 972, "flow · one breath, sine rhythm 4–14px — breaks read as sparkle",
          size=11.5, anchor="middle", opacity=0.6)

# cloth alphabet: weave crosses + nested fold band + stipple patch
for gx in range(3):
    for gy in range(3):
        cross(1096 + gx * 22, 906 + gy * 20, r=4.5, opacity=0.85)
for k, off in enumerate((20, 13, 7)):
    pen.stroke([(1268 + off, 900), (1268 + off, 950)],
               width=2.2 - k * 0.4, opacity=0.75 - k * 0.12, amp=0.8)
clip = pen.closed_d([(1330, 900), (1362, 900), (1362, 952), (1330, 952)])
pen.stipple(clip, (1330, 900, 1362, 952), n=42, size=2.6, opacity=0.85)
pen.label(1230, 972, "weave · crosses on the light, bands + stipple in the dark",
          size=11.5, anchor="middle", opacity=0.6)

# ------------------------------------------------------------------ footer

pen.label(W / 2, 1002,
          "what it taught: texture is rhythm, not detail — direction + spacing + weight; the subject barely matters",
          size=13, opacity=0.55, anchor="middle")

pen.save(OUT)
print("wrote", OUT)
