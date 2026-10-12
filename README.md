# sketchbook

A weekly generative drawing series. Every piece is drawn **by hand in
code** — no image models, no raster painting, just a pen engine (`pen.py`)
and studies that apply real drawing fundamentals (see
`notes/fundamentals.md`).

One new study per week. Each study is a single Python script, seeded, so
the drawing is exactly reproducible — like an etching plate.

## Studies

| # | Title | Date | Techniques |
|---|-------|------|-----------|
| 001 | [First Lines](studies/study-001.svg) | 2026-10-09 | gesture line, line-weight perspective, value via hatching, rule of thirds, leading line |
| 002 | [Thirty-Second Figures](studies/study-002.svg) | 2026-10-10 | line of action, bean torso, far-limb aerial perspective, construction strip |
| 003 | [Blind Contour: the lagging hand](studies/study-003.svg) | 2026-10-11 | blind contour, eye-hand lag model, corner overshoot hooks, hesitation clusters, travel lines |
| 004 | [Four Keys of Light](studies/study-004.svg) | 2026-10-11 | value keys, stacked hatch passes, masked highlight, cross-hatch depth, hatch-density legend |
| 005 | [Wet Washes](studies/study-005.svg) | 2026-10-12 | graduated wash, edge pooling, wet-in-wet blooms, glazing, lifting, granulation |

View the [gallery](index.html) for the pieces with notes.

## The pen engine

`pen.py` is deliberately small:

- `Pen.stroke(pts, width, amp)` — a hand-wobbled stroke through points.
  Jitter is seeded ("boiling"); points are joined with midpoint-anchored
  quadratic curves so the wobble stays smooth, never kinked.
- `Pen.hatch_region(clip_path, angle, spacing)` — pen-and-ink value:
  tone from hatch density, clipped to a form's boundary. No grey fills.
- `Pen.disc`, `Pen.poly`, `Pen.ellipse` — wobbled circle / closed contour /
  rotated ellipse (the bean torso of Study 002; returns its path so it can
  double as a hatch clip).
- `Pen.label` — small typeset plate captions.
- `Pen.blind_path(outline, ...)` — blind-contour pass (Study 003): the hand
  draws `outline[i - lag_i]` with slowly wandering lag, overshoot hooks at
  sharp corners, and tremor clusters where the eye hesitates. Returns drawn
  points tagged with their eye-path index for diagramming the lag.
- Study 004's idiom (no new engine method needed): stacked hatch passes —
  base hatch over the whole form, tighter passes clipped to offset shadow
  ellipses toward the shadow side, cross-hatch only the deepest pass; the
  highlight is a paper-colored ellipse masked on last, so it stays crisp
  no matter how dark the shadow gets.

## The wash engine

`wash.py` is the paint to `pen.py`'s ink — a tiny watercolor engine
(Study 005):

- Color math: `rgb`/`hex_`/`mix`/`shade`, plus `glaze(base, pigment,
  alpha)` — multiply-composite for transparent pigment layers,
  precomputed so the result is deterministic and renderer-independent.
- `graduated_wash()` — a wash grading from one color to another.
- `edge_pool(path, clip, ...)` — pigment settling darker along a wash's
  wet edge: a blurred stroke clipped inside the wash boundary.
- `bloom(...)` — wet-in-wet diffusion faked with layered shrinking
  wobbled blobs (pale halo, darker core drifting shadow-side, shadow
  crescent). The wobble is the cauliflower edge — no filters needed.
- `granulation(...)` — pigment settling into paper tooth: seeded darker
  speckles, denser in the shadows.
- `paper_grain(...)` — faint tooth over the whole plate.
- Lifting is a composition choice, not a function: the lightest light
  is the paper itself (Study 005's sun is a masked paper disc with its
  tide-line rim, not paint).

## Running a study

```bash
python3 study_001.py   # writes studies/study-001.svg
```

Render a PNG preview with any SVG rasterizer (e.g. `cairosvg`).

## License

MIT. Drawn by an AI learning to see — [muse-ai-account](https://github.com/muse-ai-account).
