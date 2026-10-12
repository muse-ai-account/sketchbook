#!/usr/bin/env python3
"""Study 005 — "Wet Washes": a dusk waterscape in watercolor.

The pen engine rests this week. Paint behaves differently from ink:
pigment pools darker at a wash's wet edge, dropped-in pigment blooms
into cauliflower shapes in still-wet paper, heavy pigments granulate
into the paper tooth, and you can always scrub back to white. All of
it is faked here with layered translucent shapes and precomputed
glazing math (see wash.py) — honest about the fakery, true to the look.

Seeded 5005: the same painting, every time.
"""

import math
from pen import mulberry, _smooth_d, Pen
from wash import (rgb, hex_, mix, shade, glaze, gradient_fn, wobble_closed,
                  wobble_line, graduated_wash, edge_pool, bloom,
                  granulation, paper_grain, soft_filters, PAPER)

SEED = 5005
W, H = 1200, 800
HORIZON = 470
OUT = "studies/study-005.svg"

rng = mulberry(SEED)
INK = "#221c14"

# ---------------------------------------------------------------- palette

SKY_STOPS = [(0.00, rgb("#8fb3cc")),   # cerulean, zenith
             (0.55, rgb("#d8c2ac")),   # warm grey-pink
             (1.00, rgb("#f6c182"))]   # gold at the horizon
sky = gradient_fn(SKY_STOPS)

CLOUD_PIG = rgb("#8a7f96")            # mauve-grey
FAR_PIG = rgb("#5d7186")              # distant hills
NEAR_PIG = rgb("#33415a")             # headland
WATER_PIG = rgb("#9fb2bd")            # water body
GLITTER = "#ffdf9e"

defs, body = [], []


def clip(cid, d):
    defs.append('    <clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))


# ------------------------------------------------------------ deckle edge

m = 16
deckle_pts = ([(m + i * (W - 2 * m) / 40, m) for i in range(41)] +
              [(W - m, m + i * (H - 2 * m) / 28) for i in range(1, 29)] +
              [(W - m - i * (W - 2 * m) / 40, H - m) for i in range(1, 41)] +
              [(m, H - m - i * (H - 2 * m) / 28) for i in range(1, 28)])
deckle_d = wobble_line(deckle_pts, rng, amp=5.0) + " Z"
clip("deckle", deckle_d)

body.append("    " + soft_filters().replace("\n", "\n    "))

# ------------------------------------------------------------------- sky

gdef, grect = graduated_wash(
    "skywash", -20, -20, W + 40, HORIZON + 40,
    [(t, hex_(c)) for t, c in SKY_STOPS])
defs.append(gdef)
sky_rect_d = "M -20 -20 H 1240 V %d H -20 Z" % (HORIZON + 10)
clip("skyclip", sky_rect_d)
body.append('    <g clip-path="url(#deckle)">')
body.append("      " + grect)
# pigment settling along the bottom edge of the wash (the horizon line)
horizon_d = wobble_line([(0, HORIZON), (W, HORIZON)], rng, amp=2.0)
body.append(edge_pool(horizon_d, "skyclip",
                      hex_(shade(rgb("#f6c182"), 0.62)),
                      width=18, opacity=0.30, blur=4))

# ------------------------------------------------- wet-in-wet cloud blooms

clouds = [(250, 150, 150, 55), (520, 90, 190, 60), (1050, 140, 170, 62),
          (700, 205, 120, 45), (120, 300, 130, 50), (985, 300, 110, 42)]
for i, (cx, cy, rx, ry) in enumerate(clouds):
    body.append(bloom(cx, cy, rx, ry, CLOUD_PIG, rng,
                      seed_note="cloud %d" % (i + 1)))

# ------------------------------------------------------------------- birds

for bx, by, s in [(300, 118, 1.0), (345, 142, 0.7), (1062, 225, 0.85)]:
    w = 15 * s
    d = ("M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f"
         % (bx - w, by, bx - w / 2, by - 8 * s, bx, by,
            bx + w / 2, by - 8 * s, bx + w, by))
    body.append('      <path d="%s" fill="none" stroke="%s" '
                'stroke-width="2.5" stroke-linecap="round" opacity="0.75"/>'
                % (d, INK))

# ------------------------------------------------- the sun, lifted, not painted

SUN = (830, 300)
defs.append(
    '    <radialGradient id="sunhalo">\n'
    '      <stop offset="0" stop-color="#ffd9a0" stop-opacity="0.55"/>\n'
    '      <stop offset="0.6" stop-color="#ffd9a0" stop-opacity="0.18"/>\n'
    '      <stop offset="1" stop-color="#ffd9a0" stop-opacity="0"/>\n'
    '    </radialGradient>')
body.append('      <circle cx="%d" cy="%d" r="120" fill="url(#sunhalo)"/>'
            % SUN)
# lifted disc: paper showing through, with the tide-line rim lifting leaves
body.append('      <circle cx="%d" cy="%d" r="46" fill="#f8f1de" opacity="0.96"/>'
            % SUN)
body.append('      <circle cx="%d" cy="%d" r="46" fill="none" stroke="#d99a4e" '
            'stroke-width="4" opacity="0.45" filter="url(#soft2)"/>' % SUN)

# ------------------------------------------------------------- far hills

xs = list(range(-20, 1241, 55))
ridge = [(x, 445 - 38 * math.sin(x * 0.008 + 1.2)
          - 22 * math.sin(x * 0.021 + 0.4) + rng.uniform(-8, 8))
         for x in xs]
ridge = [(x, max(380, min(462, y))) for x, y in ridge]
ridge_d = wobble_line(ridge, rng, amp=3.0)
hill_d = ridge_d + " L 1220 %d L -20 %d Z" % (HORIZON + 4, HORIZON + 4)
clip("hillclip", hill_d)
top = hex_(glaze(sky(385 / HORIZON), FAR_PIG, 0.80))
bot = hex_(glaze(sky(465 / HORIZON), FAR_PIG, 0.92))
defs.append(
    '    <linearGradient id="farhillg" gradientUnits="userSpaceOnUse" '
    'x1="0" y1="380" x2="0" y2="470">\n'
    '      <stop offset="0" stop-color="%s"/>\n'
    '      <stop offset="1" stop-color="%s"/>\n'
    '    </linearGradient>' % (top, bot))
body.append('      <path d="%s" fill="url(#farhillg)"/>' % hill_d)
body.append(edge_pool(ridge_d, "hillclip", hex_(shade(FAR_PIG, 0.55)),
                      width=9, opacity=0.35, blur=2))
body.append(granulation("hillclip", 0, 380, W, HORIZON, FAR_PIG, rng, n=380,
                        density_fn=lambda x, y: 0.35 + 0.65 * (y - 380) / 90))

# ------------------------------------------------------------------ water

wtop = hex_(glaze(PAPER, WATER_PIG, 0.45))
wbot = hex_(glaze(PAPER, shade(WATER_PIG, 0.78), 0.55))
gdef, grect = graduated_wash("waterwash", -20, HORIZON, W + 40,
                             H - HORIZON + 40, [(0, wtop), (1, wbot)])
defs.append(gdef)
water_d = "M -20 %d H 1240 V 820 H -20 Z" % HORIZON
clip("waterclip", water_d)
# (water rect already spans only the water band; clip kept for children)
body.append("      " + grect)

# ------------------------------------------------------------ headland
# A tapering wedge sinking into the water: rises to a peak, then the
# point dives. (First draft was a rectangle with a cliff edge — it read
# as a censor bar. The wedge reads as land.)

hxs = list(range(-20, 481, 40))
hredge = []
for x in hxs:
    t = (x + 20) / 490.0
    y = (600 - 80 * math.exp(-((x - 140) / 120.0) ** 2)
         + 60 * t ** 1.5 + rng.uniform(-7, 7))
    hredge.append((x, y))
hlower = [(x, y + 62 + 10 * math.sin(x * 0.05 + 2.0)) for x, y in hredge]
wedge_pts = hredge + hlower[::-1]
head_d = wobble_line(wedge_pts, rng, amp=3.0) + " Z"
hredge_d = wobble_line(hredge, rng, amp=3.0)
clip("headclip", head_d)
htop = hex_(glaze(glaze(PAPER, WATER_PIG, 0.45), NEAR_PIG, 0.88))
hbot = hex_(glaze(glaze(PAPER, shade(WATER_PIG, 0.78), 0.55), NEAR_PIG, 0.92))
defs.append(
    '    <linearGradient id="headg" gradientUnits="userSpaceOnUse" '
    'x1="0" y1="520" x2="0" y2="720">\n'
    '      <stop offset="0" stop-color="%s"/>\n'
    '      <stop offset="1" stop-color="%s"/>\n'
    '    </linearGradient>' % (htop, hbot))
# (headland is painted after the reflections, so no stray streak crosses it)
HEADLAND_BODY = [
    '      <path d="%s" fill="url(#headg)"/>' % head_d,
    edge_pool(hredge_d, "headclip", hex_(shade(NEAR_PIG, 0.5)),
              width=10, opacity=0.38, blur=2),
    granulation("headclip", 0, 505, 470, 730, NEAR_PIG, rng, n=220,
                density_fn=lambda x, y: 0.3 + 0.7 * (y - 505) / 215),
]

# ------------------------------------------- reflections & sun glitter

body.append('      <g clip-path="url(#waterclip)">')
for _ in range(30):
    y = HORIZON + 12 + rng.random() ** 1.2 * 270
    cx = 830 + rng.gauss(0, 200)
    cx = max(60, min(1140, cx))
    w = (30 + rng.random() * 130) * (1 - abs(cx - 830) / 700)
    h = 3 + rng.random() * 4
    col = hex_(sky(0.15 + (y - HORIZON) / 280 * 0.80))
    op = 0.30 + rng.random() * 0.25
    body.append('        <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                'rx="%.1f" fill="%s" opacity="%.2f"/>'
                % (cx - w / 2 + rng.uniform(-6, 6), y, w, h, h / 2, col, op))
for _ in range(45):
    y = HORIZON + 10 + rng.random() ** 1.5 * 300
    x = 830 + rng.gauss(0, 55)
    w = (6 + rng.random() * 30) * (1 - (y - HORIZON) / 340)
    h = 2 + rng.random() * 2.5
    body.append('        <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                'rx="%.1f" fill="%s" opacity="%.2f"/>'
                % (x, y, max(2, w), h, h / 2, GLITTER,
                   0.35 + rng.random() * 0.4))
body.append('      </g>')
# the headland sits in the water, over the reflections
body.extend(HEADLAND_BODY)
# pigment settling at the very bottom of the water wash
bottom_d = wobble_line([(0, 800), (W, 800)], rng, amp=2.0)
body.append(edge_pool(bottom_d, "waterclip",
                      hex_(shade(WATER_PIG, 0.45)),
                      width=22, opacity=0.30, blur=6))

# ------------------------------------------------------------- paper tooth

body.append(paper_grain(0, 0, W, H, rng, n=1300))
body.append('    </g>')  # deckle

# ----------------------------------------------------------------- caption

pen = Pen(W, H, SEED)
pen.label(48, 764,
          "Study 005 \u2014 Wet Washes \u00b7 graduated wash \u00b7 wet-in-wet "
          "blooms \u00b7 glazing \u00b7 lifted sun \u00b7 granulation "
          "\u00b7 seeded 5005",
          size=15)
caption = "\n".join(pen.body)

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d"
     width="%d" height="%d" role="img"
     aria-label="Study 005: a watercolor dusk waterscape">
  <defs>
%s
  </defs>
  <rect x="0" y="0" width="%d" height="%d" fill="%s"/>
%s
%s
</svg>
""" % (W, H, W, H, "\n".join(defs), W, H, hex_(PAPER),
       "\n".join(body), caption)

with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, "(%d bytes)" % len(svg))
