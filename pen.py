"""pen.py — a small hand-drawn-look SVG drawing engine.

Techniques borrowed from how human artists actually draw, and from
generative artists who fake it well:

- Lines are never plotted raw: every stroke passes through a seeded
  jitter ("boiling"), then through midpoint-anchored quadratic curves so
  the jitter reads as hand wobble, not zig-zag kinks.
- Value comes from hatching, not grey fills — clustered parallel
  strokes, exactly how pen-and-ink artists build tone.
- Line weight carries meaning: near = heavy, far = light (aerial
  perspective), emphasis = heavier.
"""

from __future__ import annotations

import math
import random

PAPER = "#f5f0e4"
INK = "#221c14"
ACCENT = "#b3412e"  # vermilion, used sparingly


def mulberry(seed: int) -> random.Random:
    """Seeded PRNG so every study is exactly reproducible."""
    return random.Random(seed)


def _jitter(pts, amp, rng) -> list[tuple[float, float]]:
    return [
        (x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp))
        for x, y in pts
    ]


def _smooth_d(pts) -> str:
    """Quadratic curve through jittered points, midpoints as anchors.

    Original points become control points, midpoints become on-curve
    anchors — this is what keeps the wobble smooth instead of kinked.
    """
    if len(pts) < 2:
        return ""
    p = list(pts)
    mids = [((p[i][0] + p[i + 1][0]) / 2, (p[i][1] + p[i + 1][1]) / 2)
            for i in range(len(p) - 1)]
    d = f"M {mids[0][0]:.1f} {mids[0][1]:.1f}"
    for i in range(1, len(mids)):
        cx, cy = p[i]
        ax, ay = mids[i]
        d += f" Q {cx:.1f} {cy:.1f} {ax:.1f} {ay:.1f}"
    # end at the true last point
    d += f" L {p[-1][0]:.1f} {p[-1][1]:.1f}"
    return d


class Pen:
    def __init__(self, w: int, h: int, seed: int):
        self.w, self.h = w, h
        self.rng = mulberry(seed)
        self.body: list[str] = []
        self.defs: list[str] = []
        self._clip_n = 0

    # -- primitives -------------------------------------------------

    def _emit(self, s: str) -> None:
        self.body.append(s)

    def stroke(self, pts, width: float = 2.0, color: str = INK,
               amp: float = 1.5, dash: str | None = None,
               opacity: float = 1.0) -> None:
        """Draw a hand-wobbled stroke through `pts` (list of x,y)."""
        if len(pts) < 2:
            return
        pts = _jitter(pts, amp, self.rng)
        d = _smooth_d(pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self._emit(
            f'<path d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{opacity}"{dash_attr}/>'
        )

    def poly(self, pts, color: str = INK, amp: float = 1.0,
             opacity: float = 1.0) -> None:
        """Wobbled closed outline, no fill (like a sketch contour)."""
        pts = _jitter(pts, amp, self.rng)
        d = _smooth_d(pts) + " Z"
        self._emit(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6" '
            f'stroke-linecap="round" opacity="{opacity}"/>'
        )

    def disc(self, cx: float, cy: float, r: float, color: str = INK,
             amp: float = 1.0, opacity: float = 1.0) -> None:
        """Wobbled circle outline."""
        pts = [(cx + r * math.cos(t), cy + r * math.sin(t))
               for t in [i * math.pi / 24 for i in range(25)]]
        self.poly(pts, color=color, amp=amp, opacity=opacity)

    # -- value via hatching ------------------------------------------

    def hatch_region(self, clip_d: str, angle_deg: float, spacing: float,
                     width: float = 1.0, color: str = INK,
                     opacity: float = 0.55, margin: float = 0.0) -> None:
        """Hatch lines clipped to the closed path `clip_d`.

        Tone comes from spacing/width, never from grey — pen-and-ink style.
        """
        self._clip_n += 1
        cid = f"clip{self._clip_n}"
        self.defs.append(f'<clipPath id="{cid}"><path d="{clip_d}"/></clipPath>')
        ang = math.radians(angle_deg)
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx  # hatch line normal
        diag = math.hypot(self.w, self.h)
        lines = []
        off = -diag
        while off < diag:
            cx, cy = self.w / 2 + nx * off, self.h / 2 + ny * off
            x0, y0 = cx - dx * diag, cy - dy * diag
            x1, y1 = cx + dx * diag, cy + dy * diag
            # small wobble on endpoints so hatches don't look ruled
            j = lambda v: v + self.rng.uniform(-1.2, 1.2)
            lines.append(
                f'<line x1="{j(x0):.1f}" y1="{j(y0):.1f}" '
                f'x2="{j(x1):.1f}" y2="{j(y1):.1f}" '
                f'stroke="{color}" stroke-width="{width}"/>'
            )
            off += spacing
        self._emit(
            f'<g clip-path="url(#{cid})" opacity="{opacity}">'
            + "".join(lines) + "</g>"
        )

    def save(self, path: str) -> None:
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}">'
            f"<defs>{''.join(self.defs)}</defs>"
            f'<rect width="{self.w}" height="{self.h}" fill="{PAPER}"/>'
            + "".join(self.body) +
            "</svg>"
        )
        with open(path, "w") as f:
            f.write(svg)
