"""Study 004 — Four Keys of Light.

The exercise: draw the same sphere under four different lights — morning,
overcast, dusk, candlelight — using nothing but ink. No grey, no fills:
tone is hatch density, and the deepest tone earns a cross-hatch pass.

The model: light comes from the upper-left. A highlight ellipse sits
upper-left of center; shadow mass builds lower-right in stacked passes —
base hatch over the whole disc, then a tighter pass clipped to a shadow
ellipse, then the deepest pass (with a cross-hatch) clipped tighter still.
Each key changes the spacing of the passes and the size of the highlight,
and the same ball reads as four times of day.

Plate: four shaded spheres with cast shadows on a shared ground line, and
a hatch-density legend strip at the bottom — paper, light, mid, dark,
black. Seeded 4004 — the same plate, every time.
"""

from __future__ import annotations

import math

from pen import Pen, INK, PAPER

SEED = 4004
W, H = 1200, 920

LIGHT = (-0.55, -0.83)  # upper-left, unit-ish


def paper_ellipse(pen: Pen, cx: float, cy: float, rx: float, ry: float) -> None:
    """A paper-colored ellipse — the masked highlight, drawn over hatches."""
    pen._emit(
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{PAPER}"/>'
    )


def shade_sphere(pen: Pen, cx: float, cy: float, r: float,
                 base: float, shadow: float, deep: float | None,
                 hl_rx: float, cross_deep: bool = False,
                 terminator: float = 1.0) -> None:
    """Shade one sphere. `terminator` scales the shadow ellipses (smaller =
    sharper terminator, for candlelight)."""
    # shadow passes first (hatches), outline drawn first as their clip,
    # highlight masked on top last
    d = pen.ellipse(cx, cy, r, r, width=2.4, amp=1.2)
    pen.hatch_region(d, 45.0, base, width=1.0, opacity=0.5)
    sx, sy = cx + 28 * terminator, cy + 28 * terminator
    sr = 88 * terminator
    sd = pen.ellipse(sx, sy, sr, sr, width=0)  # clip only, no visible stroke
    pen.hatch_region(sd, 45.0, shadow, width=1.2, opacity=0.55)
    if deep is not None:
        dx, dy = cx + 48 * terminator, cy + 48 * terminator
        dr = 62 * terminator
        dd = pen.ellipse(dx, dy, dr, dr, width=0)
        pen.hatch_region(dd, 45.0, deep, width=1.3, opacity=0.6)
        cross_ang = 90.0 if cross_deep else -30.0
        pen.hatch_region(dd, cross_ang, deep, width=1.1, opacity=0.5)
    # crisp outline already drawn above (it doubled as the hatch clip);
    # now the masked highlight, up and to the left (light is upper-left)
    paper_ellipse(pen, cx + LIGHT[0] * 70, cy + LIGHT[1] * 52,
                  hl_rx, hl_rx * 0.75)


def cast_shadow(pen: Pen, cx: float, gy: float, spacing: float) -> None:
    d = pen.ellipse(cx + 45, gy, 85, 13, width=0)
    pen.hatch_region(d, 0.0, spacing, width=1.0, opacity=0.5)
    pen.ellipse(cx + 45, gy, 85, 13, width=1.2, amp=1.0)


def rect_pts(x, y, w, h, per_edge: int = 8):
    """Rectangle perimeter with subdivided edges, so the smoothing keeps
    the sides fairly straight instead of melting the corners."""
    pts = []
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    for i in range(4):
        x0, y0 = corners[i]
        x1, y1 = corners[(i + 1) % 4]
        for s in range(per_edge):
            f = s / per_edge
            pts.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    return pts


def main() -> None:
    pen = Pen(W, H, SEED)

    pen.label(60, 70, "Study 004 — Four Keys of Light", size=26,
              italic=False, opacity=0.9)
    pen.label(60, 100, "the same sphere at four times of day — tone from "
              "hatch density alone, no grey, no fills", size=15)
    pen.label(60, 128, "light: upper left", size=13, opacity=0.5)

    spheres = [
        # (cx, base, shadow, deep, highlight rx, caption, cast spacing)
        (170, 15.0, 11.0, None, 40, "high key — morning", 10.0),
        (450, 11.0, 8.0, 6.0, 30, "mid key — overcast", 8.0),
        (730, 8.0, 6.0, 4.5, 24, "low key — dusk", 6.5),
    ]
    cy, r = 380, 115
    ground_y = cy + r + 24

    # shared ground line
    pen.stroke([(60, ground_y + 14), (1140, ground_y + 14)],
               width=1.2, amp=1.0, opacity=0.45)

    for cx, base, sh, deep, hl, cap, cs in spheres:
        shade_sphere(pen, cx, cy, r, base, sh, deep, hl)
        cast_shadow(pen, cx, ground_y, cs)
        pen.label(cx, cy + r + 62, cap, size=14, anchor="middle")

    # chiaroscuro — sharper terminator, smallest highlight, boldest shadow
    cx = 1010
    shade_sphere(pen, cx, cy, r, 10.0, 5.5, 4.0, 20,
                 cross_deep=True, terminator=0.82)
    cast_shadow(pen, cx, ground_y, 5.0)
    pen.label(cx, cy + r + 62, "chiaroscuro — candlelight", size=14,
              anchor="middle")

    # -- legend strip --------------------------------------------------
    pen.label(60, 660, "tone is density: no grey, only ink", size=16,
              italic=False, opacity=0.85)
    swatches = [
        ("paper", None, None),
        ("light", 16.0, None),
        ("mid", 11.0, None),
        ("dark", 7.0, None),
        ("black — cross", 5.0, 90.0),
    ]
    x = 60
    for name, sp, cross in swatches:
        # jitter-free clip rect; wobbled outline drawn separately
        clip = (f"M {x} 686 L {x + 180} 686 L {x + 180} 778 L {x} 778 Z")
        pen.poly(rect_pts(x, 686, 180, 92), amp=0.7)
        if sp is not None:
            pen.hatch_region(clip, 45.0, sp, width=1.1, opacity=0.6)
            if cross is not None:
                pen.hatch_region(clip, cross, sp, width=1.0, opacity=0.55)
        pen.label(x, 806, name, size=13, anchor="start")
        x += 210

    pen.label(60, 858, "what it taught: the same ball reads as four times "
              "of day from hatch density alone;", size=13, opacity=0.6)
    pen.label(60, 880, "a crisp highlight survives any amount of shadow if "
              "it is masked first; cross-hatch only the deepest tone, or "
              "everything reads muddy.", size=13, opacity=0.6)

    pen.save("studies/study-004.svg")
    print("wrote studies/study-004.svg")


if __name__ == "__main__":
    main()
