"""Study 002 — "Thirty-Second Figures" (gesture study plate).

Human drawing classes teach gesture before anatomy: 30-second poses where
you capture the line of action, hang a bean torso on it, and let the limbs
follow. This plate is six such poses plus a three-panel construction strip
showing how one of them is built.

From notes/fundamentals.md this tests the queued idea:
"Figure gesture: line of action + bean torso, 30-second poses."

New engine work in pen.py for this study: `Pen.ellipse()` (the bean torso)
and `Pen.label()` (plate captions).

Seeded (2002): the drawing is exactly reproducible, like a plate.
"""

import math

from pen import Pen, INK

SEED = 2002
W, H = 800, 1080

# ---------------------------------------------------------------- poses ---
# Unit space: figure height = 1.0, y grows downward. Each limb is a jointed
# polyline; `far` limbs are drawn first, lighter — aerial perspective on
# the body itself.

POSES = {
    "arabesque": dict(
        head=(0.60, 0.10), head_r=0.062,
        gesture=[(0.60, 0.06), (0.585, 0.14), (0.55, 0.22), (0.50, 0.34),
                 (0.46, 0.48), (0.48, 0.62), (0.50, 0.76), (0.52, 1.00)],
        sho=(0.56, 0.21), hip=(0.46, 0.48), ground=1.00,
        limbs=[
            ([(0.46, 0.48), (0.50, 0.72), (0.52, 1.00)], False),  # standing leg
            ([(0.46, 0.48), (0.30, 0.44), (0.10, 0.30)], False),  # extended leg
            ([(0.56, 0.21), (0.70, 0.28), (0.84, 0.24)], False),  # front arm
            ([(0.56, 0.21), (0.44, 0.30), (0.32, 0.38)], True),   # back arm
        ]),
    "runner": dict(
        head=(0.55, 0.12), head_r=0.062,
        gesture=[(0.55, 0.07), (0.53, 0.16), (0.49, 0.24), (0.45, 0.36),
                 (0.42, 0.50), (0.50, 0.62), (0.56, 0.78), (0.55, 0.95)],
        sho=(0.50, 0.23), hip=(0.42, 0.50), ground=0.95,
        limbs=[
            ([(0.42, 0.50), (0.60, 0.62), (0.55, 0.95)], False),
            ([(0.42, 0.50), (0.28, 0.68), (0.14, 0.92)], True),
            ([(0.50, 0.23), (0.64, 0.30), (0.56, 0.18)], False),
            ([(0.50, 0.23), (0.38, 0.32), (0.30, 0.44)], True),
        ]),
    "thinker": dict(
        head=(0.55, 0.28), head_r=0.062,
        gesture=[(0.55, 0.23), (0.53, 0.32), (0.50, 0.40), (0.46, 0.50),
                 (0.42, 0.62)],
        sho=(0.50, 0.39), hip=(0.42, 0.62), ground=1.00,
        limbs=[
            ([(0.42, 0.62), (0.60, 0.66), (0.58, 1.00)], False),
            ([(0.42, 0.62), (0.50, 0.68), (0.44, 1.00)], True),
            ([(0.50, 0.39), (0.60, 0.52), (0.55, 0.35)], False),  # hand to chin
            ([(0.50, 0.39), (0.42, 0.54), (0.46, 0.70)], True),
        ]),
    "reaching": dict(
        head=(0.50, 0.12), head_r=0.062,
        gesture=[(0.51, 0.02), (0.50, 0.10), (0.50, 0.18), (0.50, 0.32),
                 (0.50, 0.44), (0.50, 0.52), (0.48, 0.68), (0.46, 0.84),
                 (0.45, 1.00)],
        sho=(0.50, 0.21), hip=(0.50, 0.52), ground=1.00,
        limbs=[
            ([(0.50, 0.52), (0.45, 0.76), (0.43, 1.00)], False),
            ([(0.50, 0.52), (0.55, 0.76), (0.57, 1.00)], True),
            ([(0.50, 0.21), (0.43, 0.08), (0.39, -0.04)], False),
            ([(0.50, 0.21), (0.57, 0.08), (0.62, -0.02)], True),
        ]),
    "crouch": dict(
        head=(0.54, 0.34), head_r=0.062,
        gesture=[(0.54, 0.29), (0.52, 0.38), (0.49, 0.48), (0.46, 0.58),
                 (0.45, 0.68)],
        sho=(0.49, 0.47), hip=(0.45, 0.68), ground=0.98,
        limbs=[
            ([(0.45, 0.68), (0.62, 0.72), (0.56, 0.98)], False),
            ([(0.45, 0.68), (0.36, 0.74), (0.34, 0.98)], True),
            ([(0.49, 0.47), (0.60, 0.60), (0.58, 0.74)], False),
            ([(0.49, 0.47), (0.38, 0.62), (0.40, 0.76)], True),
        ]),
    "leap": dict(
        head=(0.50, 0.14), head_r=0.062,
        gesture=[(0.14, 0.64), (0.30, 0.58), (0.42, 0.54), (0.50, 0.44),
                 (0.50, 0.30), (0.50, 0.18), (0.50, 0.09), (0.62, 0.10),
                 (0.82, 0.22)],
        sho=(0.50, 0.25), hip=(0.50, 0.52), ground=None,
        limbs=[
            ([(0.50, 0.52), (0.30, 0.60), (0.12, 0.66)], False),
            ([(0.50, 0.52), (0.70, 0.58), (0.88, 0.64)], True),
            ([(0.50, 0.25), (0.32, 0.28), (0.16, 0.22)], False),
            ([(0.50, 0.25), (0.68, 0.28), (0.84, 0.24)], True),
        ]),
}


def _bean(pen, sho, hip, dashed=False):
    """The bean torso: an ellipse tilted along the shoulder→hip axis."""
    mx, my = (sho[0] + hip[0]) / 2, (sho[1] + hip[1]) / 2
    dx, dy = sho[0] - hip[0], sho[1] - hip[1]
    dist = math.hypot(dx, dy)
    ry, rx = dist * 0.62, dist * 0.62 * 0.58
    rot = math.degrees(math.atan2(dx, dy))
    if dashed:
        pen.ellipse(mx, my, rx, ry, rot, dash="7 6", opacity=0.4)
        return None
    d = pen.ellipse(mx, my, rx, ry, rot, width=1.8)
    # gentle tone inside the bean, from hatching only
    pen.hatch_region(d, angle_deg=55, spacing=24, width=0.9, opacity=0.30)
    return d


def _limb(pen, pts, faint=False):
    """A jointed limb as one flowing stroke; muscle mass suggested by a
    thicker wash over the proximal segment — an inker's shortcut."""
    w = 2.6 if not faint else 1.8
    op = 0.95 if not faint else 0.45
    pen.stroke(pts, width=w, amp=0.9, opacity=op)
    if not faint and len(pts) >= 2:
        mid = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        pen.stroke([pts[0], mid], width=w + 1.6, amp=0.9, opacity=0.5)


def figure(pen, ox, oy, h, pose, mode="final"):
    """Draw one gesture figure. Modes: gesture / construct / final."""
    P = lambda p: (ox + p[0] * h, oy + p[1] * h)
    head = P(pose["head"])
    hr = pose["head_r"] * h
    sho, hip = P(pose["sho"]), P(pose["hip"])
    # the gesture begins at the head itself — one continuous line of action
    gpts = [head] + [P(p) for p in pose["gesture"][1:]]

    if mode in ("gesture", "construct"):
        con = dict(color=INK, opacity=0.38, dash="7 6")
        pen.stroke(gpts, width=2.0, amp=1.2, **con)
        pen.disc(head[0], head[1], hr, amp=1.0, opacity=0.38)
        if mode == "construct":
            _bean(pen, sho, hip, dashed=True)
            for pts, _far in pose["limbs"]:
                pen.stroke([P(p) for p in pts], width=1.2, amp=0.8, **con)
        return

    # final: far limbs first (lighter = farther), then the energy line,
    # then torso, head, near limbs — big to small, per the fundamentals.
    for pts, far in pose["limbs"]:
        if far:
            _limb(pen, [P(p) for p in pts], faint=True)
    pen.stroke(gpts, width=2.2, amp=1.2, opacity=0.9)  # the gesture stays
    _bean(pen, sho, hip)
    pen.disc(head[0], head[1], hr, amp=1.2, width=2.0)
    for pts, far in pose["limbs"]:
        if not far:
            _limb(pen, [P(p) for p in pts])
    if pose.get("ground") is not None:
        gy = oy + pose["ground"] * h
        pen.stroke([(ox + 0.15 * h, gy), (ox + 0.85 * h, gy)],
                   width=1.6, amp=1.0, opacity=0.6)


def main():
    pen = Pen(W, H, SEED)

    pen.label(48, 62, "Study 002 \u2014 Thirty-Second Figures", size=26,
              opacity=0.92)
    pen.label(48, 88, "line of action \u00b7 bean torso \u00b7 six poses, one plate",
              size=13, opacity=0.55)

    # six poses, two columns by three rows
    order = ["arabesque", "runner", "thinker", "reaching", "crouch", "leap"]
    for i, name in enumerate(order):
        ox = 70 + (i % 2) * 370
        oy = 120 + (i // 2) * 250
        figure(pen, ox, oy, 230, POSES[name])

    # construction strip: how the "reaching" pose is built, in three steps
    pen.label(48, 912, "how a figure is built \u2014 the reaching pose",
              size=13, opacity=0.55)
    strip = [("gesture", 60), ("construct", 290), ("final", 520)]
    captions = ["1 \u00b7 the line of action", "2 \u00b7 hang the bean on it",
                "3 \u00b7 limbs follow the torso"]
    for (mode, sx), cap in zip(strip, captions):
        figure(pen, sx, 928, 120, POSES["reaching"], mode=mode)
        pen.label(sx, 1070, cap, size=12, opacity=0.6)

    pen.save("studies/study-002.svg")
    print("wrote studies/study-002.svg")


if __name__ == "__main__":
    main()
