#!/usr/bin/env python3
"""Study 008 — "The Edges You Don't Draw": lost and found edges.

The exercise human teachers give after contour drawing: an edge is not
a wire of constant ink around the form. Where the surface turns sharply
or drops into shadow, the edge is FOUND — bold, certain. Where the
surface glides straight or dissolves into light, the edge is LOST —
a ghost, or nothing at all — and the eye finishes the drawing itself.
Draw every edge equally and the form goes flat.

Three panels, one plate:
  I.   The same mug twice — constant-weight outline (flat) vs a contour
       whose presence follows the surface: corners found, straight
       flanks thinning, the lit flank dissolving entirely.
  II.  The gap the eye closes — a bottle whose contour is interrupted
       by five clean gaps on straight runs; the eye still reads it whole.
       A presence meter below diagrams the ink's on/off rhythm.
  III. Lost in the light — a pear lit from the upper left: the contour
       fades where the highlight washes the shoulder out, stays bold
       on the shadow side, and sparse hatching + cross-contour rings
       carry the form where the edge gives up.

New engine work: Pen.edge_life() — draws a path whose width and opacity
breathe along its length from a per-point presence value. The presence
model here is presence(t) = clamp(base + gain*turn(t) - light(t)):
turning surfaces keep their edges, lit flanks lose theirs.

Seeded 8008: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT

SEED = 8008
W, H = 1200, 760
OUT = "studies/study-008.svg"

pen = Pen(W, H, SEED)
rng = pen.rng


def turning(pts):
    """Normalized local turning 0..1 along a polyline (1 = U-turn)."""
    n = len(pts)
    out = []
    for i in range(n):
        ax, ay = pts[i][0] - pts[max(0, i - 1)][0], pts[i][1] - pts[max(0, i - 1)][1]
        bx, by = pts[min(n - 1, i + 1)][0] - pts[i][0], pts[min(n - 1, i + 1)][1] - pts[i][1]
        la, lb = math.hypot(ax, ay) + 1e-9, math.hypot(bx, by) + 1e-9
        c = max(-1.0, min(1.0, (ax * bx + ay * by) / (la * lb)))
        out.append(math.acos(c) / math.pi)
    return out


def gauss(du, w):
    return math.exp(-((du / w) ** 2))


def presence_strip(x, y, w, fn, n=30):
    """Presence meter: a row of dashes showing the ink's on/off rhythm."""
    slot = w / n
    for j in range(n):
        u = (j + 0.5) / n
        p = max(0.0, min(1.0, fn(u)))
        cx = x + j * slot + slot / 2
        if p > 0.5:
            pen.stroke([(cx - slot * 0.32, y), (cx + slot * 0.32, y)],
                       width=3.0, amp=0.4)
        elif p > 0.12:
            pen.stroke([(cx - slot * 0.28, y), (cx + slot * 0.28, y)],
                       width=1.0, amp=0.4, opacity=0.5)
        else:
            pen.stroke([(cx - slot * 0.10, y), (cx + slot * 0.10, y)],
                       width=1.6, amp=0.3, opacity=0.35)


def light_mark(x, y):
    """Vermilion light-direction marker: small disc + three rays."""
    pen.disc(x, y, 7, color=ACCENT, width=2.2, amp=0.6)
    for a in (-0.5, 0.0, 0.5):
        dx, dy = math.cos(math.pi + a), math.sin(math.pi + a)
        pen.stroke([(x + dx * 11, y + dy * 11), (x + dx * 20, y + dy * 20)],
                   width=1.8, color=ACCENT, amp=0.4)


# ---------------------------------------------------------------- header

pen.label(48, 54, "Study 008 \u2014 The Edges You Don\u2019t Draw", size=26,
          italic=False, opacity=0.92)
pen.label(48, 80, "lost and found edges: let the light dissolve what the "
          "pen doesn\u2019t need to say \u00b7 seeded 8008", size=14)

# ================================================= I. the same mug twice

def mug_body(cx, top, w, h, corner=13):
    pts = []
    half = w / 2
    for i in range(7):                      # lip edge, left -> right
        pts.append((cx - half + (i / 6) * w, top))
    for i in range(1, 7):                   # lip-right corner
        a = math.pi / 2 - (i / 6) * math.pi / 2
        pts.append((cx + half - corner + corner * math.cos(a),
                    top + corner - corner * math.sin(a)))
    for i in range(1, 11):                  # right flank
        pts.append((cx + half, top + corner + (i / 10) * (h - 2 * corner)))
    for i in range(1, 7):                   # base-right corner
        a = -(i / 6) * math.pi / 2
        pts.append((cx + half - corner + corner * math.cos(a),
                    top + h - corner + corner * math.sin(a)))
    for i in range(1, 11):                  # base edge, right -> left
        pts.append((cx + half - (i / 10) * (w - 2 * corner),
                    top + h))
    for i in range(1, 7):                   # base-left corner
        a = -math.pi / 2 - (i / 6) * math.pi / 2
        pts.append((cx - half + corner + corner * math.cos(a),
                    top + h - corner + corner * math.sin(a)))
    for i in range(1, 11):                  # left flank, up
        pts.append((cx - half, top + h - corner - (i / 10) * (h - 2 * corner)))
    return pts


def mug_handle(cx, top, w, h):
    half = w / 2
    pts = []
    ax, ay = cx + half - 2, top + 38       # upper attach
    bx, by = cx + half - 2, top + h - 38   # lower attach
    for i in range(21):
        t = i / 20
        x = ax + (bx - ax) * t + 52 * math.sin(math.pi * t) ** 1.2
        y = ay + (by - ay) * t
        pts.append((x, y))
    return pts


def mug_presence(pts, lit_u=0.93):
    turn = turning(pts)
    tnorm = max(turn) or 1.0
    pres = []
    n = len(pts)
    for i, t in enumerate(turn):
        u = i / (n - 1)
        du = min(abs(u - lit_u), 1 - abs(u - lit_u))
        p = 0.38 + 1.4 * (t / tnorm) - 0.85 * gauss(du, 0.07)
        pres.append(max(0.0, min(1.0, p)))
    return pres


pen.label(60, 128, "I. the same mug twice", size=16, italic=False, opacity=0.85)
light_mark(52, 168)

for mx, const in ((115, True), (305, False)):
    body = mug_body(mx, 190, 96, 160)
    handle = mug_handle(mx, 190, 96, 160)
    if const:
        pen.stroke(body, width=2.4, amp=1.3)
        pen.stroke(handle, width=2.2, amp=1.3)
    else:
        pen.edge_life(body, mug_presence(body), width=2.6)
        hturn = turning(handle)
        hmax = max(hturn) or 1.0
        pen.edge_life(handle,
                      [0.55 + 0.45 * t / hmax for t in hturn], width=2.4)
    pen.ellipse(mx, 190, 44, 44 * 0.28, width=1.1, opacity=0.6, amp=1.0)

pen.label(115, 392, "flat: every edge equal", size=13, anchor="middle")
pen.label(305, 392, "round: lit flanks lost", size=13, anchor="middle")
_mug_pres = mug_presence(mug_body(0, 0, 96, 160))
presence_strip(50, 414, 130, lambda u: 1.0, n=22)   # constant edge, flat meter
presence_strip(240, 414, 130,
               lambda u: _mug_pres[min(len(_mug_pres) - 1, int(u * len(_mug_pres)))],
               n=22)

# ================================================= II. the gap the eye closes

def bottle_pts(cx, top, neckw, bodyw, neckh, shh, bodyh):
    pts = []
    nl, nr = cx - neckw / 2, cx + neckw / 2
    bl, br = cx - bodyw / 2, cx + bodyw / 2
    ny = top + neckh            # neck base
    sy = ny + shh               # shoulder end
    for i in range(8):          # neck left, down
        pts.append((nl, top + (i / 7) * neckh))
    for i in range(1, 9):       # shoulder left
        t = i / 8
        e = (1 - math.cos(t * math.pi)) / 2
        pts.append((nl + (bl - nl) * e, ny + shh * e))
    for i in range(1, 12):      # body left, down
        pts.append((bl, sy + (i / 11) * bodyh))
    for i in range(1, 6):       # base-left corner
        a = math.pi - (i / 5) * math.pi / 2
        pts.append((bl + 12 + 12 * math.cos(a), sy + bodyh + 12 * math.sin(a)))
    for i in range(1, 12):      # base edge, left -> right
        pts.append((bl + 12 + (i / 11) * (bodyw - 24), sy + bodyh + 12))
    for i in range(1, 6):       # base-right corner
        a = -math.pi / 2 + (i / 5) * math.pi / 2
        pts.append((br - 12 + 12 * math.cos(a), sy + bodyh + 12 * math.sin(a)))
    for i in range(1, 12):      # body right, up
        pts.append((br, sy + bodyh - (i / 11) * bodyh))
    for i in range(1, 9):       # shoulder right
        t = i / 8
        e = (1 - math.cos(t * math.pi)) / 2
        pts.append((br + (nr - br) * e, sy - shh * e))
    for i in range(1, 8):       # neck right, up
        pts.append((nr, ny - (i / 7) * neckh))
    for i in range(1, 9):       # neck top edge, right -> left
        pts.append((nr - (i / 8) * neckw, top))
    return pts


GAP_U = [0.055, 0.35, 0.565, 0.79, 0.945]    # gaps land on straight runs


def bottle_presence(pts):
    turn = turning(pts)
    tnorm = max(turn) or 1.0
    n = len(pts)
    pres = []
    for i, t in enumerate(turn):
        u = i / (n - 1)
        gap = sum(gauss(min(abs(u - g), 1 - abs(u - g)), 0.022) for g in GAP_U)
        p = 0.28 + 1.0 * (t / tnorm) - 0.95 * gap
        pres.append(max(0.0, min(1.0, p)))
    return pres


pen.label(470, 128, "II. the gap the eye closes", size=16, italic=False,
          opacity=0.85)

bx, btop = 600, 170
bpts = bottle_pts(bx, btop, 32, 124, 80, 62, 180)
pen.edge_life(bpts, bottle_presence(bpts), width=2.6)
pen.ellipse(bx, btop, 16, 16 * 0.30, width=1.6, amp=1.0)   # mouth

pen.label(600, 552, "five clean gaps on straight runs \u2014", size=13,
          anchor="middle")
pen.label(600, 570, "the bottle is still a bottle", size=13, anchor="middle")
_btl_pres = bottle_presence(bottle_pts(0, 0, 32, 124, 80, 62, 180))
presence_strip(516, 596, 168,
               lambda u: _btl_pres[min(len(_btl_pres) - 1, int(u * len(_btl_pres)))],
               n=24)

# ================================================= III. lost in the light

def pear_r(t):
    # narrow stem, belly low, rounded base: peak near t=0.76, still
    # wide at t=1 (the walk's U-turn at the bottom rounds it)
    return (math.sin(math.pi * (0.03 + 0.62 * t)) ** 0.7) * (0.8 + 0.35 * t)


def pear_pts(cx, top, w, h):
    left = [(cx - pear_r(t) * w / 2, top + t * h) for t in [i / 45 for i in range(46)]]
    right = [(cx + pear_r(t) * w / 2, top + t * h) for t in [i / 45 for i in range(45, -1, -1)]]
    return left + right


def pear_presence(pts):
    turn = turning(pts)
    tnorm = max(turn) or 1.0
    n = len(pts)
    pres = []
    for i, t in enumerate(turn):
        u = i / (n - 1)
        du = min(abs(u - 0.11), 1 - abs(u - 0.11))
        p = 0.30 + 1.5 * (t / tnorm) - 0.80 * gauss(du, 0.07)
        pres.append(max(0.0, min(1.0, p)))
    return pres


pen.label(830, 128, "III. lost in the light", size=16, italic=False, opacity=0.85)
light_mark(822, 168)

px, ptop, pw, ph = 955, 175, 175, 300
ppts = pear_pts(px, ptop, pw, ph)
pen.edge_life(ppts, pear_presence(ppts), width=2.6)
# stem: found edge, it needs to be
pen.stroke([(px - 2, ptop + 6), (px + 8, ptop - 26), (px + 4, ptop - 40)],
           width=2.2, amp=1.0)

# shadow half carries what the contour abandoned: sparse hatch + rings
half = [(px + 8 + pear_r(t) * (pw / 2 - 8), ptop + t * ph)
        for t in [i / 45 for i in range(46)]]
half += [(px + 8, ptop + ph), (px + 8, ptop)]
pen.hatch_region(pen.closed_d(half, amp=1.0), 45, 15, width=1.0, opacity=0.4)
for tk in (0.35, 0.52, 0.69):
    pen.ellipse(px, ptop + tk * ph, pear_r(tk) * pw / 2 * 0.96,
                pear_r(tk) * pw / 2 * 0.30, width=1.1, opacity=0.22, amp=1.0)

pen.label(955, 552, "the lit shoulder dissolves \u2014 hatch and", size=13,
          anchor="middle")
pen.label(955, 570, "cross-rings hold the form instead", size=13, anchor="middle")

# ---------------------------------------------------------------- footer

pen.label(48, 668, "What it taught: a contour is not a wire around the "
          "drawing \u2014 it is a rumor of an edge, loud where the form "
          "turns", size=13)
pen.label(48, 688, "into shadow and silent where light dissolves it. The eye "
          "trusts the rumor and finishes the drawing itself; ink every "
          "edge", size=13)
pen.label(48, 708, "equally and the form goes flat.", size=13)

pen.save(OUT)
print("wrote", OUT)
