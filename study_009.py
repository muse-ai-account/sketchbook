#!/usr/bin/env python3
"""Study 009 — "The Hardest Subject": hands, one hand five ways.

Every drawing teacher's warning: hands are the hardest thing to draw,
and the standard fix is construction order — the mitten FIRST (a palm
is a rounded box, not five sausages glued on), the knuckle arc SECOND
(the four finger bases sit on an arc, middle highest, pinky lowest),
the finger skeletons THIRD (three segments, middle longest, each joint
a hinge), and only then the flesh, the creases, the wrinkles.

One plate, two rows:
  Construction strip — 1. the mitten / 2. knuckle arc + slot marks /
    3. the skeleton / 4. flesh + creases.
  Five hands — I. relaxed / II. open palm / III. fist / IV. pointing /
    V. the grip (side view, holding the pen that draws it).

Honest proportions baked in: finger bases on an arc; segment ratios
proximal : middle : distal ≈ 0.36 : 0.24 : 0.20 of palm length;
finger lengths middle 1.0, index 0.90, ring 0.95, pinky 0.70, thumb
0.65; the thumb opposes the fingers — it never runs parallel to them.
Curl is drawn as foreshortening in the frontal views (segments shrink
by cos(curl)), the way a curled finger genuinely reads head-on.

Seeded 9009: the same plate, every time.
"""

import math
from pen import Pen, INK, ACCENT, PAPER

SEED = 9009
W, H = 1500, 1020
OUT = "studies/study-009.svg"
GHOST = "#a79c86"  # construction ghosts and the held pen

pen = Pen(W, H, SEED)
rng = pen.rng

# ------------------------------------------------------------------ helpers

def arc_pts(cx, cy, r, a0_deg, a1_deg, n=28):
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / (n - 1)),
             cy + r * math.sin(a0 + (a1 - a0) * i / (n - 1)))
            for i in range(n)]


def quad(p0, pc, p1, n=24):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * pc[0] + t ** 2 * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * pc[1] + t ** 2 * p1[1]
        pts.append((x, y))
    return pts


def tube(pts, widths, width=2.0, color=INK, amp=1.1, opacity=1.0):
    """Tapered tube along `pts` (widths per point) — a finger, a thumb."""
    n = len(pts)
    left, right = [], []
    # direction from neighbours, normals averaged at joints
    for i in range(n):
        p_prev = pts[max(0, i - 1)]
        p_next = pts[min(n - 1, i + 1)]
        dx, dy = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
        L = math.hypot(dx, dy) + 1e-9
        nx, ny = -dy / L, dx / L
        hw = widths[i] / 2.0
        left.append((pts[i][0] + nx * hw, pts[i][1] + ny * hw))
        right.append((pts[i][0] - nx * hw, pts[i][1] - ny * hw))
    # round the tip: add a cap point past the end
    ex, ey = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
    L = math.hypot(ex, ey) + 1e-9
    cap = (pts[-1][0] + ex / L * widths[-1] * 0.45,
           pts[-1][1] + ey / L * widths[-1] * 0.45)
    outline = left + [cap] + list(reversed(right))
    pen.poly(outline, color=color, amp=amp, opacity=opacity)


def rounded_rect(cx, cy, w, h, r, n_corner=8):
    pts = []
    for (ccx, ccy, a0) in [(cx - w / 2 + r, cy - h / 2 + r, 180),
                           (cx + w / 2 - r, cy - h / 2 + r, 270),
                           (cx + w / 2 - r, cy + h / 2 - r, 0),
                           (cx - w / 2 + r, cy + h / 2 - r, 90)]:
        for i in range(n_corner + 1):
            a = math.radians(a0 + 90 * i / n_corner)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


# ------------------------------------------------------------------ the hand

# finger table: (name, x-offset as fraction of palm half-width, knuckle
# drop below the middle knuckle, length as fraction of middle, spread
# handled per-pose). x sign: negative = index side (thumb side).
FINGERS = [
    ("index",  -0.72,  6, 0.90),
    ("middle", -0.25,  0, 1.00),
    ("ring",    0.25,  6, 0.95),
    ("pinky",   0.70, 15, 0.70),
]
SEG_RATIO = (0.36, 0.24, 0.20)  # of palm length
THUMB_RATIO = (0.40, 0.32)


class Hand:
    """A frontal hand: origin at palm center-top (knuckle line middle)."""

    def __init__(self, cx, cy, pw=76.0, pl=96.0, s=1.0):
        self.cx, self.cy = cx, cy
        self.pw, self.pl = pw * s, pl * s
        self.s = s

    def knuckle(self, fx, drop):
        return (self.cx + fx * self.pw / 2, self.cy + drop * self.s)

    def palm_outline(self):
        # mitten: rounded rect, slightly wider at knuckles
        w, h = self.pw, self.pl
        return rounded_rect(self.cx, self.cy + h / 2, w, h, r=w * 0.28)

    def finger_joints(self, fx, drop, flen, spread_deg, curls):
        """Joint positions with curl drawn as foreshortening."""
        bx, by = self.knuckle(fx, drop)
        theta = math.radians(-90 + spread_deg)
        segs = [r * self.pl * flen for r in SEG_RATIO]
        pts = [(bx, by)]
        cum = 0.0
        for L, c in zip(segs, curls):
            cum += c
            eff = L * math.cos(math.radians(min(cum, 82)))
            pts.append((pts[-1][0] + eff * math.cos(theta),
                        pts[-1][1] + eff * math.sin(theta)))
        widths = [13.5 * self.s, 12.0 * self.s, 10.0 * self.s, 7.5 * self.s]
        return pts, widths

    def draw_finger(self, spec, spread_deg, curls):
        _, fx, drop, flen = spec
        pts, widths = self.finger_joints(fx, drop, flen, spread_deg, curls)
        tube(pts, widths, width=2.0)
        # knuckle wrinkle ticks at the two inner joints
        for j in (1, 2):
            x, y = pts[j]
            w = widths[j] * 0.55
            pen.stroke([(x - w, y - 2 * self.s), (x - w * 0.3, y + 1.5 * self.s),
                        (x + w * 0.4, y + 1.0 * self.s), (x + w, y - 2 * self.s)],
                       width=1.2, opacity=0.75)
        return pts

    def draw_thumb(self, angle_deg=-143, curl=(14, 22), across=False,
                   across_target=None, across_lift=-26):
        """angle measured from +x, screen coords (y down)."""
        bx = self.cx - self.pw / 2 + 8 * self.s
        by = self.cy + self.pl * 0.58
        if across and across_target is not None:
            # thumb wrapped across the front: bezier from base to target
            mid = ((bx + across_target[0]) / 2 - 6 * self.s,
                   (by + across_target[1]) / 2 + across_lift * self.s)
            pts = quad((bx, by), mid, across_target)
            widths = [15 * self.s] * (len(pts) // 2) + \
                     [11 * self.s] * (len(pts) - len(pts) // 2)
            tube(pts, widths, width=2.1)
            return pts
        th = math.radians(angle_deg)
        L1, L2 = THUMB_RATIO[0] * self.pl, THUMB_RATIO[1] * self.pl
        p0 = (bx, by)
        p1 = (p0[0] + L1 * math.cos(th), p0[1] + L1 * math.sin(th))
        th2 = th + math.radians(curl[0])
        p2 = (p1[0] + L2 * math.cos(th2), p1[1] + L2 * math.sin(th2))
        widths = [15 * self.s, 12.5 * self.s, 9.5 * self.s]
        tube([p0, p1, p2], widths, width=2.0)
        # thumb knuckle tick
        pen.stroke([(p1[0] - 6 * self.s, p1[1] - 3 * self.s),
                    (p1[0], p1[1] + 1 * self.s),
                    (p1[0] + 6 * self.s, p1[1] - 3 * self.s)],
                   width=1.2, opacity=0.75)
        return [p0, p1, p2]

    def draw_palm(self):
        pen.poly(self.palm_outline(), amp=1.2)
        # wrist hint: two short strokes below
        pen.stroke([(self.cx - self.pw * 0.32, self.cy + self.pl + 4 * self.s),
                    (self.cx - self.pw * 0.30, self.cy + self.pl + 22 * self.s)],
                   width=1.8)
        pen.stroke([(self.cx + self.pw * 0.32, self.cy + self.pl + 4 * self.s),
                    (self.cx + self.pw * 0.30, self.cy + self.pl + 22 * self.s)],
                   width=1.8)

    def draw_creases(self):
        k = self.cy
        s = self.s
        pw = self.pw
        # heart line — across the upper palm
        pen.stroke(quad((-0.34 * pw + self.cx, k + 0.30 * self.pl),
                        (self.cx, k + 0.22 * self.pl),
                        (0.36 * pw + self.cx, k + 0.34 * self.pl)),
                   width=1.4, opacity=0.8)
        # head line — mid palm
        pen.stroke(quad((-0.32 * pw + self.cx, k + 0.48 * self.pl),
                        (self.cx - 0.02 * pw, k + 0.52 * self.pl),
                        (0.34 * pw + self.cx, k + 0.46 * self.pl)),
                   width=1.4, opacity=0.8)
        # life line — big sweep around the thumb mound
        pen.stroke(quad((-0.30 * pw + self.cx, k + 0.32 * self.pl),
                        (-0.42 * pw + self.cx, k + 0.62 * self.pl),
                        (-0.10 * pw + self.cx, k + 0.94 * self.pl)),
                   width=1.4, opacity=0.8)

    def draw_fist(self):
        """Frontal fist: knuckle bumps, nail slivers, thumb wrapped."""
        self.draw_palm()
        for name, fx, drop, flen in FINGERS:
            bx, by = self.knuckle(fx, drop)
            w = 13.5 * self.s * (0.85 if name == "pinky" else 1.0)
            # knuckle bump: an arc rising above the knuckle line
            pen.stroke(arc_pts(bx, by + 2 * self.s, w * 0.62, 200, 340),
                       width=2.0)
            # nail sliver: the curled fingertip peeking over the top
            pen.stroke(arc_pts(bx, by - w * 0.55, w * 0.42, 195, 345),
                       width=1.6)
            # knuckle wrinkle
            pen.stroke([(bx - w * 0.5, by - w * 0.15),
                        (bx, by - w * 0.30), (bx + w * 0.5, by - w * 0.15)],
                       width=1.2, opacity=0.7)
        # thumb wrapped across the front
        self.draw_thumb(across=True,
                        across_target=(self.cx + self.pw * 0.28,
                                       self.cy - 14 * self.s))

    def draw(self, pose):
        """pose: 'relaxed' | 'palm' | 'fist' | 'pointing'."""
        if pose == "fist":
            self.draw_fist()
            return
        spreads = {
            "relaxed": [-8, -3, 3, 9],
            "palm": [-20, -7, 7, 19],
            "pointing": [-4, -3, 3, 9],
        }[pose]
        curls = {
            "relaxed": [(6, 12, 16)] * 4,
            "palm": [(2, 3, 4)] * 4,
            "pointing": [(2, 3, 4), (78, 88, 60), (78, 88, 60), (74, 84, 58)],
        }[pose]
        self.draw_palm()
        for spec, sp, cu in zip(FINGERS, spreads, curls):
            name = spec[0]
            if pose == "pointing" and name != "index":
                # curled fingers of the pointing hand: fist-style caps
                bx, by = self.knuckle(spec[1], spec[2])
                w = 13.5 * self.s * (0.85 if name == "pinky" else 1.0)
                pen.stroke(arc_pts(bx, by + 2 * self.s, w * 0.62, 200, 340),
                           width=2.0)
                pen.stroke(arc_pts(bx, by - w * 0.55, w * 0.42, 195, 345),
                           width=1.6)
            else:
                self.draw_finger(spec, sp, cu)
        if pose == "pointing":
            # thumb braced against the index finger's side, up the palm edge
            self.draw_thumb(across=True, across_lift=-10,
                            across_target=(self.cx - self.pw * 0.40,
                                           self.cy + 6 * self.s))
        else:
            self.draw_thumb(angle_deg=-143 if pose == "palm" else -138,
                            curl=(10, 18))
        self.draw_creases()


# ------------------------------------------------------------------ title

pen.label(W / 2, 46, "Study 009 — “The Hardest Subject”: hands",
          size=26, italic=False, opacity=0.9, anchor="middle")
pen.label(W / 2, 74,
          "the mitten first, the knuckle arc second, the fingers last — one hand five ways",
          size=15, opacity=0.6, anchor="middle")

# ------------------------------------------------------------------ construction strip

cy0 = 250
cells = [("1 · the mitten — a palm is a rounded box",
          200, None),
         ("2 · knuckle arc + slot marks",
          520, None),
         ("3 · the skeleton — three hinges per finger",
          860, None),
         ("4 · flesh + creases",
          1220, None)]

for caption, ccx, _ in cells:
    pen.label(ccx, 120, caption, size=13, opacity=0.65, anchor="middle")

# 1. mitten
h1 = Hand(200, cy0 - 40, s=0.72)
pen.poly(h1.palm_outline(), amp=1.2)
# thumb wedge: a short rounded tube, no fingers yet
bx, by = h1.cx - h1.pw / 2 + 8 * h1.s, h1.cy + h1.pl * 0.58
th = math.radians(-143)
_t0 = (bx, by)
_t1 = (bx + 20 * h1.s * math.cos(th), by + 20 * h1.s * math.sin(th))
_t2 = (bx + 34 * h1.s * math.cos(th), by + 34 * h1.s * math.sin(th))
tube([_t0, _t1, _t2], [15 * h1.s, 12 * h1.s, 9 * h1.s], width=2.0)
pen.label(200, 392, "rounded box + thumb wedge — no fingers yet",
          size=12, opacity=0.55, anchor="middle")

# 2. knuckle arc + slot marks
h2 = Hand(520, cy0 - 40, s=0.72)
pen.poly(h2.palm_outline(), amp=1.2, opacity=0.45)
kx = [h2.knuckle(fx, drop)[0] for _, fx, drop, _ in FINGERS]
ky = [h2.knuckle(fx, drop)[1] for _, fx, drop, _ in FINGERS]
# the arc through the four knuckles
pen.stroke(quad((kx[0] - 14 * h2.s, ky[0] + 10 * h2.s),
                (h2.cx, h2.cy - 12 * h2.s),
                (kx[3] + 14 * h2.s, ky[3] + 10 * h2.s)),
           width=1.6, color=ACCENT, dash="7 5")
for x, y, sp in zip(kx, ky, [-20, -7, 7, 19]):
    a = math.radians(-90 + sp)
    pen.stroke([(x, y), (x + 26 * h2.s * math.cos(a), y + 26 * h2.s * math.sin(a))],
               width=1.6, color=ACCENT, dash="7 5")
    pen.disc(x, y, 3.2, color=ACCENT, width=1.6)
pen.label(520, 392, "four bases on an arc — middle highest, pinky lowest",
          size=12, opacity=0.55, anchor="middle")

# 3. skeleton
h3 = Hand(860, cy0 - 40, s=0.72)
pen.poly(h3.palm_outline(), amp=1.2, opacity=0.45)
pen.stroke([(h3.cx, h3.cy + h3.pl), (h3.cx, h3.cy)], width=1.4, opacity=0.6)
for name, fx, drop, flen in FINGERS:
    pts, _ = h3.finger_joints(fx, drop, flen, 0, (0, 0, 0))
    pen.stroke(pts, width=1.6)
    for p in pts[1:]:
        pen.disc(p[0], p[1], 3.0, color=ACCENT, width=1.6)
pen.label(860, 386, "proximal : middle : distal ≈ 0.36 : 0.24 : 0.20 of palm",
          size=12, opacity=0.55, anchor="middle")
pen.label(860, 404, "index .90 · ring .95 · pinky .70 (× middle)",
          size=12, opacity=0.55, anchor="middle")

# 4. fleshed
h4 = Hand(1220, cy0 - 40, s=0.72)
h4.draw("relaxed")
pen.label(1220, 392, "only now: flesh, wrinkles, the three creases",
          size=12, opacity=0.55, anchor="middle")

# ------------------------------------------------------------------ five hands

row_y = 700
poses = [("I · relaxed", "relaxed", 165),
         ("II · open palm", "palm", 460),
         ("III · fist", "fist", 755),
         ("IV · pointing", "pointing", 1050)]

for caption, pose, ccx in poses:
    pen.label(ccx, 500, caption, size=14, opacity=0.7, anchor="middle")
    Hand(ccx, row_y - 60, s=1.0).draw(pose)

# V. the grip — side view, holding the pen that draws it
# (near-vertical handle: fingers wrap horizontally, thumb opposes)
gx = 1345
pen.label(gx, 500, "V · the grip — holding the pen that draws it",
          size=14, opacity=0.7, anchor="middle")

# ghosted pen, near-vertical with a slight tilt
pen_axis = quad((gx + 6, row_y + 128), (gx + 16, row_y + 4), (gx + 28, row_y - 118))
pen.stroke(pen_axis, width=9, color=GHOST, opacity=0.85)
pen.stroke(pen_axis, width=1.4, color=GHOST, dash="10 8")  # dashed core
off = 5.5
pen.stroke([(x - off, y) for x, y in pen_axis], width=1.4, color=GHOST)
pen.stroke([(x + off, y) for x, y in pen_axis], width=1.4, color=GHOST)

# palm mass behind the pen (left side)
palm_c = (gx - 56, row_y + 26)
pen.poly(rounded_rect(palm_c[0], palm_c[1], 60, 134, r=22), amp=1.4)
# heel of the hand
pen.stroke(arc_pts(palm_c[0] - 28, palm_c[1] + 44, 24, 90, 200), width=1.8)

# four fingers wrapping the handle, stacked: out of the palm, around
# the front, tips tucking back toward the handle's far side
for i in range(4):
    fy = row_y - 44 + i * 28
    start = (gx - 36, fy - 4)
    ctrl = (gx + 56, fy + 2)
    tip = (gx + 2, fy + 30)
    pts = quad(start, ctrl, tip)
    w0 = 13.5 - i * 0.9
    widths = [w0] * (len(pts) // 3) + [w0 - 2] * (len(pts) // 3) + \
             [w0 - 5] * (len(pts) - 2 * (len(pts) // 3))
    tube(pts, widths, width=2.0)
    # knuckle bump where the finger leaves the palm
    pen.stroke(arc_pts(start[0] + 4, start[1] - 2, 9, 180, 330), width=1.6)
    # one wrinkle on the wrap
    wx, wy = pts[len(pts) // 2]
    pen.stroke([(wx - 6, wy - 7), (wx, wy - 3), (wx + 6, wy - 7)],
               width=1.2, opacity=0.7)

# thumb opposing from below-front, tip pressing the handle's near edge
th_pts = quad((gx - 52, row_y + 96), (gx - 28, row_y + 30), (gx + 13, row_y - 40))
tube(th_pts, [15] * 8 + [12] * 8 + [9] * 8, width=2.1)
# thumbnail where it presses
tx, ty = th_pts[-1]
pen.stroke(arc_pts(tx - 2, ty - 3, 7, 150, 330), width=1.4)

pen.label(1485, 945, "side view: fingers wrap, thumb opposes — never parallels",
          size=12, opacity=0.55, anchor="end")

# ------------------------------------------------------------------ footer

pen.label(W / 2, 1000,
          "the rule of thumb, so to speak: fingers ≈ palm long · middle longest · thumb opposes",
          size=13, opacity=0.55, anchor="middle")

pen.save(OUT)
print("wrote", OUT)
