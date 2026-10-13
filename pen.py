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
             amp: float = 1.0, opacity: float = 1.0, width: float = 1.6) -> None:
        """Wobbled circle outline."""
        pts = [(cx + r * math.cos(t), cy + r * math.sin(t))
               for t in [i * math.pi / 24 for i in range(25)]]
        pts = _jitter(pts, amp, self.rng)
        d = _smooth_d(pts) + " Z"
        self._emit(
            f'<path d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'opacity="{opacity}"/>'
        )

    def ellipse(self, cx: float, cy: float, rx: float, ry: float,
                rot_deg: float = 0.0, width: float = 1.6, color: str = INK,
                amp: float = 1.0, opacity: float = 1.0,
                dash: str | None = None) -> str:
        """Wobbled rotated-ellipse outline. Returns the path `d` (handy
        as a clip path for hatching the form it bounds)."""
        rot = math.radians(rot_deg)
        pts = []
        for i in range(49):
            t = 2 * math.pi * i / 48
            ex, ey = rx * math.cos(t), ry * math.sin(t)
            pts.append((cx + ex * math.cos(rot) - ey * math.sin(rot),
                        cy + ex * math.sin(rot) + ey * math.cos(rot)))
        pts = _jitter(pts, amp, self.rng)
        d = _smooth_d(pts) + " Z"
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self._emit(
            f'<path d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'opacity="{opacity}"{dash_attr}/>'
        )
        return d

    def blind_path(self, outline, width: float = 2.0, color: str = INK,
                   lag_base: float = 7.0, lag_wander: float = 5.0,
                   tremor: float = 1.1, drift: float = 2.6,
                   overshoot: float = 16.0, corner_deg: float = 38.0,
                   hesitate: int = 3, hesitate_len: int = 16,
                   seed: int | None = None) -> list[tuple[float, float]]:
        """Blind-contour pass: the hand follows the eye's path with lag.

        `outline` is the intended contour (the eye's path), an ordered,
        reasonably dense polyline. The drawn hand position is
        ``outline[i - lag_i]``: the eye moves ahead while the hand lags,
        and the lag wanders slowly (sometimes the hand almost catches up,
        sometimes it falls far behind — so corners get rounded and detail
        gets lost, exactly like the real exercise).

        Sharp corners produce overshoot hooks: the hand keeps going past
        the corner along the incoming direction, then hooks back — the
        signature blind-contour tell. A few seeded hesitation spots leave
        dense tremor clusters where the eye lingered. Deterministic for a
        given seed (defaults to the pen's seed stream).
        Returns a list of (x, y, walk_i) triples: the drawn points plus the
        walk index of the eye's path each drawn point belongs to, so a
        study can diagram the lag (rubber bands between eye and hand).
        """
        pts = [(float(x), float(y)) for x, y in outline]
        n = len(pts)
        if n < 8:
            return []
        rng = mulberry(self.rng.randrange(1 << 30) if seed is None else seed)

        # -- locate sharp corners in the eye's path --------------------
        def turn_at(i: int) -> float:
            x0, y0 = pts[max(0, i - 2)]
            x1, y1 = pts[i]
            x2, y2 = pts[min(n - 1, i + 2)]
            ax, ay = x1 - x0, y1 - y0
            bx, by = x2 - x1, y2 - y1
            la, lb = math.hypot(ax, ay), math.hypot(bx, by)
            if la < 1e-6 or lb < 1e-6:
                return 0.0
            cos_a = max(-1.0, min(1.0, (ax * bx + ay * by) / (la * lb)))
            return math.degrees(math.acos(cos_a))

        corners = [i for i in range(3, n - 3) if turn_at(i) > corner_deg]
        # keep corners apart so hooks don't pile up
        kept: list[int] = []
        for c in corners:
            if not kept or c - kept[-1] > 14:
                kept.append(c)
        corners = kept

        # -- slow wander phases for lag, drift, and the eye's own path --
        p1, p2 = rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)
        q1, q2 = rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)

        def sample(idx: float) -> tuple[float, float]:
            i0 = max(0, min(n - 2, int(math.floor(idx))))
            f = max(0.0, min(1.0, idx - i0))
            x0, y0 = pts[i0]
            x1, y1 = pts[i0 + 1]
            return (x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)

        # hesitation spots, chosen up front on walk indices away from corners
        hspots: set[int] = set()
        for _ in range(hesitate):
            for _try in range(20):
                h = rng.randrange(n // 8, 7 * n // 8)
                if not any(abs(h - c) < 20 for c in corners):
                    hspots.add(h)
                    break

        drawn: list[tuple[float, float, int]] = []
        crossed: set[int] = set()
        for i in range(n):
            t = i / n
            lag = lag_base + lag_wander * (
                0.6 * math.sin(2 * math.pi * t * 1.5 + p1)
                + 0.4 * math.sin(2 * math.pi * t * 3.0 + p2))
            lag = max(1.5, lag)
            j = max(0.0, i - lag)
            x, y = sample(j)
            # tremor (fast) + drift (slow, the "feeling the edge" wobble)
            x += rng.uniform(-tremor, tremor) + drift * math.sin(
                2 * math.pi * t * 2.0 + q1)
            y += rng.uniform(-tremor, tremor) + drift * 0.7 * math.sin(
                2 * math.pi * t * 2.7 + q2)
            drawn.append((x, y, i))
            # hesitation: the eye lingers, the hand trembles in place
            if i in hspots:
                for _h in range(hesitate_len):
                    drawn.append((x + rng.uniform(-tremor * 1.8, tremor * 1.8),
                                  y + rng.uniform(-tremor * 1.8, tremor * 1.8), i))

            # corner overshoot: when the hand crosses a corner, keep going
            # along the incoming direction, then hook back.
            for c in corners:
                if c in crossed:
                    continue
                if j >= c - 0.5:
                    crossed.add(c)
                    cx, cy, _ = drawn[-1]
                    px, py = pts[c]
                    # incoming direction at the corner (eye's path)
                    ax, ay = pts[c][0] - pts[c - 3][0], pts[c][1] - pts[c - 3][1]
                    la = math.hypot(ax, ay) or 1.0
                    ax, ay = ax / la, ay / la
                    turn = turn_at(c)
                    hook = overshoot * (0.5 + turn / 90.0)
                    steps = 7
                    for s in range(1, steps + 1):
                        f = s / steps
                        drawn.append((cx + ax * hook * f,
                                      cy + ay * hook * f, i))
                    # hook back toward where the eye's path went
                    tx, ty = sample(c + 2)
                    for s in range(1, steps + 1):
                        f = s / steps
                        ease = f * f * (3 - 2 * f)
                        drawn.append((cx + ax * hook * (1 - ease) + (tx - cx - ax * hook) * ease,
                                      cy + ay * hook * (1 - ease) + (ty - cy - ay * hook) * ease, i))

        d = _smooth_d([(x, y) for x, y, _ in drawn])
        self._emit(
            f'<path d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>'
        )
        return drawn

    def label(self, x: float, y: float, text: str, size: int = 14,
              italic: bool = True, opacity: float = 0.65,
              anchor: str = "start") -> None:
        """Small typeset caption — for plate titles and panel notes."""
        style = "font-style:italic;" if italic else ""
        self._emit(
            f'<text x="{x:.1f}" y="{y:.1f}" '
            f'font-family="Georgia, \'Times New Roman\', serif" '
            f'font-size="{size}" fill="{INK}" opacity="{opacity}" '
            f'text-anchor="{anchor}" style="{style}">{text}</text>'
        )

    def closed_d(self, pts, amp: float = 1.0) -> str:
        """Wobbled closed path `d` through `pts`.

        Handy for building hatch clip holes: the same jitter/smoothing
        as a drawn stroke, so a punched hole and its hand-drawn edge
        line agree to within a pixel or two."""
        pts = _jitter(pts, amp, self.rng)
        return _smooth_d(pts) + " Z"

    def neg_hatch(self, x0: float, y0: float, x1: float, y1: float,
                  holes: list[str], angle_deg: float, spacing: float,
                  width: float = 1.0, color: str = INK,
                  opacity: float = 0.55, edge_amp: float = 2.2) -> None:
        """Hatch the field (x0,y0)-(x1,y1), leaving `holes` as paper.

        The negative-space trick: the field boundary and every hole are
        joined into ONE clip path with clip-rule="evenodd", so the holes
        punch cleanly through the hatching — draw the ground, not the
        figure. The field edge itself is wobbled (edge_amp) so the toned
        area reads as a hand-drawn boundary, not a vector rectangle.
        `holes` are closed path `d` strings (see `closed_d`).
        """
        self._clip_n += 1
        cid = f"clip{self._clip_n}"
        edge = _smooth_d(_jitter(
            [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], edge_amp, self.rng)
        ) + " Z"
        d = edge + " " + " ".join(holes)
        self.defs.append(
            f'<clipPath id="{cid}"><path d="{d}" '
            f'clip-rule="evenodd"/></clipPath>')
        ang = math.radians(angle_deg)
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        cx0, cy0 = (x0 + x1) / 2, (y0 + y1) / 2
        diag = math.hypot(x1 - x0, y1 - y0)
        lines = []
        off = -diag
        while off < diag:
            cx, cy = cx0 + nx * off, cy0 + ny * off
            xa, ya = cx - dx * diag, cy - dy * diag
            xb, yb = cx + dx * diag, cy + dy * diag
            # wobble the endpoints so hatches don't look ruled
            j = lambda v: v + self.rng.uniform(-1.2, 1.2)
            lines.append(
                f'<line x1="{j(xa):.1f}" y1="{j(ya):.1f}" '
                f'x2="{j(xb):.1f}" y2="{j(yb):.1f}" '
                f'stroke="{color}" stroke-width="{width}"/>'
            )
            off += spacing
        self._emit(
            f'<g clip-path="url(#{cid})" opacity="{opacity}">'
            + "".join(lines) + "</g>"
        )

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

    def edge_life(self, pts, presence, width: float = 2.0, color: str = INK,
                  amp: float = 1.4, chunk: int = 5) -> None:
        """Lost-and-found contour: the pen's ink fades in and out along
        `pts` according to `presence` — a list of 0..1 values, one per
        point, or a callable mapping t in 0..1 to a 0..1 presence.

        Each short chunk of the path gets width and opacity scaled by its
        presence: high presence = found edge (bold, full ink), low
        presence = lost edge (hairline, ghosted), near-zero = nothing
        drawn — the eye closes the gap. Overlapping chunks with round
        caps keep neighboring sections merging like wet ink.
        Deterministic for a given seed.
        """
        pts = [(float(x), float(y)) for x, y in pts]
        n = len(pts)
        if n < 2:
            return
        if callable(presence):
            pres = [max(0.0, min(1.0, float(presence(i / max(1, n - 1)))))
                    for i in range(n)]
        else:
            pres = [max(0.0, min(1.0, float(p))) for p in presence]
            if len(pres) < n:
                pres = pres + [pres[-1]] * (n - len(pres))
        runs = []
        run = []
        for i in range(n):
            if pres[i] > 0.06:
                run.append(i)
            elif run:
                runs.append(run)
                run = []
        if run:
            runs.append(run)
        for run in runs:
            if len(run) < 2:
                continue
            j = 0
            while j < len(run) - 1:
                k = min(j + chunk, len(run) - 1)
                idx = run[j:k + 1]
                p = sum(pres[i] for i in idx) / len(idx)
                seg = [pts[i] for i in idx]
                # extend each chunk by one neighbor point so the curve
                # keeps its direction across chunk boundaries
                if j > 0:
                    seg = [pts[run[j - 1]]] + seg
                if k < len(run) - 1:
                    seg = seg + [pts[run[k + 1]]]
                w = width * (0.45 + 0.75 * p)
                self.stroke(seg, width=w, color=color, amp=amp,
                            opacity=min(1.0, 0.25 + 0.95 * p))
                j = k

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
