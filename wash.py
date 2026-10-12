"""wash.py — a tiny watercolor engine for the sketchbook series.

Paint, not pen: translucent pigment layers, graduated washes, edge
pooling (pigment settling at a wash's wet edge), wet-in-wet blooms
(cauliflower-edged diffusion), granulation (pigment settling into paper
tooth), and lifting (scrubbing back to paper). Emits SVG fragments; the
study script composes the plate. Everything is seeded, like the pen
engine — same seed, same painting.

Honesty note: real watercolor is per-pixel fluid dynamics. This engine
fakes the *visible* behaviours with layered translucent shapes and
precomputed glazing math, and says so.
"""

from pen import mulberry, _smooth_d

PAPER = (245, 240, 228)


# ---------------------------------------------------------------- color math

def rgb(hexstr):
    """'#rrggbb' -> (r, g, b) floats 0..255."""
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hex_(c):
    """(r, g, b) -> '#rrggbb'."""
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in c)


def mix(a, b, t):
    """Linear interpolate between two colors; t=0 -> a, t=1 -> b."""
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def shade(c, f):
    """Multiply a color by f (f<1 darkens, f>1 lightens toward white-ish)."""
    return tuple(v * f for v in c)


def glaze(base, pigment, alpha):
    """Composite translucent pigment over base with multiply blending.

    Real glazing multiplies: light passes through the pigment layer,
    bounces off the paper, and passes through again. We approximate the
    pigment-on-pigment interaction as base*pigment, then alpha-blend that
    over the base.
    """
    p = tuple(b / 255.0 * q / 255.0 * 255.0 for b, q in zip(base, pigment))
    return tuple(b + (pp - b) * alpha for b, pp in zip(base, p))


def gradient_fn(stops):
    """stops: [(t, color), ...] sorted by t. Returns f(t) -> color."""
    def f(t):
        t = max(stops[0][0], min(stops[-1][0], t))
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                return mix(c0, c1, k)
        return stops[-1][1]
    return f


# ------------------------------------------------------------ path builders

def wobble_closed(cx, cy, rx, ry, rng, wob=0.16, n=16, rot=0.0):
    """Wobbled ellipse -> closed smooth path (irregular organic blob)."""
    import math
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rot
        k = 1.0 + rng.uniform(-wob, wob)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    pts.append(pts[0])  # close the loop so the smoothing wraps around
    return _smooth_d(pts) + " Z"


def wobble_line(pts, rng, amp=3.0):
    """Jitter a polyline and smooth it (ridgelines, horizons, strokes)."""
    j = [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp))
         for x, y in pts]
    return _smooth_d(j)


# ---------------------------------------------------------- wash fragments

def graduated_wash(gid, x, y, w, h, stops, vertical=True):
    """A wash that grades from one color to another: <defs> gradient + rect.

    stops: [(t, hexcolor), ...]. Returns (defs_str, rect_str).
    """
    x1, y1, x2, y2 = ("0", "0", "0", "1") if vertical else ("0", "0", "1", "0")
    s = "".join(
        '      <stop offset="%.3f" stop-color="%s"/>' % (t, c)
        for t, c in stops)
    defs = (
        '    <linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">\n%s\n'
        '    </linearGradient>' % (gid, x1, y1, x2, y2, s))
    rect = ('    <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
            'fill="url(#%s)"/>' % (x, y, w, h, gid))
    return defs, rect


def edge_pool(path_d, clip_id, color, width=12, opacity=0.30, blur=3):
    """Pigment settling darker along a wash's wet edge.

    A blurred stroke centered on the edge, clipped to the wash so only
    the inner half shows: the classic dark tide-line of a drying wash.
    """
    return (
        '    <g clip-path="url(#%s)">\n'
        '      <path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
        'opacity="%.2f" filter="url(#soft%d)"/>\n'
        '    </g>' % (clip_id, path_d, color, width, opacity, blur))


def bloom(cx, cy, rx, ry, pigment, rng, seed_note=""):
    """A wet-in-wet bloom: pigment dropped into a still-wet wash.

    Layered shrinking wobbled blobs fake the diffusion: a pale wide halo
    with a darker irregular core, plus a shadow-side crescent. Cauliflower
    edges come from the wobble, not a filter, so it rasterizes anywhere.
    """
    light, dark = mix(pigment, PAPER, 0.55), shade(pigment, 0.62)
    layers = [(1.00, light, 0.10), (0.76, pigment, 0.13),
              (0.54, pigment, 0.16), (0.34, dark, 0.18)]
    out = ['    <g class="bloom"%s>' %
           ("" if not seed_note else ' data-note="%s"' % seed_note)]
    dx = dy = 0.0
    for i, (s, col, op) in enumerate(layers):
        # cores drift toward the shadow side (down, away from the sun)
        dx += rng.uniform(-0.06, 0.02) * rx
        dy += rng.uniform(0.02, 0.10) * ry
        d = wobble_closed(cx + dx, cy + dy, rx * s, ry * s, rng,
                          wob=0.22, n=18, rot=rng.uniform(0, 6.28))
        out.append('      <path d="%s" fill="%s" opacity="%.2f"/>'
                   % (d, hex_(col), op))
    # shadow crescent on the lower far side
    d = wobble_closed(cx - rx * 0.18, cy + ry * 0.42, rx * 0.42, ry * 0.30,
                      rng, wob=0.25, n=14)
    out.append('      <path d="%s" fill="%s" opacity="0.16"/>' % (d, hex_(dark)))
    out.append('    </g>')
    return "\n".join(out)


def granulation(clip_id, x0, y0, x1, y1, pigment, rng, n=350,
                rmax=2.2, omin=0.08, omax=0.20, density_fn=None):
    """Pigment settling into the paper tooth: seeded darker speckles.

    density_fn(x, y) -> 0..1 scales local speckle probability, so
    granulation can gather in the shadows.
    """
    dark = hex_(shade(pigment, 0.5))
    out = ['    <g clip-path="url(#%s)" class="granulation">' % clip_id]
    placed = 0
    guard = 0
    while placed < n and guard < n * 20:
        guard += 1
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        if density_fn and rng.random() > density_fn(x, y):
            continue
        r = rng.uniform(0.7, rmax)
        op = rng.uniform(omin, omax)
        out.append('      <circle cx="%.1f" cy="%.1f" r="%.2f" fill="%s" '
                   'opacity="%.2f"/>' % (x, y, r, dark, op))
        placed += 1
    out.append('    </g>')
    return "\n".join(out)


def paper_grain(x0, y0, x1, y1, rng, n=1300):
    """Faint paper tooth over the whole plate."""
    out = ['    <g class="grain">']
    for _ in range(n):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        light = rng.random() < 0.5
        col = "#fffdf6" if light else "#e0d3b6"
        r = rng.uniform(0.6, 1.6)
        out.append('      <circle cx="%.1f" cy="%.1f" r="%.2f" fill="%s" '
                   'opacity="%.2f"/>' % (x, y, r, col, rng.uniform(0.04, 0.09)))
    out.append('    </g>')
    return "\n".join(out)


def soft_filters():
    """Blur filters used by edge_pool (cairosvg-safe: feGaussianBlur)."""
    return """    <filter id="soft2" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2"/>
    </filter>
    <filter id="soft3" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
    <filter id="soft4" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
    <filter id="soft6" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>"""
