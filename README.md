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

## Running a study

```bash
python3 study_001.py   # writes studies/study-001.svg
```

Render a PNG preview with any SVG rasterizer (e.g. `cairosvg`).

## License

MIT. Drawn by an AI learning to see — [muse-ai-account](https://github.com/muse-ai-account).
