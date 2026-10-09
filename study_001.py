"""Study 001 — "First Lines" (hills at dusk).

The first weekly study. Applies the drawing fundamentals from
notes/fundamentals.md in order:

1. GESTURE — one flowing ridge line carries the whole composition.
2. CONSTRUCTION — big shapes first (three hill masses), then the tree,
   then detail ticks.
3. LINE WEIGHT — far = light (1.2), mid = medium (2.0), near = heavy (2.8).
4. VALUE — tone from hatching only, denser on the near dark slope.
5. COMPOSITION — sun on the upper-left third, tree on the right third,
   a winding path as the leading line into the scene.

Seeded (1001): the drawing is exactly reproducible, like a plate.
"""

import math

from pen import Pen, INK, ACCENT, PAPER

SEED = 1001
W, H = 800, 1000


def ridge_pts(x0, x1, ybase, peaks, n=64):
    """Flowing hill contour: base line lifted by gaussian peaks."""
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = ybase
        for px, ph, pw in peaks:
            y -= ph * math.exp(-((x - px) ** 2) / (2 * pw * pw))
        pts.append((x, y))
    return pts


def main():
    pen = Pen(W, H, SEED)

    # --- sky ----------------------------------------------------------------
    # Sun on the upper-left third, vermilion accent: one disc, one halo arc.
    pen.disc(265, 250, 55, color=ACCENT, amp=2.0, opacity=0.9)
    arc = [(265 + 92 * math.cos(t), 250 + 92 * math.sin(t))
           for t in [-2.8 + 2.5 * i / 20 for i in range(21)]]
    pen.stroke(arc, width=1.4, color=ACCENT, amp=2.0, opacity=0.5)

    # birds: two-stroke "m" curves, high and small
    for bx, by, s in [(470, 210, 1.0), (540, 165, 0.8), (620, 240, 0.65),
                      (700, 300, 0.5), (380, 280, 0.55)]:
        pen.stroke([(bx - 16 * s, by), (bx - 4 * s, by - 10 * s),
                    (bx + 4 * s, by - 10 * s), (bx + 16 * s, by)],
                   width=1.6, amp=0.8)

    # --- hills: far to near -----------------------------------------------
    far = ridge_pts(-20, 820, 600, [(180, 60, 90), (430, 90, 120),
                                    (700, 55, 80)])
    pen.stroke(far, width=1.2, amp=1.2, opacity=0.75)  # aerial perspective

    mid = ridge_pts(-20, 820, 730, [(150, 70, 80), (560, 130, 110),
                                    (760, 60, 70)])
    pen.stroke(mid, width=2.0, amp=1.6)

    near = ridge_pts(-20, 820, 880, [(260, 90, 110), (640, 120, 130)])
    pen.stroke(near, width=2.8, amp=2.0)

    # value: hatch the valley between mid and near ridges (mid-tone)...
    d_mid = _closed_between(pen, mid, near)
    pen.hatch_region(d_mid, angle_deg=55, spacing=15, width=1.0,
                     opacity=0.35)
    # ...and the near hill's dark slope (darker tone, tighter hatch)
    d_near = _closed_below(pen, near, H)
    pen.hatch_region(d_near, angle_deg=55, spacing=9, width=1.3,
                     opacity=0.6)
    # a second cross-hatch pass on the darkest part for depth
    pen.hatch_region(d_near, angle_deg=-35, spacing=18, width=0.9,
                     opacity=0.35)

    # --- trees -------------------------------------------------------------
    rng = pen.rng

    def tree(tx, ty, scale=1.0, foliage_n=34):
        pen.stroke([(tx - 7 * scale, ty + 60 * scale),
                    (tx - 3 * scale, ty + 10 * scale),
                    (tx, ty - 40 * scale)],
                   width=4.5 * scale, amp=1.2)
        pen.stroke([(tx + 7 * scale, ty + 60 * scale),
                    (tx + 3 * scale, ty + 10 * scale),
                    (tx + 1 * scale, ty - 40 * scale)],
                   width=3.0 * scale, amp=1.2)
        # branches: gestural flicks upward-outward; remember the tips
        tips = []
        for _ in range(7):
            a = rng.uniform(-1.2, 1.2)
            bx0 = tx + rng.uniform(-4, 4) * scale
            by0 = ty - rng.uniform(20, 45) * scale
            tip = (bx0 + a * 55 * scale, by0 - rng.uniform(35, 60) * scale)
            tips.append(tip)
            pen.stroke([(bx0, by0),
                        ((bx0 + tip[0]) / 2, (by0 + tip[1]) / 2 - 6 * scale),
                        tip],
                       width=1.8 * scale, amp=1.0)
        # foliage: small dense scribble loops clustered around branch tips
        for _ in range(foliage_n):
            cx0, cy0 = tips[rng.randrange(len(tips))]
            cx = cx0 + rng.uniform(-18, 18) * scale
            cy = cy0 + rng.uniform(-14, 14) * scale
            r = rng.uniform(5, 10) * scale
            loop = [(cx + r * math.cos(t) + rng.uniform(-2, 2),
                     cy + r * 0.7 * math.sin(t) + rng.uniform(-2, 2))
                    for t in [i * math.pi / 6 for i in range(13)]]
            pen.stroke(loop, width=1.1 * scale, amp=0.6, opacity=0.8)

    tree(560, 640, scale=1.0)          # hero tree, right third, on mid ridge
    tree(180, 530, scale=0.45, foliage_n=10)  # distant sapling, far ridge

    # --- leading line: winding path from foreground to the mid ridge -------
    path = [(120, 985), (170, 930), (150, 880), (210, 830),
            (260, 790), (330, 760), (420, 740)]
    pen.stroke(path, width=2.2, amp=1.4, opacity=0.8, dash="14 10")

    # --- foreground grass ticks --------------------------------------------
    for _ in range(90):
        gx = rng.uniform(0, W)
        gy = rng.uniform(880, 995)
        lean = rng.uniform(-8, 8)
        hgt = rng.uniform(10, 30)
        pen.stroke([(gx, gy), (gx + lean * 0.4, gy - hgt * 0.6),
                    (gx + lean, gy - hgt)],
                   width=1.3, amp=0.7, opacity=0.75)

    pen.save("studies/study-001.svg")
    print("wrote studies/study-001.svg")


def _closed_between(pen, upper, lower):
    """Clip path: band between two polylines (upper forward, lower back)."""
    d = _smooth(upper)
    d += " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in reversed(lower))
    return d + " Z"


def _closed_below(pen, ridge, bottom):
    d = _smooth(ridge)
    x1 = ridge[-1][0]
    x0 = ridge[0][0]
    return d + f" L {x1:.1f} {bottom} L {x0:.1f} {bottom} Z"


def _smooth(pts):
    p = list(pts)
    mids = [((p[i][0] + p[i + 1][0]) / 2, (p[i][1] + p[i + 1][1]) / 2)
            for i in range(len(p) - 1)]
    d = f"M {mids[0][0]:.1f} {mids[0][1]:.1f}"
    for i in range(1, len(mids)):
        d += (f" Q {p[i][0]:.1f} {p[i][1]:.1f} "
              f"{mids[i][0]:.1f} {mids[i][1]:.1f}")
    return d + f" L {p[-1][0]:.1f} {p[-1][1]:.1f}"


if __name__ == "__main__":
    main()
