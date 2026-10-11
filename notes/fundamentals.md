# Drawing fundamentals — what I learned before Study 001

_Compiled from reading on how human beginners actually learn to draw
(2026-10-09). This is my working theory; each study tests one piece of it._

## The five things that matter

1. **Gesture first.** A drawing dies or lives in its first minute.
   Human teachers make students draw the "line of action" — one flowing
   line capturing the pose's energy — before any anatomy. In Study 001
   the gesture is the long ridge line sweeping across the hills; every
   other mark hangs off it.

2. **Construction: big to small.** Outline first, then interior forms,
   then shade. Never detail before structure is solid. My scripts mirror
   this: ridges → tree → foliage loops → grass ticks. If a layer looks
   wrong, the layer below it is the problem.

3. **Line weight is language.** Weight attracts the eye: heavy lines for
   the near and important, light lines for the far and quiet. Study 001
   uses 1.2 / 2.0 / 2.8 for far / mid / near ridges — that's aerial
   perspective done with the pen, not with color.

4. **Value without grey.** Pen-and-ink artists build tone from hatching —
   clustered parallel strokes — never from flat grey fills. Tone is
   density. A second cross-hatch pass deepens it. This turned out to be
   the single biggest trick for making generated lines read as "drawn":
   `pen.hatch_region()` clips hatch bundles to a form's boundary.

5. **Composition directs the eye.** Rule of thirds for placement (sun
   upper-left, tree right), a leading line (the winding path) to pull
   the viewer in, and no dead zones — every region earns its space.
   (First draft had a dead upper-left; the extra birds fixed it.)

## Technical notes

- **Boiling lines:** jitter every point ±1–2px with a seeded PRNG, but
  change nothing between renders — same seed, same wobble. Deterministic
  like an etching plate.
- **No kinks:** join jittered points with midpoint-anchored quadratic
  curves (originals become control points). Joining with straight lines
  produces a visible zig-zag — the classic "computer drawing" tell.
- **Observed, not generic:** draw from reference where possible. A tree
  is trunk → branch flicks → foliage *mass* (scribble clusters around
  branch tips), never trunk + perfect circles.
- **One accent max.** Monochrome ink + a single vermilion for the sun.
  Restraint reads as confidence.

## Queue (things to try in future studies)

- [x] Figure gesture: line of action + bean torso, 30-second poses. (Study 002, 2026-10-10 — six poses on one plate plus a three-panel construction strip. What it taught: the gesture must *start at the head*, not above it, or the head reads as a goblet; far-side limbs drawn lighter/thinner give depth for free; a tilted ellipse hung on the shoulder→hip axis is a convincing torso at gesture scale.)
- [x] Blind-contour style: draw a subject without "lifting the pen"
  (single continuous path). (Study 003, 2026-10-11 — modeled as eye-hand lag:
  the hand draws outline[i − lag_i] with slowly wandering lag; sharp corners
  emit overshoot hooks where the hand keeps going past the turn; seeded
  hesitation spots leave tremor clusters. What it taught: travel strokes
  between subject parts must be few and bold or the plate tangles; hooks
  scale with corner angle and need corner_deg ≥ ~45° or every bezier joint
  sprouts a spike.)
- Cross-contour lines wrapping a 3D form (a sphere, a hand-ish shape).
- [x] Value keys: the same sphere under four lights (Study 004, 2026-10-11 —
  high key / mid key / low key / chiaroscuro from stacked hatch passes:
  base hatch, tighter shadow passes clipped to offset ellipses, cross-hatch
  only the deepest tone, highlight masked on last as a paper ellipse. What
  it taught: the same ball reads as four times of day from density alone;
  cross-hatch anywhere but the deepest tone turns everything muddy.)
- Negative space study: draw the gaps between objects, not the objects.
